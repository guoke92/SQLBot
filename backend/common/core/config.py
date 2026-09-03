import secrets
import urllib.parse
from pathlib import Path
from typing import Annotated, Any, Literal

from pydantic import (
    AnyUrl,
    BeforeValidator,
    PostgresDsn,
    computed_field,
    field_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

from common.core.branding import APP_DISPLAY_NAME

# .env 固定在仓库根（backend/ 上一级）——相对 cwd 解析会让从其它目录
# 启动的脚本（提取管线/评测）拿到 /opt/sqlbot 类部署默认值。
_REPO_ROOT = Path(__file__).resolve().parents[3]
_ENV_FILE = _REPO_ROOT / ".env"


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Use top level .env file (one level above ./backend/)
        env_file=str(_ENV_FILE),
        env_ignore_empty=True,
        extra="ignore",
    )
    PROJECT_NAME: str = APP_DISPLAY_NAME
    # CONTEXT_PATH: str = "/sqlbot"
    CONTEXT_PATH: str = ""
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    FRONTEND_HOST: str = "http://localhost:5173"

    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = []

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [
            self.FRONTEND_HOST
        ]

    @computed_field  # type: ignore[prop-decorator]
    @property
    def API_V1_STR(self) -> str:
        return self.CONTEXT_PATH + "/api/v1"

    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "root"
    POSTGRES_PASSWORD: str = "Password123@pg"
    POSTGRES_DB: str = "sqlbot"
    SQLBOT_DB_URL: str = ""
    # SQLBOT_DB_URL: str = 'mysql+pymysql://root:Password123%40mysql@127.0.0.1:3306/sqlbot'

    TOKEN_KEY: str = "X-SQLBOT-TOKEN"
    DEFAULT_PWD: str = "Lls@123456"
    ASSISTANT_TOKEN_KEY: str = "X-SQLBOT-ASSISTANT-TOKEN"

    CACHE_TYPE: Literal["redis", "memory", "None"] = "memory"
    CACHE_REDIS_URL: str | None = (
        None  # Redis URL, e.g., "redis://[[username]:[password]]@localhost:6379/0"
    )

    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR
    LOG_DIR: str = "logs"
    LOG_PATTERN: str = "%(asctime)s - %(name)s - %(levelname)s:%(lineno)d - %(message)s"
    SQL_DEBUG: bool = False
    BASE_DIR: str = "/opt/sqlbot"
    SCRIPT_DIR: str = f"{BASE_DIR}/scripts"
    UPLOAD_DIR: str = "/opt/sqlbot/data/file"
    SQLBOT_KEY_EXPIRED: int = (
        100  # License key expiration timestamp, 0 means no expiration
    )

    SQLBOT_DOC_ENABLED: bool = True

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn | str:
        if self.SQLBOT_DB_URL:
            return self.SQLBOT_DB_URL
        # return MultiHostUrl.build(
        #     scheme="postgresql+psycopg",
        #     username=urllib.parse.quote(self.POSTGRES_USER),
        #     password=urllib.parse.quote(self.POSTGRES_PASSWORD),
        #     host=self.POSTGRES_SERVER,
        #     port=self.POSTGRES_PORT,
        #     path=self.POSTGRES_DB,
        # )
        return f"postgresql+psycopg://{urllib.parse.quote(self.POSTGRES_USER)}:{urllib.parse.quote(self.POSTGRES_PASSWORD)}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    MCP_IMAGE_PATH: str = "/opt/sqlbot/images"
    EXCEL_PATH: str = "/opt/sqlbot/data/excel"
    MCP_IMAGE_HOST: str = "http://localhost:3000"
    SERVER_IMAGE_HOST: str = "http://YOUR_SERVE_IP:MCP_PORT/images/"
    SERVER_IMAGE_TIMEOUT: int = 15

    LOCAL_MODEL_PATH: str = "/opt/sqlbot/models"
    DEFAULT_EMBEDDING_MODEL: str = "shibing624/text2vec-base-chinese"
    # Embedding provider: "huggingface" (local sentence-transformers) or
    # "ollama"/"openai"/"http" (OpenAI-compatible /v1/embeddings, e.g. Ollama).
    EMBEDDING_PROVIDER: str = "huggingface"
    EMBEDDING_API_BASE: str = "http://localhost:11434/v1"
    EMBEDDING_API_KEY: str = "ollama"
    EMBEDDING_ENABLED: bool = True
    EMBEDDING_DEFAULT_SIMILARITY: float = 0.4
    EMBEDDING_TERMINOLOGY_SIMILARITY: float = EMBEDDING_DEFAULT_SIMILARITY
    EMBEDDING_DATA_TRAINING_SIMILARITY: float = EMBEDDING_DEFAULT_SIMILARITY
    EMBEDDING_TABLE_SIMILARITY: float = EMBEDDING_DEFAULT_SIMILARITY
    EMBEDDING_DS_SIMILARITY: float = EMBEDDING_DEFAULT_SIMILARITY
    EMBEDDING_DEFAULT_TOP_COUNT: int = 5
    EMBEDDING_TERMINOLOGY_TOP_COUNT: int = EMBEDDING_DEFAULT_TOP_COUNT
    EMBEDDING_DATA_TRAINING_TOP_COUNT: int = EMBEDDING_DEFAULT_TOP_COUNT

    # 是否启用SQL查询行数限制，默认值，可被参数配置覆盖
    GENERATE_SQL_QUERY_LIMIT_ENABLED: bool = True
    GENERATE_SQL_QUERY_HISTORY_ROUND_COUNT: int = 3

    # 安全配置：是否允许元数据查询（SHOW/DESCRIBE/DESC/EXPLAIN）
    # 默认关闭，防止通过元数据查询泄露数据库结构
    SQLBOT_ALLOW_METADATA_QUERIES: bool = False

    PARSE_REASONING_BLOCK_ENABLED: bool = True
    DEFAULT_REASONING_CONTENT_START: str = "<think>"
    DEFAULT_REASONING_CONTENT_END: str = "</think>"

    PG_POOL_SIZE: int = 20
    PG_MAX_OVERFLOW: int = 30
    PG_POOL_RECYCLE: int = 3600
    PG_POOL_PRE_PING: bool = True

    TABLE_EMBEDDING_ENABLED: bool = True
    TABLE_EMBEDDING_COUNT: int = 10
    DS_EMBEDDING_COUNT: int = 10

    ORACLE_CLIENT_PATH: str = "/opt/sqlbot/db_client/oracle_instant_client"

    # Directory containing graph topology YAML files (default: backend/graphs/current)
    GRAPH_SPEC_DIR: str = ""
    CONVERSATION_MAX_WORKERS: int = 32
    CONVERSATION_STREAM_QUEUE_SIZE: int = 256
    CONVERSATION_RECURSION_LIMIT: int = 64
    CONVERSATION_QUERY_MAX_CONCURRENCY: int = 16
    CONVERSATION_QUEUED_RETRY_SEC: int = 15
    CONVERSATION_MAX_DISPATCH_ATTEMPTS: int = 2
    CONVERSATION_STATUS_PUSH_SEC: int = 10
    CONVERSATION_RUNNING_LEASE_SEC: int = 420
    LLM_REQUEST_TIMEOUT_SEC: int = 180
    LLM_MAX_RETRIES: int = 1
    QUERY_PLANNING_BUDGET_SEC: int = 180
    BUSINESS_TIMEZONE: str = "Asia/Shanghai"
    KNOWLEDGE_CAPTURE_LEASE_SECONDS: int = 300
    KNOWLEDGE_RECALL_STRATEGY: str = "unit"  # "unit" | "node" (v3.1 node-plane recall)
    # wiki 知识体系召回切换（v0 契约）：wiki=默认全量（allowlist 空或 * ），unit=回退
    KNOWLEDGE_BACKEND: str = "wiki"
    KNOWLEDGE_WIKI_DS_ALLOWLIST: str = "*"  # 逗号分隔 ds_id；* 或空 = 全量启用 wiki
    KNOWLEDGE_WIKI_PAGES_DIRS: str = "docs/wiki-knowledge/pplatform/wiki-pages"

    @computed_field  # type: ignore[misc]
    @property
    def knowledge_wiki_pages_dirs_abs(self) -> str:
        """PAGES_DIRS 的仓库根绝对形态——运行时从任意 cwd（uvicorn/脚本）加载一致。"""
        return ":".join(
            str((_REPO_ROOT / part).resolve()) if not Path(part).is_absolute() else part
            for part in self.KNOWLEDGE_WIKI_PAGES_DIRS.split(":")
            if part.strip()
        )

    KNOWLEDGE_WIKI_RECALL_TOP_K: int = 8
    KNOWLEDGE_WIKI_EMBEDDING_ENABLED: bool = True
    # wiki 主导表选择：wiki 命中时闭包表必选，embedding 召回补充 N 张
    # （0 = 不补充，仅闭包表；wiki 无命中时不裁剪走现状）
    WIKI_TABLE_SUPPLEMENT_COUNT: int = 4
    # wiki 主导模式下 embedding 补充表的相关性下限（独立于 WIKI_TABLE_SUPPLEMENT_COUNT
    # 的数量预算：分数不过线的表不进 prompt，不足预算不凑数）。默认对齐 wiki
    # 页级向量过滤强度（chat 169：0.4 的表级线拦不住 tenant_setting_config 类
    # 运营配置表，实际通过分 ~0.43-0.46 与业务表无区分度）
    WIKI_TABLE_SUPPLEMENT_SIMILARITY: float = 0.5
    # business 模式单页正文摘要上限（剔除 ground 围栏后的散文；0 = 不截断）
    KNOWLEDGE_WIKI_PROSE_CHARS: int = 400
    # 提取面：Test-wiki（需求文档 wiki）目录，E0.5 证据源；空=不用需求文档补充
    KNOWLEDGE_WIKI_REQDOC_DIR: str = ""

    # Recall top-up: deterministic value index ("value ⊂ question" containment)
    # plus evidence-driven working-set expansion. Any layer off = legacy recall.
    RECALL_VALUE_INDEX_ENABLED: bool = True
    RECALL_VALUE_INDEX_MAX_DISTINCT_RATIO: float = 0.2
    RECALL_VALUE_INDEX_TOP_K: int = 20
    RECALL_TOUP_ENABLED: bool = True
    RECALL_TOUP_DS_ALLOWLIST: str = ""  # comma-separated ds ids; empty = all

    # API datasource SSRF protection
    API_SSRF_PROTECTION: bool = True
    # Allow private/reserved IPs when SSRF protection is enabled (for internal deployments)
    API_SSRF_ALLOW_PRIVATE: bool = False
    API_MAX_RESPONSE_SIZE_MB: int = 10

    @field_validator(
        "SQL_DEBUG",
        "EMBEDDING_ENABLED",
        "GENERATE_SQL_QUERY_LIMIT_ENABLED",
        "PARSE_REASONING_BLOCK_ENABLED",
        "PG_POOL_PRE_PING",
        "TABLE_EMBEDDING_ENABLED",
        "RECALL_VALUE_INDEX_ENABLED",
        "RECALL_TOUP_ENABLED",
        "KNOWLEDGE_WIKI_EMBEDDING_ENABLED",
        mode="before",
    )
    @classmethod
    def lowercase_bool(cls, v: Any) -> Any:
        """将字符串形式的布尔值转换为Python布尔值"""
        if isinstance(v, str):
            v_lower = v.lower().strip()
            if v_lower == "true":
                return True
            elif v_lower == "false":
                return False
        return v


settings = Settings()  # type: ignore
