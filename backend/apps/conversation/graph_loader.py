"""Load graph topology YAML and register compiled LangGraph builders.

Sole assembly path for product graphs. Call ``bootstrap_graphs()`` once at
process start (see ``apps.api``). Topology truth source = YAML under
``backend/graphs/`` (or ``settings.GRAPH_SPEC_DIR``).
"""

from __future__ import annotations

import importlib
import inspect
from collections.abc import Callable, Iterable, Mapping, MutableMapping
from functools import wraps
from pathlib import Path
from typing import (
    Any,
)

import yaml
from langgraph.graph import END, START, StateGraph

from apps.conversation.checkpoint import get_checkpointer
from apps.conversation.graph_spec import (
    ConditionalEdge,
    GraphSpec,
    GraphSpecError,
    OkOrFailRouter,
    PlainEdge,
    parse_graph_spec,
)
from apps.conversation.registry import clear_registry, register_graph
from apps.conversation.routers_builtin import ok_or_fail
from common.utils.utils import SQLBotLogUtil

# backend/ — parent of apps/
_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_SPEC_DIR = _BACKEND_ROOT / "graphs" / "current"


def default_spec_dir() -> Path:
    """Resolve configured or default topology directory."""
    try:
        from common.core.config import settings

        raw = (getattr(settings, "GRAPH_SPEC_DIR", None) or "").strip()
        if raw:
            p = Path(raw)
            if not p.is_absolute():
                p = (_BACKEND_ROOT / p).resolve()
            return p
    except Exception:
        pass
    return _DEFAULT_SPEC_DIR


def resolve_dotted(path: str) -> Any:
    """Import ``package.module.attr`` and return the attribute."""
    dotted = (path or "").strip()
    if not dotted or "." not in dotted:
        raise GraphSpecError(f"invalid dotted path: {path!r}")
    module_path, _, attr = dotted.rpartition(".")
    try:
        mod = importlib.import_module(module_path)
    except ImportError as e:
        raise GraphSpecError(
            f"cannot import module {module_path!r} for {path!r}"
        ) from e
    try:
        obj = getattr(mod, attr)
    except AttributeError as e:
        raise GraphSpecError(f"module {module_path!r} has no attribute {attr!r}") from e
    return obj


def resolve_callable(path: str) -> Callable[..., Any]:
    obj = resolve_dotted(path)
    if not callable(obj):
        raise GraphSpecError(f"resolved object is not callable: {path!r}")
    return obj


def resolve_state_type(path: str) -> type:
    obj = resolve_dotted(path)
    if not isinstance(obj, type):
        raise GraphSpecError(
            f"state must be a type, got {type(obj).__name__}: {path!r}"
        )
    return obj


def _endpoint(name: str) -> Any:
    if name == "START":
        return START
    if name == "END":
        return END
    return name


def _resolve_router(ref: Any) -> Callable[..., Any]:
    if isinstance(ref, OkOrFailRouter):
        return ok_or_fail(ref.next)
    if isinstance(ref, str):
        return resolve_callable(ref)
    raise GraphSpecError(f"unsupported router ref: {ref!r}")


