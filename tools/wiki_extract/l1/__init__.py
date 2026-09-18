"""L1 wiki extract: coding-agent IR → catalog-checked draft pages.

Step 1 writes discrete YAML under ``_raw/l1_intermediate/``.
Step 2 loads those files, validates against L0 catalog, upgrades claims,
and emits the nine page types. Isolated from ``apps.knowledge.wiki``.
"""

from tools.wiki_extract.l1.reconcile import compile_l1

__all__ = ["compile_l1"]
