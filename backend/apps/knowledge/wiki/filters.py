"""Extraction filters: shared white/blacklist gates (plan §0.2).

Two filter families, one implementation each — every consumer (Step A entry
enumeration, Step B callgraph scan, Step D file reads, E0.5 reqdoc candidate
pool) goes through the same function so exclusion policy can never drift
between pipeline stages (杜绝同口径重复实现).

* ``CodeIgnore`` — repo-side glob filter, gitignore-like: patterns are
  repo-rooted, ``!`` prefix negates (last match wins), ``default_excludes``
  layers the built-in set (build/test/generated/docs).
* ``ReqdocFilter`` — Test-wiki side; supports ``include_only`` (whitelist
  mode, default — more reliable than enumerating noise) or ``exclude``.

Both load from YAML files under ``substrate/tmp/``; Step A proposes entries,
humans curate, the files are the single source of truth.
"""

from __future__ import annotations

import fnmatch
from pathlib import Path

import yaml

# Built-in logic-irrelevant paths for a Java multi-module repo (layered under
# user patterns when default_excludes is on).
_DEFAULT_CODE_EXCLUDES = (
    "*/target/*",
    "*/build/*",
    "*/node_modules/*",
    "*/src/test/*",
    "*/src/test-rescue/*",
    "*/gen/*",
    "*/generated/*",
    "*/.git/*",
    "*/resources/static/*",
    "*/resources/templates/*",
    "*/.dev-standards/*",
    "*/docs/*",
    "*/doc/*",
)


class CodeIgnore:
    """Repo-side ignore list (gitignore-like, last-match-wins with ``!``)."""

    def __init__(self, patterns: list[str], *, default_excludes: bool = True) -> None:
        self.patterns = [
            p for p in patterns if p and not p.startswith("#") and not p.startswith("!")
        ]
        self.negations = [p[1:] for p in patterns if p.startswith("!")]
        base = _DEFAULT_CODE_EXCLUDES if default_excludes else ()
        self._all = tuple(self.patterns) + base

    @classmethod
    def load(cls, path: Path) -> CodeIgnore:
        if not path.exists():
            return cls([])
        data = yaml.safe_load(path.read_text()) or {}
        patterns = data.get("exclude") or []
        if isinstance(patterns, str):
            patterns = [patterns]
        return cls(patterns, default_excludes=bool(data.get("default_excludes", True)))

    def should_scan(self, path: str | Path) -> bool:
        rel = path.as_posix() if isinstance(path, Path) else path
        rel = rel.lstrip("/")
        excluded = any(
            fnmatch.fnmatch(rel, pat) or fnmatch.fnmatch(f"/{rel}", pat)
            for pat in self._all
        )
        if excluded and any(
            fnmatch.fnmatch(rel, neg) or fnmatch.fnmatch(f"/{rel}", neg)
            for neg in self.negations
        ):
            return True  # last-match-wins: negation re-includes
        return not excluded


class ReqdocFilter:
    """Test-wiki page filter — include_only whitelist by default."""

    def __init__(
        self,
        *,
        include_only: tuple[str, ...] = (),
        exclude: tuple[str, ...] = (),
    ) -> None:
        self.include_only = include_only
        self.exclude = exclude

    @classmethod
    def load(cls, path: Path) -> ReqdocFilter:
        if not path.exists():
            # 默认策略（无配置文件时）：type 白名单 + 明显噪声后缀黑名单，
            # 项目专属 slug 由 reqdoc-filter.yaml 维护（单一事实源）。
            return cls(
                include_only=(
                    "concepts/**",
                    "entities/*表.md",
                    "entities/sso*.md",
                ),
                exclude=(
                    "entities/余*.md",
                    "entities/*公司.md",
                    "queries/*",
                    "findings/*",
                    "sources/*",
                ),
            )
        data = yaml.safe_load(path.read_text()) or {}
        inc = tuple(data.get("include_only") or ())
        exc = tuple(data.get("exclude") or ())
        return cls(include_only=inc, exclude=exc)

    def should_use(self, rel_path: str) -> bool:
        rel = rel_path.lstrip("/")
        if self.include_only:
            if not any(fnmatch.fnmatch(rel, pat) for pat in self.include_only):
                return False
        if self.exclude and any(fnmatch.fnmatch(rel, pat) for pat in self.exclude):
            return False
        return True

    def iter_pages(self, wiki_root: Path) -> list[Path]:
        """Filtered page list under a Test-wiki project (wiki/ directory)."""
        return [
            p
            for p in sorted(wiki_root.rglob("*.md"))
            if not p.name.startswith("_")
            and self.should_use(str(p.relative_to(wiki_root)))
        ]
