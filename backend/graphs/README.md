# Graph Topology Configuration

## Overview

AI智能问数 product graphs (LangGraph) are defined as **YAML topology files**.
The YAML declares nodes (as dotted Python paths), edges, and routers.
The loader (`apps.conversation.graph_loader`) resolves the dotted paths,
builds a `StateGraph`, compiles it, and registers it under `graph_key`.

**YAML is the sole topology truth source.** Node/router *bodies* remain
Python; YAML only wires them together.

普通对话遵循 `docs/对话路由与查询执行统一架构-v6.md`：查询、分析和预测共用唯一
`chat.yaml`，节点内部不得再次提交旧 analysis/predict Graph。

## Directory Layout

```
backend/graphs/
├── current/        ← default production load (GRAPH_SPEC_DIR default)
│   ├── chat.yaml
│   ├── recommend.yaml
│   └── config.yaml
└── README.md       ← this file
```

## How It Works

1. `apps.api` calls `bootstrap_graphs()` at process start.
2. `bootstrap_graphs()` reads `settings.GRAPH_SPEC_DIR` (default: `backend/graphs/current`).
3. Each `*.yaml` file is parsed into a `GraphSpec` (validated schema).
4. Dotted paths are resolved to Python objects via `importlib`.
5. A `StateGraph` is built, compiled, and registered under the file's `graph_key`.
6. Product code calls `submit_graph("chat", state)` — query, analysis and
   prediction turns share that single durable topology. The runtime runs the
   graph compiled and registered during bootstrap.

## YAML Schema

```yaml
version: 1              # must be 1
graph_key: chat         # registry key (must match file stem for clarity)
state: apps.chat.graphs.nodes.nlq.NlqState # JSON-only checkpoint state
durable: true            # use checkpoint + shared run lifecycle (default)
description: "..."      # human-readable, not parsed

nodes:
  node_name: package.module.function_name   # must be importable + callable

edges:
  # Plain edge
  - from: START
    to: node_name

  # Conditional edge with builtin router
  - from: node_name
    router:
      type: ok_or_fail
      next: target_node
    paths:
      target_node: target_node
      fail: fail

  # Conditional edge with custom router
  - from: node_name
    router: package.module.router_function
    paths:
      option_a: target_a
      option_b: target_b
      fail: fail
```

### Validation Rules

- All `nodes` values must be importable and callable.
- `from`/`to` references must exist in `nodes` or be `START`/`END`.
- Conditional edge `paths` values must exist in `nodes` or be `END`.
- `ok_or_fail` requires `next` to be present in `paths`, and `fail` must be in `paths`.
- At least one edge from `START` is required.
- Duplicate `graph_key` across files is an error.
- `durable` must be boolean. Durable graphs receive run lifecycle/checkpoint
  handling; side-effect-free helper graphs may explicitly set `durable: false`.

## Builtin Routers

| Router | Usage | Behavior |
|--------|-------|----------|
| `ok_or_fail` | `{ type: ok_or_fail, next: X }` | Returns `fail` if `state["error"]` is set, otherwise `X` |

Custom routers are any Python callable `(state) -> str` returning a key
from the `paths` map.

## Selecting a graph directory

Set `GRAPH_SPEC_DIR` in `.env` (relative to `backend/` or absolute):

```bash
# Default production graphs
GRAPH_SPEC_DIR=
```

## Migration Notes

### Key Changes

- **`nlq` → `chat`**: The primary NLQ graph's registry key is now `chat`.
  The API, MCP, and all `submit_graph` callers use `"chat"`.
  There is **no** `"nlq"` alias.
- **No side-effect registration**: Graph modules no longer call
  `register_graph()` at import time. All registration goes through
  `bootstrap_graphs()` reading YAML.
- **Nodes extracted**: Implementations live in `apps.chat.graphs.nodes.*`
  (nlq, analysis, predict, recommend). Tool-enabled scenarios reuse
  `apps.conversation.agent`, `apps.conversation.tooling`, and
  `apps.conversation.turn`; `apps.config_assistant.nodes` only prepares
  configuration-specific state.

### predict

Predict remains an independent production graph.

### analysis

The `analysis` graph remains an independent production graph.

### config

The configuration assistant keeps its own topology because its domain and
termination rules differ from NLQ, while reusing the shared conversation
agent/tool/turn nodes:

```text
prepare -> agent -> execute_tools -> agent
                  \-> finish
          failures -> fail
```

Configuration tools are explicit domain adapters under
`apps.config_assistant.tools`; they call datasource, relationship,
terminology, and dictionary services instead of duplicating persistence logic.
