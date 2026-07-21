# Graph Topology Configuration

## Overview

SQLBot product graphs (LangGraph) are defined as **YAML topology files**.
The YAML declares nodes (as dotted Python paths), edges, and routers.
The loader (`apps.conversation.graph_loader`) resolves the dotted paths,
builds a `StateGraph`, compiles it, and registers it under `graph_key`.

**YAML is the sole topology truth source.** Node/router *bodies* remain
Python; YAML only wires them together.

## Directory Layout

```
backend/graphs/
├── current/        ← default production load (GRAPH_SPEC_DIR default)
│   ├── chat.yaml
│   ├── analysis.yaml
│   ├── predict.yaml
│   ├── recommend.yaml
│   └── config.yaml
├── target/         ← architecture draft (compile-ready, not default)
│   ├── chat.yaml   ← unified nlq_path + dialogue_path
│   ├── config.yaml
│   └── recommend.yaml
└── README.md       ← this file
```

## How It Works

1. `apps.api` calls `bootstrap_graphs()` at process start.
2. `bootstrap_graphs()` reads `settings.GRAPH_SPEC_DIR` (default: `backend/graphs/current`).
3. Each `*.yaml` file is parsed into a `GraphSpec` (validated schema).
4. Dotted paths are resolved to Python objects via `importlib`.
5. A `StateGraph` is built, compiled, and registered under the file's `graph_key`.
6. Product code calls `submit_graph("chat", state)` — the runtime looks up the
   registered builder, compiles a fresh graph, and runs it.

## YAML Schema

```yaml
version: 1              # must be 1
graph_key: chat         # registry key (must match file stem for clarity)
state: apps.chat.graphs.nodes.nlq.NlqState   # TypedDict dotted path
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

## Builtin Routers

| Router | Usage | Behavior |
|--------|-------|----------|
| `ok_or_fail` | `{ type: ok_or_fail, next: X }` | Returns `fail` if `state["error"]` is set, otherwise `X` |

Custom routers are any Python callable `(state) -> str` returning a key
from the `paths` map.

## Switching Between current/ and target/

Set `GRAPH_SPEC_DIR` in `.env` (relative to `backend/` or absolute):

```bash
# Default: current (production behaviour)
GRAPH_SPEC_DIR=

# Target architecture (requires dialogue stubs to be implemented)
GRAPH_SPEC_DIR=backend/graphs/target
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
  (nlq, analysis, predict, recommend) and `apps.config_assistant.nodes`.

### Target Graph (not default-loaded)

`graphs/target/chat.yaml` defines the unified chat graph with two internal paths:

- **nlq_path**: Same as current `chat.yaml` (generate_sql → execute → chart).
- **dialogue_path**: Stub nodes for multi-turn cognition
  (resolve_anchor → load_evidence → reason → synthesize → repair_brief → complete).

The dialogue path stubs are real callables that compile and run as no-ops.
Product implementation of Working Set and dialogue LLM is in a future PR.

### predict

Predict remains an independent graph in `current/`. The target plan notes
it will eventually merge into the chat graph as `chat.predict_path`, but
that is out of scope for this PR.

### analysis

The `analysis` graph remains independent in `current/`. In the target
architecture, analysis requests will be routed to `submit_graph("chat", intent="explain_result", ...)`,
eliminating the separate `analysis` key. This cutover is a future PR.
