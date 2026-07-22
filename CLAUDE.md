# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SQLBot is an LLM + RAG-powered conversational data analysis (ChatBI) system by DataEase. Users ask natural-language questions; the system retrieves table/column embeddings, generates SQL via an LLM, executes it against the configured datasource, and renders the result as a chart. The repo is a monorepo with three deployable surfaces: `backend/` (FastAPI Python), `frontend/` (Vite/React), and `g2-ssr/` (Node.js server for chart rendering). Backend is the focus of this file.

## Tech Stack & Constraints

- Python 3.11, FastAPI, SQLModel + SQLAlchemy, Pydantic v2 / pydantic-settings
- Postgres 16 (system DB), pgvector (embeddings)
- LangChain 0.3 + LangGraph for LLM orchestration; supports OpenAI-compatible APIs (Tongyi/Qianfan/DeepSeek/Kimi/Gemini/MiniMax/etc.) plus Azure and vLLM
- HuggingFace `sentence-transformers` for the local embedding model (`shibing624/text2vec-base-chinese` by default)
- `dmpython` is pinned to `2.5.22` and conditional on `platform_system != 'Darwin'` — DM datasource will not work on macOS dev hosts
- Tooling: `uv` for deps, `ruff` (lint+format), `mypy` (strict), `pytest` + `coverage`, `pre-commit`
- Rust-typed `bcrypt==4.0.1` (passlib compat pin)
- License: FIT2CLOUD Open Source License (GPLv3 with restrictions — see `LICENSE`). Do not replace logo/copyright. Commercial licensing: `support@fit2cloud.com`

## Common Commands

All backend commands run from `backend/`. A virtualenv is expected at `backend/venv/`. The project reads `.env` from the repo root (one level above `backend/`) — `common/core/config.py` sets `env_file="../.env"`.

```bash
# Install / sync (uses uv; see backend/pyproject.toml)
cd backend
uv sync --extra cpu              # CPU torch; use --extra cu128 for GPU

# Run dev server (auto-migrates DB on startup)
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Lint + format check
bash scripts/lint.sh             # mypy on app/, ruff check, ruff format --check
bash scripts/format.sh           # ruff --fix + ruff format

# Tests
bash scripts/tests-start.sh      # runs app/tests_pre_start.py then scripts/test.sh
bash scripts/test.sh             # coverage run -m pytest + report + html
pytest tests/test_cwe89_escape_fix.py -v   # single file (from repo root; reads backend/ via path)
pytest -k name_substring                  # single test by name

# DB migrations (Alembic)
alembic upgrade head
alembic revision --autogenerate -m "msg"   # autogenerate is restricted — see Migrations
```

## Architecture (Backend)

`backend/main.py` is the FastAPI entrypoint. It builds the app, registers middleware, mounts routers, and runs an async `lifespan` that performs startup work: alembic migrations, cache init, dynamic CORS init, RAG embedding backfill, and xpack init.

### Layered layout under `backend/`

- `apps/` — feature modules. Each follows the same shape: `api/` (FastAPI routers), `curd/` or `crud/` (DB business logic), `models/` (SQLModel tables + Pydantic DTOs), sometimes `schemas/`, `middleware/`, `utils/`. Notable:
  - `apps/chat/` — Q&A endpoints and the LLM service. The hot path lives in `apps/chat/task/llm.py` (≈2000 LOC) — `LLMService` runs the full generate-SQL → execute → generate-chart pipeline, also `analysis` and `predict_data` and `recommend_questions` flows. Quick commands like `/regenerate`, `/analysis`, `/predict` are parsed in `common/utils/command_utils.py`.
  - `apps/datasource/` — datasources, table/field metadata, embedding (`apps/datasource/embedding/`), row/column permissions. The `CoreDatasource` model also embeds an `Excel/CSV` virtual type that round-trips through a Postgres table.
  - `apps/ai_model/` — LLM factory (`model_factory.py`) and embedding cache. `LLMFactory` registers `openai|tongyi|azure|vllm`; `EmbeddingModelCache` lazily loads the local HF model with a per-key lock.
  - `apps/system/` — users, workspaces, login, AI model config, assistants (embedded integrations), API keys, parameters. `apps/system/middleware/auth.py` is `TokenMiddleware` — handles bearer tokens, assistant tokens, and embedded tokens.
  - `apps/template/` — generators that pull prompt fragments from `backend/templates/template.yaml` (per-feature `generator.py` returns the relevant YAML subtree). The base SQL generation rules live in `templates/template.yaml` and per-dialect examples in `templates/sql_examples/{DBName}.yaml`.
  - `apps/db/` — DB connection helpers, dialect-specific metadata SQL (`db_sql.py`), engine factory, ES engine. `DB` enum in `apps/db/constant.py` lists every supported dialect with quote prefix/suffix, connect type, and template filename.
  - `apps/mcp/` — MCP server routes mounted at `/mcp`. `main.py` also creates a `FastApiMCP` instance and mounts it under `mcp_app` on port 8001 (`start.sh` runs `uvicorn main:mcp_app` separately for the MCP service).
  - `apps/dashboard/`, `apps/data_training/`, `apps/terminology/`, `apps/settings/`, `apps/swagger/`.
