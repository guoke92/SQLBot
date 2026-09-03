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
pytest tests/test_query_intent_v6.py -v
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

1. `apps/api.py` calls `bootstrap_graphs()` (defined in `apps/conversation/graph_loader.py`) at import time.
2. YAML under `backend/graphs/current/` (override via `GRAPH_SPEC_DIR`) is the **sole topology source**.
3. Callers use `submit_graph(graph_key, state)` from `apps.conversation.runtime`.
4. Node bodies live in `apps/chat/graphs/nodes/{nlq,recommend}.py`; the `metadata` graph's nodes live in `apps/datasource/profiling/graphs/nodes/`.
5. `plan_query → plan_gate` (deterministic): the gate verifies terminal negatives — `unsupported.missing_concepts` are looked up against the catalog map / value index (`apps/chat/steps/recall_topup.py` + `apps/datasource/recall/value_index.py`); a resolvable concept bounces once back into `plan_query` with an expanded working set (snapshot write-back to `query_run.planning_context` is mandatory — plan_query restores from it on every entry). `ready` gets an advisory entity-coverage lint only. Gate off (`RECALL_TOUP_ENABLED=false`) = exact legacy routing via `route_after_planning`. A hard-gate `ACCESS_POLICY_VIOLATION` for a map-visible table is a recall gap: `_topup_on_failed_gates` expands it and the decision is re-validated against the expanded window (stale gate errors are never sent to the repairer); only hallucinated/out-of-scope tables (or non-SQL violations) stay fatal.
6. Domain steps / observability live in `apps/chat/steps/` (prefer existing steps + `log_span`).

| graph_key   | YAML                         | Purpose                          |
|-------------|------------------------------|----------------------------------|
| `chat`      | `graphs/current/chat.yaml`   | Unified topology for query, analysis, and prediction turns (plan → execute → chart → summarize) |
| `recommend` | `graphs/current/recommend.yaml` | Recommended questions          |
| `config`    | `graphs/current/config.yaml`   | Config assistant               |
| `metadata`  | `graphs/current/metadata.yaml` | Agent-only metadata cognition mining: discovers candidate relations via ReAct tools; facts bootstrap is owned by the profiling worker |

Query, analysis, and prediction turns share the single `chat.yaml` (v6 unified architecture, `docs/对话路由与查询执行统一架构-v6.md`). Do not re-submit old `analysis`/`predict` graph keys — those YAMLs no longer exist.

Graph docs: `backend/graphs/README.md`. Deeper backend notes: `CLAUDE.md` (may lag graphs — prefer this file + YAML for the chat path).

### Chat-related modules worth knowing

| Path | Role |
|------|------|
| `apps/conversation/` | Graph loader, runtime, sinks, session, tooling |
| `apps/chat/api/chat.py` | HTTP/SSE entry; dispatches `submit_graph` |
| `apps/chat/turn_contracts.py` | `TurnRoute` + terminal answer payload contracts (single validation home) |
| `apps/chat/turn_router.py` | Cheap turn routing; never performs semantic query planning |
| `apps/chat/query_intent.py` | Compact business intent — what the user wants, not physical tables/joins |
| `apps/chat/semantic_planning.py` | Planning decisions + the single clarification-card contract |
| `apps/chat/planning_context.py` | Durable, replayable retrieval boundary persisted on the `nlq_run` row |
| `apps/chat/plan_policy.py` / `planning.py` | Batch planning limits & policy |
| `apps/chat/steps/` | Schema/SQL/chart/knowledge steps + `observability.log_span`; recall top-up resolver+fulfiller in `recall_topup.py`, planner maps in `recall_map.py` |
| `apps/datasource/recall/` | Value index: per-DS process-local index (published dictionary values ∪ profiling low-cardinality `top_values`), "value ⊂ text" containment matching, generation-stamped invalidation |
| `apps/dictionary/` | Dictionary domain |
| `apps/knowledge/` | Knowledge Architecture v3.1 (see below) |
| `apps/terminology/` / `apps/data_training/` | RAG terminology + Q→SQL training |

### Knowledge subsystem (Architecture v3.1)

- ADR: `docs/知识体系目标架构-v3.1.md`; 提取技能（唯一权威，含类型族/绑定校验码表/坏样本/成功标准）: `.cursor/skills/knowledge-extraction/`（`SKILL.md` + `reference.md` + `examples.md`）。
- `graph/` — unit node store (assembly, decompose, feedback); `semantic/` — authoritative semantic layer (runtime K1–K5 assets are projections of approved unit revisions; `lint.py` / `schema.py` / `service.py`); `compile/` — seed policy + business-data bundle application; `capture/` + `staging/` — capture jobs and candidate admission; `lineage/` — promotion audit events; `gateway.py` — recall gateway.
- Extracting business knowledge from a business system's source code follows the `.cursor/skills/knowledge-extraction/` skill (produces KnowledgePackageV2 unit packages).
- `apps/knowledge/retrieval/` and `importing/` hold only stale `__pycache__` (no source) — do not import from them.
- `apps/knowledge/wiki/` — 新一代 wiki 知识体系（prototype，独立于 unit 知识包）：页面契约/切块/RRF+图扩展召回（权威契约 `docs/wiki页面契约-spec-v0.md`，运行面文本直拼 prompt，切换见 `docs/wiki-knowledge/wiki召回接口-v1.md`；产品化/证据基座/锚点闭包/关系通道完整方案见 `docs/wiki-knowledge/wiki知识体系完整方案-v1.md`）

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
| `datasource/` | Datasources, metadata, embeddings, row/col permissions, `profiling/` (mining worker + `metadata` graph nodes) |
| `system/` | Users, workspaces, login, assistants, API keys |
| `template/` | Prompt generators from `templates/template.yaml` |
| `db/` | Connections, dialect metadata SQL, engine factory |
| `dashboard/` | Dashboard/chart endpoints |
| `config_assistant/` | Config-chat graph entry |
| `settings/` / `swagger/` | App settings, OpenAPI i18n |
| `protocol/` | Protocol base + registry with `rest/` and `sql/` implementations |

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
- Prefer contracts in `turn_contracts` / `query_intent` / `planning_context` over ad-hoc dicts

### Turn routing & planning contracts

- `apps/chat/turn_contracts.py` is the single validation home for turn routing
  and terminal answers. `TurnRoute.task_kind` is one of
  `query | analysis | prediction | unsupported`; `relation` is
  `independent | continue | revise`. Cross-field rules (analysis requires
  referenced datasets, continuation/revision require references, unsupported
  turns cannot reference records) live in the model validator — extend it
  instead of re-checking in callers.
- `apps/chat/planning_context.py` is the durable, replayable input boundary for
  semantic planning: LangGraph checkpoints carry IDs and orchestration state
  only; retrieval snapshots persist on the `nlq_run` row (`planning_context`
  column) and are restored on resume.
- `apps/chat/query_intent.py` describes what the user wants — never physical
  tables, joins, or expressions; `semantic_planning.py` owns planning decisions
  and the single clarification-card contract.

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
