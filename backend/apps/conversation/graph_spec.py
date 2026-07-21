"""Graph topology spec — parse + validate YAML declarations.

YAML is the sole topology truth source. Node/router bodies remain Python
callables resolved by dotted path.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Union


class GraphSpecError(ValueError):
    """Invalid graph topology document or unresolvable reference."""


@dataclass(frozen=True)
class OkOrFailRouter:
    next: str


RouterRef = Union[str, OkOrFailRouter]


@dataclass(frozen=True)
class PlainEdge:
    source: str
    target: str


@dataclass(frozen=True)
class ConditionalEdge:
    source: str
    router: RouterRef
    paths: Dict[str, str]


@dataclass(frozen=True)
class GraphSpec:
    version: int
    graph_key: str
    state: str
    nodes: Dict[str, str]
    edges: List[Union[PlainEdge, ConditionalEdge]] = field(default_factory=list)
    description: str = ""
    source_path: Optional[str] = None

    def node_names(self) -> set[str]:
        return set(self.nodes.keys())


def _require_mapping(raw: Any, loc: str) -> Mapping[str, Any]:
    if not isinstance(raw, Mapping):
        raise GraphSpecError(f"{loc} must be a mapping")
    return raw


def _parse_router(raw: Any, loc: str) -> RouterRef:
    if isinstance(raw, str):
        path = raw.strip()
        if not path:
            raise GraphSpecError(f"{loc}: empty router path")
        return path
    if isinstance(raw, Mapping):
        rtype = str(raw.get("type") or "").strip()
        if rtype == "ok_or_fail":
            nxt = str(raw.get("next") or "").strip()
            if not nxt:
                raise GraphSpecError(f"{loc}: ok_or_fail requires next")
            return OkOrFailRouter(next=nxt)
        raise GraphSpecError(f"{loc}: unknown router type={rtype!r}")
    raise GraphSpecError(f"{loc}: router must be dotted path or {{type, ...}}")


def parse_graph_spec(raw: Any, *, source_path: str | None = None) -> GraphSpec:
    """Parse a loaded YAML/JSON mapping into a validated ``GraphSpec``."""
    data = _require_mapping(raw, "root")
    version = data.get("version", 1)
    if not isinstance(version, int):
        raise GraphSpecError(f"{source_path or 'spec'}: version must be int")
    if version != 1:
        raise GraphSpecError(f"{source_path or 'spec'}: unsupported version {version}")

    graph_key = str(data.get("graph_key") or "").strip()
    if not graph_key:
        raise GraphSpecError(f"{source_path or 'spec'}: graph_key is required")

    state = str(data.get("state") or "").strip()
    if not state:
        raise GraphSpecError(f"{source_path or 'spec'}: state dotted path is required")

    nodes_raw = data.get("nodes")
    if not isinstance(nodes_raw, Mapping) or not nodes_raw:
        raise GraphSpecError(f"{source_path or 'spec'}: nodes map is required")
    nodes: Dict[str, str] = {}
    for name, path in nodes_raw.items():
        n = str(name).strip()
        p = str(path).strip()
        if not n or not p:
            raise GraphSpecError(f"{source_path or 'spec'}: invalid node entry {name!r}")
        if n in ("START", "END"):
            raise GraphSpecError(f"{source_path or 'spec'}: node name {n!r} is reserved")
        nodes[n] = p

    edges_raw = data.get("edges")
    if not isinstance(edges_raw, list) or not edges_raw:
        raise GraphSpecError(f"{source_path or 'spec'}: edges list is required")

    edges: List[Union[PlainEdge, ConditionalEdge]] = []
    known = set(nodes.keys()) | {"START", "END"}

    for i, item in enumerate(edges_raw):
        loc = f"{source_path or 'spec'}.edges[{i}]"
        edge = _require_mapping(item, loc)
        src = str(edge.get("from") or "").strip()
        if not src:
            raise GraphSpecError(f"{loc}: from is required")
        if src not in known and src != "START":
            # START always allowed; other sources must be declared nodes
            if src not in nodes and src != "START":
                raise GraphSpecError(f"{loc}: unknown from={src!r}")

        if "router" in edge:
            if "to" in edge:
                raise GraphSpecError(f"{loc}: conditional edge cannot set to")
            paths_raw = edge.get("paths")
            if not isinstance(paths_raw, Mapping) or not paths_raw:
                raise GraphSpecError(f"{loc}: paths map is required for conditional edge")
            paths: Dict[str, str] = {}
            for k, v in paths_raw.items():
                pk = str(k).strip()
                pv = str(v).strip()
                if not pk or not pv:
                    raise GraphSpecError(f"{loc}: invalid paths entry")
                if pv not in nodes and pv != "END":
                    raise GraphSpecError(f"{loc}: paths[{pk!r}] unknown target {pv!r}")
                paths[pk] = pv
            router = _parse_router(edge.get("router"), f"{loc}.router")
            if isinstance(router, OkOrFailRouter):
                if router.next not in paths:
                    raise GraphSpecError(
                        f"{loc}: ok_or_fail next={router.next!r} missing from paths"
                    )
                if "fail" not in paths:
                    raise GraphSpecError(f"{loc}: ok_or_fail paths must include fail")
            edges.append(ConditionalEdge(source=src, router=router, paths=paths))
        else:
            dst = str(edge.get("to") or "").strip()
            if not dst:
                raise GraphSpecError(f"{loc}: to is required for plain edge")
            if dst not in nodes and dst != "END":
                raise GraphSpecError(f"{loc}: unknown to={dst!r}")
            if src not in nodes and src != "START":
                raise GraphSpecError(f"{loc}: unknown from={src!r}")
            edges.append(PlainEdge(source=src, target=dst))

    # Every node should be reachable as a target or START-adjacent — soft check:
    # require at least one edge from START.
    if not any(
        (isinstance(e, PlainEdge) and e.source == "START")
        or (isinstance(e, ConditionalEdge) and e.source == "START")
        for e in edges
    ):
        raise GraphSpecError(f"{source_path or 'spec'}: missing edge from START")

    description = str(data.get("description") or "")
    return GraphSpec(
        version=version,
        graph_key=graph_key,
        state=state,
        nodes=nodes,
        edges=edges,
        description=description,
        source_path=source_path,
    )
