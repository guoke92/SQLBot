# AGENTS.md

Workspace instructions for AI coding agents working on AI智能问数 (SQLBot).

## What is AI智能问数?

A ChatBI system: users ask natural-language questions; the system retrieves schema/knowledge via RAG, plans and generates SQL, executes it against a configured datasource, and renders charts. Built by DataEase / FIT2CLOUD.

**License**: FIT2CLOUD Open Source (GPLv3 with restrictions). Do not replace logo or copyright text.

## Repository Layout

```
backend/          FastAPI (Python 3.11) — primary codebase
  apps/           Feature modules (chat, conversation, datasource, …)
  graphs/         LangGraph YAML topologies (current/ = production)
  templates/      Prompt YAML + dialect SQL examples
  common/         Settings, DB, auth deps, cache, audit
frontend/         Vue 3 + Vite + TypeScript + Element Plus
g2-ssr/           Node.js chart SSR (AntV G2, port 3000, PM2)
installer/        Bare-metal Linux installer + sctl CLI
tests/            Root-level pytest (imports backend/ via path)
docs/             Documentation sources
scripts/          Dev helpers (sqlbot-dev.sh lives at repo root)
```

## Quick Commands

### Backend (from `backend/`)

```bash
uv sync --extra cpu                              # Install deps (cu128 for GPU)
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
bash scripts/lint.sh                             # mypy + ruff check + format --check
bash scripts/format.sh                           # ruff --fix + format
bash scripts/tests-start.sh                      # Full suite with prestart
bash scripts/test.sh                             # pytest + coverage
alembic upgrade head
```

From repo root for focused tests:

```bash
pytest tests/test_semantic_intent.py -v
pytest -k name_substring
```

### Frontend (from `frontend/`)

```bash
pnpm install && pnpm dev    # port 5173
pnpm build && pnpm lint
```

### Full-stack (repo root)

```bash
./sqlbot-dev.sh setup-env | start all | status
```

## Hot Path — Conversation Graphs

**Do not treat `apps/chat/task/llm.py` as the sole pipeline.** Production Q&A runs through LangGraph:

1. `apps/api.py` calls `bootstrap_graphs()` at import time.
2. YAML under `backend/graphs/current/` (override via `GRAPH_SPEC_DIR`) is the **sole topology source**.
3. Callers use `submit_graph(graph_key, state)` from `apps.conversation.runtime`.
4. Node bodies live in `apps/chat/graphs/nodes/{nlq,analysis,predict,recommend}.py`.
5. Domain steps / observability live in `apps/chat/steps/` (prefer existing steps + `log_span`).

| graph_key   | YAML                         | Purpose                          |
|-------------|------------------------------|----------------------------------|
| `chat`      | `graphs/current/chat.yaml`   | NLQ: plan → execute → chart → summarize |
| `analysis`  | `graphs/current/analysis.yaml` | Follow-up analysis             |
| `predict`   | `graphs/current/predict.yaml`  | Prediction                     |
| `recommend` | `graphs/current/recommend.yaml`| Recommended questions          |
| `config`    | `graphs/current/config.yaml`   | Config assistant               |

Graph docs: `backend/graphs/README.md`. Deeper backend notes: `CLAUDE.md` (may lag graphs — prefer this file + YAML for the chat path).

### Chat-related modules worth knowing

| Path | Role |
|------|------|
| `apps/conversation/` | Graph loader, runtime, sinks, session, tooling |
| `apps/chat/api/chat.py` | HTTP/SSE entry; dispatches `submit_graph` |
| `apps/chat/semantic_intent.py` / `query_contract.py` / `plan_context.py` | Intent & plan contracts |
| `apps/chat/contract/` | `ContractIssue` model + the single `validate_contract` entry point |
| `apps/chat/plan_policy.py` / `planning.py` | Batch planning limits & policy |
| `apps/chat/steps/` | Schema/SQL/chart/knowledge steps + `observability.log_span` |
| `apps/dictionary/` / `apps/knowledge/` | Dictionary & knowledge recall |
| `apps/terminology/` / `apps/data_training/` | RAG terminology + Q→SQL training |

## Backend Architecture (summary)

- **Entrypoint**: `backend/main.py` — middleware, routers, lifespan (migrations, cache, CORS, embedding backfill)
- **Config**: `backend/common/core/config.py` — reads `../.env` (repo root)
- **Auth**: `TokenMiddleware` — bearer / assistant / API-key (`X-SQLBOT-*` headers)
- **Response envelope**: `{code, data, msg}` via `ResponseMiddleware`; streaming/MCP/docs excluded
- **LLM factory**: `apps/ai_model/model_factory.py`; embeddings via `EmbeddingModelCache`
- **MCP**: `apps/mcp/` on port 8001 (separate uvicorn)
- **xpack**: private `sqlbot_xpack` (not in repo) — license, extra providers, embed extras