- `common/core/` — cross-cutting: `config.py` (Pydantic settings), `db.py` (engine + session), `deps.py` (`SessionDep`, `CurrentUser`, `CurrentAssistant`, `Trans`), `pagination.py`, `response_middleware.py` (wraps responses into `{code, data, msg}` envelope), `sqlbot_cache.py` (memory/redis cache decorator), `security.py` (JWT + bcrypt), `security_config.py`.
- `common/utils/` — `i18n` (`locale.py`), `embedding_threads.py` (background executor for embedding backfill), `data_format.py` (chart-row normalization incl. Hive `alias.column` keys), `command_utils.py`, `whitelist.py` (auth bypass list), `crypto.py` (xpack-backed encrypt/decrypt for stored secrets), `snowflake.py` (id generation, used by `common/core/models.py::SnowflakeBase`).
- `common/audit/` — `@system_log` decorator + `OperationType`/`OperationModules` enums. Decorate API handlers to record who did what. `request_context.py` exposes a `ContextVar` to fetch the current request from inside services.
- `apps/swagger/i18n.py` — translates OpenAPI doc strings via placeholders; supports `en`/`zh` and feeds `/docs` + `/openapi.json`.
- `locales/` — UI translation JSON (`zh-CN`, `zh-TW`, `en`, `ko-KR`).

### Key middleware stack (order matters in `main.py`)

1. `CORSMiddleware` (from settings)
2. `TokenMiddleware` (custom) — validates `X-SQLBOT-TOKEN` / `X-SQLBOT-ASSISTANT-TOKEN` / `X-SQLBOT-ASK-TOKEN`, sets `request.state.current_user` and `request.state.assistant`. Whitelisted paths bypass via `common/utils/whitelist.py::whiteUtils`.
3. `ResponseMiddleware` — wraps JSON bodies into `{code, data, msg}` envelope; some paths opt out (mcp_question, mcp_assistant, openapi, docs).
4. `RequestContextMiddleware` (local + Common) — sets the `RequestContext` ContextVar.

`RequestContextMiddleware` must be installed for any code that calls `RequestContext.get_request()` (e.g., the `@require_permissions` decorator in `apps/system/schemas/permission.py`).

### Request flow — end to end

1. Router in `apps/chat/api/chat.py` receives `/chat/question` with `CurrentUser` and `CurrentAssistant` injected by `common/core/deps.py`.
2. `parse_quick_command` checks for `/regenerate` etc., then dispatches to `stream_sql` (or `analysis_or_predict`).
3. `LLMService.create` (`apps/chat/task/llm.py`) resolves the LLM via `LLMFactory.create_llm`, with the user's default model or a chat-specific one; loads the datasource, applies RAG (terminology + data-training + table/ds embeddings via `EmbeddingModelCache`), constructs the prompt from `templates/template.yaml` + dialect example from `templates/sql_examples/{db}.yaml`, calls the LLM to generate SQL, executes it through `apps/db/db.py::exec_sql` (with row/column permission filters applied), then calls the LLM again to choose a chart spec.
4. Streaming response is delivered as `text/event-stream` chunks. The whole pipeline is logged via `apps/chat/curd/chat.py` (`save_question`, `save_sql`, `save_chart`, etc.) and the `ChatLog` table is the **single process-audit channel** for Execution Details (graph spans via `apps.chat.steps.observability.log_span` + domain steps). Do not invent a parallel trace store; put batch/attempt identity in span meta, not new tables.
5. Audit trail: `@system_log` on the route writes a row to `system_log` (operation, module, resource id, status).

### Permissions

- `apps/system/schemas/permission.py::require_permissions` is the route-level RBAC/workspace decorator. It supports `role: ['admin'|'ws_admin'|'...']` and `type/keyExpression` for workspace-scoped resources (`ds` or `chat`). `keyExpression` uses a small expression language (`args[N]`, dotted attribute paths) — see `check_ws_permission`.
- The token system supports three auth modes: standard bearer (`apps.system.api.login`), assistant-token (with `embedded` sub-scheme for iframe embeds), and API-key `sk ...` (`apps/system/api/apikey.py` + `validateAskToken`).
- `SQLBOT_ALLOW_METADATA_QUERIES` (default `False`) blocks `SHOW/DESCRIBE/DESC/EXPLAIN` to prevent schema leakage.

### RAG / embeddings

- Local model: `apps/ai_model/embedding.py::EmbeddingModelCache` wraps `HuggingFaceEmbeddings` with per-key locks and a singleton dict. Model path comes from `settings.LOCAL_MODEL_PATH` and `settings.DEFAULT_EMBEDDING_MODEL`.
- RAG inputs: terminology terms (`apps/terminology/`), data-training Q→SQL pairs (`apps/data_training/`), table/column embeddings (`apps/datasource/embedding/`).
- Backfill on startup: `common/utils/embedding_threads.py` exposes `fill_empty_*` functions that submit to a module-level `ThreadPoolExecutor(max_workers=200)` — invoked from the `lifespan` in `main.py`.
- Cosine similarity threshold/count: `settings.EMBEDDING_*_SIMILARITY` and `settings.EMBEDDING_*_TOP_COUNT`, `settings.TABLE_EMBEDDING_COUNT`, `settings.DS_EMBEDDING_COUNT`.

