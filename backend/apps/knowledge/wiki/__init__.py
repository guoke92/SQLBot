"""Wiki knowledge subsystem (prototype, spec: docs/wiki-knowledge/).

Independent of the legacy unit knowledge system; switches in at the recall
boundary (`KNOWLEDGE_BACKEND=wiki`). Modules:

- ``contract`` — page parsing/validation/lint (Spec A)
- ``chunker`` — heading-aware chunking with atomic ground blocks
- ``graph``   — wikilink adjacency + alias resolution
- ``recall``  — RRF fusion + page aggregation + graph-expansion quota (Spec C)
"""