def _map_paths(paths: Mapping[str, str]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k, v in paths.items():
        out[k] = END if v == "END" else v
    return out


def compile_graph(spec: GraphSpec) -> Any:
    """Build and compile a LangGraph ``StateGraph`` from ``spec``."""
    state_cls = resolve_state_type(spec.state)
    g: StateGraph = StateGraph(state_cls)

    for node_name, node_path in spec.nodes.items():
        fn = resolve_callable(node_path)
        g.add_node(
            node_name,
            _with_run_lifecycle(spec.graph_key, node_name, fn) if spec.durable else fn,
        )

    for edge in spec.edges:
        if isinstance(edge, PlainEdge):
            g.add_edge(_endpoint(edge.source), _endpoint(edge.target))
        elif isinstance(edge, ConditionalEdge):
            router = _resolve_router(edge.router)
            g.add_conditional_edges(
                _endpoint(edge.source),
                router,
                _map_paths(edge.paths),
            )
        else:  # pragma: no cover
            raise GraphSpecError(f"unknown edge type: {type(edge)!r}")

    return g.compile(checkpointer=get_checkpointer() if spec.durable else None)


def _with_run_lifecycle(
    _graph_key: str, name: str, fn: Callable[..., Any]
) -> Callable[..., Any]:
    """Record graph position without putting persistence code in every node."""

    def _mark(state: Any) -> None:
        if not isinstance(state, Mapping) or not state.get("run_id"):
            return
        from apps.conversation.models import ConversationRun
        from apps.conversation.run_service import (
            ConversationRunCancelled,
            update_run_status,
        )
        from apps.conversation.session import session_scope

        with session_scope() as session:
            run = session.get(ConversationRun, str(state["run_id"]))
            if run is None:
                raise LookupError(f"Conversation run {state['run_id']} not found")
            if run.status == "cancelled":
                raise ConversationRunCancelled(str(state["run_id"]))
            update_run_status(
                session, str(state["run_id"]), "running", current_node=name
            )

    if inspect.iscoroutinefunction(fn):

        @wraps(fn)
        async def _async(state: Any, *args: Any, **kwargs: Any) -> Any:
            _mark(state)
            return await fn(state, *args, **kwargs)

        return _async

    @wraps(fn)
    def _sync(state: Any, *args: Any, **kwargs: Any) -> Any:
        _mark(state)
        return fn(state, *args, **kwargs)

    return _sync


def load_spec_file(path: Path) -> GraphSpec:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        raise GraphSpecError(f"cannot read graph spec {path}: {e}") from e
    try:
        raw = yaml.safe_load(text)
    except yaml.YAMLError as e:
        raise GraphSpecError(f"invalid YAML in {path}: {e}") from e
    return parse_graph_spec(raw, source_path=str(path))


def iter_spec_files(spec_dir: Path) -> list[Path]:
    if not spec_dir.is_dir():
        raise GraphSpecError(f"graph spec directory not found: {spec_dir}")
    files = sorted(spec_dir.glob("*.yaml")) + sorted(spec_dir.glob("*.yml"))
    # dedupe while preserving order
    seen: set[Path] = set()
    out: list[Path] = []
    for f in files:
        rp = f.resolve()
        if rp in seen:
            continue
        seen.add(rp)
        out.append(f)
    if not out:
        raise GraphSpecError(f"no graph YAML files under {spec_dir}")
    return out


def load_specs(spec_dir: Path | None = None) -> list[GraphSpec]:
    root = Path(spec_dir) if spec_dir is not None else default_spec_dir()
    specs: list[GraphSpec] = []
    keys: MutableMapping[str, str] = {}
    for path in iter_spec_files(root):
        spec = load_spec_file(path)
        if spec.graph_key in keys:
            raise GraphSpecError(
                f"duplicate graph_key={spec.graph_key!r}: {keys[spec.graph_key]} and {path}"
            )
        # Optional: file stem should match graph_key for clarity
        if path.stem != spec.graph_key:
            SQLBotLogUtil.warning(
                f"graph spec file stem {path.stem!r} != graph_key {spec.graph_key!r} ({path})"
            )
        keys[spec.graph_key] = str(path)
        specs.append(spec)
    return specs


def make_builder(spec: GraphSpec) -> Callable[..., Any]:
    """Compile once at bootstrap and return a stable registry builder."""
    compiled = compile_graph(spec)

    def _builder(_ctx: Any = None, **_kwargs: Any) -> Any:
        return compiled

    _builder.__name__ = f"build_{spec.graph_key}_graph"
    _builder.__qualname__ = _builder.__name__
    _builder.__graph_spec__ = spec  # type: ignore[attr-defined]
    return _builder


def register_specs(specs: Iterable[GraphSpec], *, clear: bool = False) -> list[str]:
    """Register builders for each spec. Returns registered keys."""
    if clear:
        clear_registry()
    keys: list[str] = []
    for spec in specs:
        # make_builder compiles immediately, resolving every state/node/router
        # and validating LangGraph channel constraints exactly once.
        register_graph(spec.graph_key, make_builder(spec))
        keys.append(spec.graph_key)
    return keys


def bootstrap_graphs(
    spec_dir: Path | str | None = None, *, clear: bool = True
) -> list[str]:
    """Load topology YAML and register all product graphs.

    Idempotent when ``clear=True`` (default): clears registry first so reload
    in tests does not accumulate keys.
    """
    root = Path(spec_dir) if spec_dir is not None else default_spec_dir()
    specs = load_specs(root)
    keys = register_specs(specs, clear=clear)
    SQLBotLogUtil.info(f"bootstrap_graphs: loaded {keys} from {root}")
    return keys
