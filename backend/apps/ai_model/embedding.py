import os.path
import threading
from typing import List, Optional

import httpx
from langchain_core.embeddings import Embeddings
from pydantic import BaseModel, Field

from common.core.config import settings
from common.utils.utils import SQLBotLogUtil

os.environ["TOKENIZERS_PARALLELISM"] = "false"


class EmbeddingModelInfo(BaseModel):
    folder: str
    name: str
    device: str = "cpu"


class OllamaOpenAIEmbeddings(BaseModel, Embeddings):
    """OpenAI-compatible embeddings client (Ollama /v1/embeddings)."""

    model: str = Field(default="jina-embed")
    base_url: str = Field(default="http://localhost:11434/v1")
    api_key: str = Field(default="ollama")
    timeout: float = Field(default=60.0)

    class Config:
        arbitrary_types_allowed = True

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _endpoint(self) -> str:
        return self.base_url.rstrip("/") + "/embeddings"

    def _embed(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        payload = {"model": self.model, "input": texts if len(texts) > 1 else texts[0]}
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(self._endpoint(), json=payload, headers=self._headers())
            resp.raise_for_status()
            data = resp.json()
        items = data.get("data") or []
        # OpenAI format: list of {index, embedding}
        items = sorted(items, key=lambda x: x.get("index", 0))
        vectors = [item["embedding"] for item in items]
        if len(vectors) != len(texts):
            # Some servers only accept single input; fall back one-by-one
            if len(texts) > 1 and len(vectors) == 1:
                return [self._embed([t])[0] for t in texts]
            raise RuntimeError(
                f"Embedding count mismatch: expected {len(texts)}, got {len(vectors)}"
            )
        return vectors

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        # Batch in chunks to avoid oversized requests
        batch_size = 32
        out: List[List[float]] = []
        for i in range(0, len(texts), batch_size):
            out.extend(self._embed(texts[i : i + batch_size]))
        return out

    def embed_query(self, text: str) -> List[float]:
        return self._embed([text])[0]


local_embedding_model = EmbeddingModelInfo(
    folder=settings.LOCAL_MODEL_PATH,
    name=os.path.join(
        settings.LOCAL_MODEL_PATH, "embedding", "shibing624_text2vec-base-chinese"
    ),
)

_lock = threading.Lock()
locks: dict[str, threading.Lock] = {}

_embedding_model: dict[str, Optional[Embeddings]] = {}


class EmbeddingModelCache:

    @staticmethod
    def _new_instance(config: EmbeddingModelInfo = local_embedding_model) -> Embeddings:
        provider = (settings.EMBEDDING_PROVIDER or "huggingface").lower().strip()
        if provider in ("ollama", "openai", "openai_compatible", "http"):
            base_url = settings.EMBEDDING_API_BASE or "http://localhost:11434/v1"
            model_name = settings.DEFAULT_EMBEDDING_MODEL or "jina-embed"
            api_key = settings.EMBEDDING_API_KEY or "ollama"
            SQLBotLogUtil.info(
                f"Using HTTP embedding provider={provider} model={model_name} base={base_url}"
            )
            return OllamaOpenAIEmbeddings(
                model=model_name,
                base_url=base_url,
                api_key=api_key,
            )

        # Default: local HuggingFace sentence-transformers
        from langchain_huggingface import HuggingFaceEmbeddings

        SQLBotLogUtil.info(
            f"Using HuggingFace embedding model={config.name} folder={config.folder}"
        )
        return HuggingFaceEmbeddings(
            model_name=config.name,
            cache_folder=config.folder,
            model_kwargs={"device": config.device},
            encode_kwargs={"normalize_embeddings": True},
        )

    @staticmethod
    def _get_lock(key: str = settings.DEFAULT_EMBEDDING_MODEL):
        lock = locks.get(key)
        if lock is None:
            with _lock:
                lock = locks.get(key)
                if lock is None:
                    lock = threading.Lock()
                    locks[key] = lock
        return lock

    @staticmethod
    def get_model(
        key: str = settings.DEFAULT_EMBEDDING_MODEL,
        config: EmbeddingModelInfo = local_embedding_model,
    ) -> Embeddings:
        # Include provider in cache key so .env switches take effect after restart
        cache_key = f"{settings.EMBEDDING_PROVIDER}:{key}"
        model_instance = _embedding_model.get(cache_key)
        if model_instance is None:
            lock = EmbeddingModelCache._get_lock(cache_key)
            with lock:
                model_instance = _embedding_model.get(cache_key)
                if model_instance is None:
                    model_instance = EmbeddingModelCache._new_instance(config)
                    _embedding_model[cache_key] = model_instance
        return model_instance