### Migrations

`backend/alembic/` — 27+ revisions, the latest consolidated schema lives in the `core_*` tables. `mypy` and `ruff` exclude `alembic/`. When creating a new revision, follow the existing numeric prefix pattern (`NNN_short_slug.py`) and add column comments where the existing migrations do (recent commit history shows this is enforced — see `7d435459` "补充内置数据库表字段备注"). `pyproject.toml` excludes `alembic` from mypy/ruff.

### xpack

`sqlbot_xpack` is a private package installed from `testpypi` (see `pyproject.toml` `[tool.uv.sources]`). It supplies: extra LLM providers, license validation, audit extras, MCP auth extras, embedded-assistant extras. `main.py` calls `sqlbot_xpack.init_fastapi_app(app)` and the `lifespan` calls `sqlbot_xpack.core.clean_xpack_cache()` and `monitor_app(app)`. Functions like `find_custom_prompts`, `get_out_ds_conf`, `transRecord2DTO`, `build_resource_union_query` are xpack-provided. The repo `.gitignore` excludes `sqlbot-xpack/` — it is not in this repo.

### Cache

`common/core/sqlbot_cache.py` provides a `@cache(expire, namespace, cacheName=..., keyExpression=...)` decorator backed by `fastapi-cache2`. When `CACHE_TYPE="redis"`, `init_sqlbot_cache` creates an async redis client; with `"memory"` (default), the in-memory backend is used and multi-process mode is unsupported (logged as a warning). `clear_cache` is the matching invalidator.

### Frontend / SSR

Out of scope for backend work, but worth knowing: the chat API streams chunks that the frontend renders through `g2-ssr/` (a Node server exporting chart images) and through the dashboard endpoints. `SERVER_IMAGE_HOST` and `MCP_IMAGE_HOST` configure those URLs.

## Development Practices

- Strict mypy (`strict = true`); `target-version = "py310"`. New modules need type hints.
- Ruff rules: `E, W, F, I, B, C4, UP, ARG001`. E501/B008/W191/B904 are ignored.
- `pyupgrade.keep-runtime-typing = true` — even with `from __future__ import annotations`, runtime typing is preserved.
- Routes that mutate state should be decorated with `@system_log(LogConfig(operation_type=..., module=..., ...))` and call `@require_permissions` where applicable.
- The response envelope (`{code, data, msg}`) is added by `ResponseMiddleware`. Returning raw dicts in API code is fine — the middleware wraps them. Some endpoints (MCP/streaming/docs) are in the `direct_paths` skip list and should not be wrapped.
- Use `from common.core.deps import SessionDep, CurrentUser, CurrentAssistant, Trans` for dependency injection. For translation in services, get `I18nHelper` via `Trans` and call `trans('i18n_xxx')` keys (defined in `apps/swagger/locales/{lang}.json` and `locales/{lang}.json`).
- When adding new system config keys, extend `Settings` in `common/core/config.py` and (for booleans) add to the `lowercase_bool` validator.
- Excel/CSV datasources use the same Postgres `engine` as the system DB — `get_engine_config()` reads from settings. Uploads land in `settings.EXCEL_PATH` (`/opt/sqlbot/data/excel` in Docker).

## Testing

- `tests/` (repo root) holds standalone pytest tests that load code from `backend/` via path hacks (e.g., `test_cwe89_escape_fix.py` reads `row_permission.py` and `exec`s it in a synthetic namespace to test the SQL-injection fix in isolation).
- `backend/scripts/test.sh` runs the full `pytest` suite from inside `backend/` with coverage. CI does not run the test suite (no GitHub Actions test workflow is present — only `typos_check.yml` runs on push/PR). Use `bash scripts/tests-start.sh` to run with the prestart hook.
- Add tests next to new safety-critical logic (permission filters, SQL generation, JWT handling).

## Useful entrypoints when exploring

- FastAPI app + middleware wiring: `backend/main.py`
- API surface: `backend/apps/api.py`
- The hot path: `backend/apps/chat/api/chat.py`, `backend/apps/chat/task/llm.py`
- LLM + embedding factories: `backend/apps/ai_model/model_factory.py`, `backend/apps/ai_model/embedding.py`
- Auth: `backend/apps/system/middleware/auth.py`, `backend/common/core/security.py`
- Permission decorator: `backend/apps/system/schemas/permission.py`
- Settings: `backend/common/core/config.py`
- DB + URL construction per dialect: `backend/apps/db/db.py`, `backend/apps/db/constant.py`, `backend/apps/db/db_sql.py`
- Templates: `backend/templates/template.yaml` and `backend/templates/sql_examples/*.yaml`
- Audit decorator: `backend/common/audit/schemas/logger_decorator.py`
