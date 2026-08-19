"""Authoritative semantic knowledge layer.

Runtime K1-K5 assets are projections of approved unit revisions.  They are not
edited through this package.
"""

from apps.knowledge.compile.bundle import BusinessDataBundle
from apps.knowledge.semantic.schema import KnowledgePackageV2

__all__ = ["BusinessDataBundle", "KnowledgePackageV2"]