### Other `backend/apps/` modules

| Module | Purpose |
|--------|---------|
| `datasource/` | Datasources, metadata, embeddings, row/col permissions |
| `system/` | Users, workspaces, login, assistants, API keys |
| `template/` | Prompt generators from `templates/template.yaml` |
| `db/` | Connections, dialect metadata SQL, engine factory |
| `dashboard/` | Dashboard/chart endpoints |
| `config_assistant/` | Config-chat graph entry |
| `settings/` / `swagger/` | App settings, OpenAPI i18n |

## Frontend Architecture

- Vue 3 + Vite + TypeScript + Pinia + Element Plus
- Hash routes: `/login`, `/chat`, `/dashboard`, `/set`, `/system`, `/assistant`
- API base: `VITE_API_BASE_URL` (`http://localhost:8000/api/v1` in dev); chat via SSE `fetchStream`
- Charts: AntV G2 client-side; g2-ssr for MCP/embedded images
- i18n: `en`, `zh-CN`, `zh-TW`, `ko-KR` under `frontend/src/i18n/`

## Conventions

### Python

- Strict mypy (`strict = true`, target 3.10+); Ruff: `E, W, F, I, B, C4, UP, ARG001` (ignore E501, B008, W191, B904)
- DI: `SessionDep`, `CurrentUser`, `CurrentAssistant`, `Trans` from `common.core.deps`
- Mutating routes: `@system_log(...)` + `@require_permissions` where applicable
- New settings: extend `Settings` in `common/core/config.py`
- Graph topology changes → edit YAML in `backend/graphs/`; node logic → Python under `apps/chat/graphs/nodes/`
- Prefer contracts in `query_contract` / `semantic_intent` / `plan_context` over ad-hoc dicts

### Query contract layering

A frozen contract is not uniformly permanent, and this is what keeps a bad
inference from dead-ending a turn:

- A clause is **confirmed** only when `evidence_refs` cites `user:question` or
  `user:answer:<id>`; `RequirementBase` demotes any other `source="user"` claim
  to `"model"`. Everything else is a revocable inference.
- Every expected contract problem is a `ContractIssue` from
  `apps/chat/contract/validation.py::validate_contract` — never a bespoke
  `ValueError` in a caller. Severity follows the layer: an issue caused only by
  inferences is `advisory` and is cleared by dropping them.
- `ContractDraft.minimal_executable()` is the escape hatch. When the assessor
  or a validator cannot complete, the turn runs on the confirmed core and every
  dropped clause becomes a `ContractAssumption` shown to the user.
- Model-output defects (invented fields, missing relation slots) still raise:
  they drive the repair turn and must not be routed to the user.
- SQL-vs-contract disagreement at plan time is **advisory**: the plans are kept
  and executed; quality reads `contract_status`. Joins are not judged against
  the contract (schema bridges are never named by the assessor); a
  user-confirmed `relation` slot is still verified in `_slot_state`.
  Dialect-certain refusals (e.g. Hive `ORDER BY t.col`) are rejected in
  `validate_plan` before execution.

### TypeScript / Vue

- Prettier: single quotes, no semicolons, trailing commas (es5), 100 cols, 2-space indent
- ESLint flat config: `typescript-eslint` + `vue` + `prettier`

## Observability (execution details)

Single audit channel: **`chat_log`** → `GET /chat/record/{id}/log` → frontend `ExecutionDetails`.

- Write spans via `apps.chat.steps.observability.log_span` or domain steps (`start_log`/`end_log` + `inject_span_meta`).
- Do **not** invent a second timeline from SSE or fabricate steps at `complete`.
- Envelope may include `{sqlbot_span, graph_node, step_index, gen_attempts, unit_index, brief, payload}`.
- Put batch/attempt identity in span meta — do not explode operate enums per attempt.

## Deployment

- Docker: `dataease/sqlbot` — Postgres 17 + uvicorn + g2-ssr + MCP (`docker-compose.yaml`, `start.sh`)
- Ports: 8000 (app), 8001 (MCP), 3000 (g2-ssr internal)
- Bare-metal: `installer/install.sh` + `sctl`

## Gotchas

- `.env` is at **repo root**, not under `backend/`
- `dmpython` excluded on Darwin — Dameng DS won't work on macOS
- `CACHE_TYPE=memory` does not support multi-process
- `RequestContextMiddleware` required for `@require_permissions`
- Excel/CSV uploads → `settings.EXCEL_PATH`
- Alembic: numeric prefix `NNN_short_slug.py`; mypy/ruff exclude `alembic/`
- g2-ssr needs `node-canvas` + `Arial_Unicode.ttf`
- YAML graph topology is authoritative; do not hard-code alternate graph wiring in Python
