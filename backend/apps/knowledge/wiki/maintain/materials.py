"""Material registry: locator, toolset, and per-aspect trust.

The model never submits trust, sources, or evidence. New materials add a row
here and a read-only tool; they still enter the same propose, confirm, and
materialize path. Database, code, and SQL names are reserved and do not run.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

ASPECTS = ("structure", "enum_label", "relation", "business", "pattern")

# evidence prefixes the page contract accepts. Conversation locators are not
# among them; they stay on the patch source_ref and the page sources line.
EVIDENCE_PREFIXES = (
    "code_path:",
    "database_schema:",
    "database_profile:",
    "document_claim:",
)


@dataclass(frozen=True)
class MaterialSpec:
    kind: str
    toolset: str
    tools: tuple[str, ...]
    implemented: bool
    trust: dict[str, str]


def _trust(**levels: str) -> dict[str, str]:
    return {aspect: levels.get(aspect, "refuse") for aspect in ASPECTS}


REGISTRY: dict[str, MaterialSpec] = {
    "import": MaterialSpec(
        kind="import",
        toolset="import",
        tools=("import_file",),
        implemented=True,
        trust=_trust(
            structure="confirmed",
            enum_label="confirmed",
            relation="confirmed",
            business="confirmed",
            pattern="confirmed",
        ),
    ),
    "conversation": MaterialSpec(
        kind="conversation",
        toolset="conversation",
        tools=("read_source",),
        implemented=True,
        trust=_trust(
            enum_label="proposed",
            relation="proposed",
            business="proposed",
            pattern="proposed",
        ),
    ),
    "document": MaterialSpec(
        kind="document",
        toolset="document",
        tools=("read_source",),
        implemented=True,
        trust=_trust(
            enum_label="proposed",
            relation="proposed",
            business="confirmed",
            pattern="proposed",
        ),
    ),
    "wiki": MaterialSpec(
        kind="wiki",
        toolset="wiki",
        tools=("read_page", "search_pages", "recall_pages"),
        implemented=True,
        trust=_trust(
            enum_label="proposed",
            relation="proposed",
            business="proposed",
            pattern="proposed",
        ),
    ),
    "database_schema": MaterialSpec(
        kind="database_schema",
        toolset="database",
        tools=("read_schema",),
        implemented=False,
        trust=_trust(structure="confirmed", enum_label="proposed", relation="proposed"),
    ),
    "database_profile": MaterialSpec(
        kind="database_profile",
        toolset="database",
        tools=("read_profile",),
        implemented=False,
        trust=_trust(business="proposed"),
    ),
    "code": MaterialSpec(
        kind="code",
        toolset="code",
        tools=("read_code",),
        implemented=False,
        trust=_trust(
            structure="confirmed",
            enum_label="confirmed",
            relation="confirmed",
            business="proposed",
        ),
    ),
    "sql": MaterialSpec(
        kind="sql",
        toolset="sql",
        tools=("read_sql",),
        implemented=False,
        trust=_trust(pattern="proposed", business="proposed"),
    ),
}

_ORIGIN_KIND = {
    "import": "import",
    "conversation": "conversation",
    "document": "document",
    "maintain": "conversation",
    "wiki": "wiki",
}


def spec_for(kind: str) -> MaterialSpec:
    return REGISTRY.get(kind, REGISTRY["conversation"])


def kind_for_origin(origin: str) -> str:
    return _ORIGIN_KIND.get(origin, "conversation")


def cap_claim(kind: str, aspect: str, requested: str) -> str:
    """Return the trust this material may stamp, or ``refuse``."""
    ceiling = spec_for(kind).trust.get(aspect, "refuse")
    if ceiling == "refuse":
        return "refuse"
    if ceiling == "proposed":
        return "proposed"
    if requested in {"confirmed", "proposed", "disputed", "rejected"}:
        return requested
    return "proposed"


def conversation_locator(chat_id: int, record_id: int) -> str:
    return f"conversation:{chat_id}/{record_id}"


def document_locator(source_id: int) -> str:
    return f"document:{source_id}"


def wiki_locator(corpus_key: str, belong: str, page_key: str) -> str:
    return f"wiki:{corpus_key}/{belong}/{page_key}"


def content_sha(body: str) -> str:
    return hashlib.sha256(body.encode("utf-8")).hexdigest()
