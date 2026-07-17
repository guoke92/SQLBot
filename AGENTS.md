# AGENTS.md

Workspace instructions for AI coding agents working on SQLBot.

## What is SQLBot?

A ChatBI system: users ask natural-language questions, an LLM generates SQL, executes it against a configured datasource, and renders the result as a chart. Built by DataEase / FIT2CLOUD.

**License**: FIT2CLOUD Open Source (GPLv3 with restrictions). Do not replace logo or copyright text.

## Repository Layout

```
backend/          FastAPI (Python 3.11) — the primary codebase
frontend/         Vue 3 + Vite + TypeScript + Element Plus
g2-ssr/           Node.js chart SSR service (AntV G2, port 3000, managed by PM2)
installer/        Bare-metal Linux installer + sctl CLI
scripts/          Dev helper scripts (sqlbot-dev.sh)
tests/            Root-level pytest tests (load backend/ via path hacks)
docs/             Documentation sources
```

## Quick Commands

### Backend (from `backend/`)

```bash
uv sync --extra cpu                              # Install deps
uvicorn main:app --host 0.0.0.0 --port 8000 --reload   # Dev server
bash scripts/lint.sh                             # mypy + ruff check + ruff format --check
bash scripts/format.sh                           # ruff --fix + ruff format
bash scripts/tests-start.sh                      # Full test suite
bash scripts/test.sh                             # pytest + coverage
alembic upgrade head                             # Run DB migrations
```

### Frontend (from `frontend/`)

```bash
pnpm install        # Install deps
pnpm dev            # Dev server (port 5173)
pnpm build          # Production build
pnpm lint           # ESLint auto-fix
```

### Full-stack dev (from repo root)

```bash
./sqlbot-dev.sh setup-env       # Configure .env
./sqlbot-dev.sh start all       # Start backend + frontend
./sqlbot-dev.sh status          # Check services
```

## Backend Architecture

See `CLAUDE.md` for detailed backend architecture. Key points:

- **Entrypoint**: `backend/main.py` — builds app, registers middleware, mounts routers, runs lifespan (migrations, cache init, CORS, embedding backfill)
- **Config**: `backend/common/core/config.py` — Pydantic `Settings` reads `../.env` (repo root)
- **Auth**: `backend/apps/system/middleware/auth.py` — `TokenMiddleware` (bearer / assistant / API-key)
- **Response envelope**: All JSON wrapped into `{code, data, msg}` by `ResponseMiddleware`; streaming/MCP/docs paths excluded
- **Hot path**: `backend/apps/chat/task/llm.py` — full generate-SQL → execute → generate-chart pipeline
- **MCP server**: `backend/apps/mcp/` — mounted on port 8001, separate uvicorn process
- **xpack**: `sqlbot_xpack` is a private package (not in this repo) for extra LLM providers, license, audit

### Backend app modules (`backend/apps/`)

| Module | Purpose |
|--------|---------|
| `chat/` | Q&A endpoints, LLM pipeline, analysis, predict |
| `datasource/` | Datasources, metadata, embeddings, permissions |
| `ai_model/` | LLM factory, embedding model cache |
| `system/` | Users, workspaces, login, assistants, API keys |
| `template/` | Prompt generators from `templates/template.yaml` |
| `db/` | DB connection, dialect metadata SQL, engine factory |
| `mcp/` | MCP server routes |
| `dashboard/` | Dashboard/chart endpoints |
| `data_training/` | Q-to-SQL training pairs for RAG |
| `terminology/` | Terminology library for RAG |

## Frontend Architecture

- **Framework**: Vue 3 + Vite + TypeScript + Pinia + Element Plus
- **Routing**: Hash-based (`createWebHashHistory`). Routes: `/login`, `/chat`, `/dashboard`, `/set`, `/system`, `/assistant`
- **API**: REST via `VITE_API_BASE_URL` (`http://localhost:8000/api/v1` in dev). Chat uses SSE streaming via `fetchStream`
- **Charting**: AntV G2 (client-side), g2-ssr (server-side for MCP/embedded)
- **i18n**: 4 locales — `en`, `zh-CN`, `zh-TW`, `ko-KR` in `frontend/src/i18n/`

## Conventions

### Python (backend)

- **Strict mypy** (`strict = true`, target Python 3.10+)
- **Ruff** rules: `E, W, F, I, B, C4, UP, ARG001`. Ignores: E501, B008, W191, B904
- Use `SessionDep`, `CurrentUser`, `CurrentAssistant`, `Trans` from `common/core/deps.py` for dependency injection
- Routes that mutate state: add `@system_log(...)` decorator and `@require_permissions` where applicable
- Returning raw dicts is fine — `ResponseMiddleware` wraps them
- When adding config keys: extend `Settings` in `common/core/config.py`

### TypeScript/Vue (frontend)

- **Prettier**: single quotes, no semicolons, trailing commas (es5), 100 char width, 2-space indent
- **ESLint**: flat config with `typescript-eslint` + `eslint-plugin-vue` + `eslint-plugin-prettier`
- **Editor**: UTF-8, LF line endings

## Deployment

- **Docker**: Single container (`dataease/sqlbot`) running PostgreSQL 17 + backend (uvicorn) + g2-ssr (PM2) + MCP server. See `docker-compose.yaml` and `start.sh`
- **Ports**: 8000 (main app), 8001 (MCP), 3000 (g2-ssr, internal)
- **Bare-metal**: `installer/install.sh` + `sctl` CLI for Linux servers

## Gotchas

- `dmpython` (Dameng DB driver) is pinned and excluded on macOS — DM datasource won't work locally
- `.env` lives at repo root (not in `backend/`), read by `backend/common/core/config.py`
- Excel/CSV uploads land in `settings.EXCEL_PATH` (`/opt/sqlbot/data/excel` in Docker)
- Cache with `CACHE_TYPE="memory"` (default) does not support multi-process mode
- `REQUEST_CONTEXT_MIDDLEWARE` must be installed for `@require_permissions` to work
- g2-ssr requires `node-canvas` and a font file (`Arial_Unicode.ttf`) for server-side chart rendering
- Alembic migrations are in `backend/alembic/` — follow numeric prefix pattern (`NNN_short_slug.py`)
