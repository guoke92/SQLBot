import os.path
import threading
import time

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

    def _embed(self, texts: list[str]) -> list[list[float]]:
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

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        # Batch in chunks to avoid oversized requests
        batch_size = 32
        out: list[list[float]] = []
        for i in range(0, len(texts), batch_size):
            out.extend(self._embed(texts[i : i + batch_size]))
        return out

    def embed_query(self, text: str) -> list[float]:
        return self._embed([text])[0]


local_embedding_model = EmbeddingModelInfo(
    folder=settings.LOCAL_MODEL_PATH,
    name=os.path.join(
        settings.LOCAL_MODEL_PATH, "embedding", "shibing624_text2vec-base-chinese"
    ),
)

_lock = threading.Lock()
locks: dict[str, threading.Lock] = {}

_embedding_model: dict[str, Embeddings | None] = {}
_embedding_dimensions: dict[str, int] = {}
_dimension_lock = threading.Lock()
_failure_lock = threading.Lock()
_unavailable_until: dict[str, float] = {}
_EMBEDDING_FAILURE_COOLDOWN_SEC = 60.0
VECTOR_DIMENSION_PREDICATE = (
    "vector_dims(child.embedding) = :embedding_dimension"
)


def embedding_query_params(vector: list[float]) -> dict[str, object]:
    """Build the shared pgvector query parameters with an explicit dimension."""
    if not vector:
        raise ValueError("Embedding vector cannot be empty")
    return {
        "embedding_array": str(vector),
        "embedding_dimension": len(vector),
    }


def has_compatible_dimension(
    query_vector: list[float],
    stored_vector: list[float],
) -> bool:
    """Return whether a persisted vector belongs to the active embedding space."""
    return bool(
        query_vector
        and stored_vector
        and len(query_vector) == len(stored_vector)
    )


class EmbeddingModelCache:

    @staticmethod
    def _cache_key(key: str) -> str:
        return f"{settings.EMBEDDING_PROVIDER}:{key}"

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
        cache_key = EmbeddingModelCache._cache_key(key)
        model_instance = _embedding_model.get(cache_key)
        if model_instance is None:
            lock = EmbeddingModelCache._get_lock(cache_key)
            with lock:
                model_instance = _embedding_model.get(cache_key)
                if model_instance is None:
                    model_instance = EmbeddingModelCache._new_instance(config)
                    _embedding_model[cache_key] = model_instance
        return model_instance

    @staticmethod
    def embed_query(
        text: str,
        *,
        key: str = settings.DEFAULT_EMBEDDING_MODEL,
    ) -> list[float]:
        """Embed once through a process-wide short failure circuit.

        Recall callers intentionally degrade to lexical/catalog fallbacks when
        embeddings are unavailable. Without a shared gate, one failed provider
        produced the same remote 403 in terminology, table and example recall
        during every clarification round.
        """
        cache_key = EmbeddingModelCache._cache_key(key)
        now = time.monotonic()
        with _failure_lock:
            retry_at = _unavailable_until.get(cache_key, 0.0)
        if retry_at > now:
            raise RuntimeError("Embedding provider is temporarily unavailable")
        try:
            vector = EmbeddingModelCache.get_model(key).embed_query(text)
        except Exception:
            with _failure_lock:
                _unavailable_until[cache_key] = (
                    time.monotonic() + _EMBEDDING_FAILURE_COOLDOWN_SEC
                )
            raise
        with _failure_lock:
            _unavailable_until.pop(cache_key, None)
        return vector

    @staticmethod
    def get_dimension(key: str = settings.DEFAULT_EMBEDDING_MODEL) -> int:
        """Return and cache the active model dimension for persistence repair."""
        cache_key = EmbeddingModelCache._cache_key(key)
        dimension = _embedding_dimensions.get(cache_key)
        if dimension is not None:
            return dimension
        with _dimension_lock:
            dimension = _embedding_dimensions.get(cache_key)
            if dimension is None:
                vector = EmbeddingModelCache.embed_query(
                    "embedding dimension probe", key=key
                )
                if not vector:
                    raise ValueError("Embedding model returned an empty vector")
                dimension = len(vector)
                _embedding_dimensions[cache_key] = dimension
        return dimension
