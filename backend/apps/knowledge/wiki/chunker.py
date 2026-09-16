"""Heading-aware markdown chunking with atomic fenced/ground blocks.

Ported from llm-wiki page_embedding.rs::chunk_markdown (verified source):
heading stack → per-chunk ``heading_path``; fenced blocks — including v0
```` ```ground: ```` anchor fences — are atomic and never split.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_FENCE_RE = re.compile(r"^\s*(```|~~~)")
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")

# 嵌入 API 常见上限 8192 tokens；CJK 约 1 token/字。单块硬顶 + 请求侧按
# token 打包，避免整批 input 合计超限。
_TARGET_CHARS = 600
_MAX_CHUNK_CHARS = 1800
_OVERLAP_CHARS = 80


@dataclass(frozen=True)
class Chunk:
    text: str
    heading_path: str
    recall: bool = True


_NORECALL_HEADINGS = frozenset(
    {
        "展示",
        "版本演进",
        "版本说明",
        "给人看",
        "本期说明",
        "排期",
        "不召回",
    }
)
_DISPLAY_FENCE_INFO = frozenset(
    {"wiki:display", "display", "wiki:norecall", "norecall"}
)


def body_recall_flag(body: str) -> bool:
    """Frontmatter ``recall: false`` disables the whole page for embeddings."""
    if not body.lstrip().startswith("---"):
        return True
    start = body.find("---")
    end = body.find("\n---", start + 3)
    if end < 0:
        return True
    for line in body[start + 3 : end].splitlines():
        stripped = line.strip()
        if stripped.startswith("recall:"):
            value = stripped.split(":", 1)[1].strip().lower()
            return value not in {"false", "no", "0", "off"}
    return True


def _is_norecall_heading(title: str) -> bool:
    text = title.strip()
    if "不召回" in text:
        return True
    head = text.split("（", 1)[0].split("(", 1)[0].strip()
    return head in _NORECALL_HEADINGS


def _is_display_fence(open_line: str) -> bool:
    rest = open_line.strip().lstrip("`~").strip().lower()
    info = rest.split()[0] if rest else ""
    return info in _DISPLAY_FENCE_INFO


def _explode_long_lines(lines: list[str]) -> list[str]:
    """A single YAML/prose line can exceed the embed context by itself."""
    exploded: list[str] = []
    for line in lines:
        if len(line) <= _MAX_CHUNK_CHARS:
            exploded.append(line)
            continue
        for start in range(0, len(line), _MAX_CHUNK_CHARS):
            exploded.append(line[start : start + _MAX_CHUNK_CHARS])
    return exploded


def _split_with_overlap(lines: list[str]) -> list[str]:
    """Window long prose by characters with a trailing-overlap echo."""
    pieces: list[str] = []
    buffer: list[str] = []
    size = 0
    for line in _explode_long_lines(lines):
        buffer.append(line)
        size += len(line) + 1
        if size >= _TARGET_CHARS:
            pieces.append("\n".join(buffer))
            tail: list[str] = []
            tail_size = 0
            for prev in reversed(buffer[:-1]):
                tail.insert(0, prev)
                tail_size += len(prev) + 1
                if tail_size >= _OVERLAP_CHARS:
                    break
            buffer = list(tail)
            size = tail_size
    if buffer:
        text = "\n".join(buffer).strip()
        if text and (not pieces or text != pieces[-1]):
            pieces.append(text)
    return pieces


def _split_long_fence(
    atomic: list[str],
    _fence_open: str,
    heading_path: str,
    *,
    recall: bool = True,
) -> list[Chunk]:
    """llm-wiki ``split_preserving_atomic_blocks``：围栏块超长时内部按行窗口
    再切，每子块保持围栏开/闭配对（渲染仍是合法 ground 块，召回粒度变小）。"""
    total = sum(len(line) + 1 for line in atomic)
    if total <= _MAX_CHUNK_CHARS:
        return [
            Chunk(text="\n".join(atomic), heading_path=heading_path, recall=recall)
        ]
    opener, closer = atomic[0], atomic[-1]
    inner = _explode_long_lines(atomic[1:-1])
    chunks: list[Chunk] = []
    buffer: list[str] = []
    size = 0
    for line in inner:
        buffer.append(line)
        size += len(line) + 1
        if size >= _TARGET_CHARS:
            chunks.append(
                Chunk(
                    text="\n".join([opener, *buffer, closer]),
                    heading_path=heading_path,
                    recall=recall,
                )
            )
            buffer.clear()
            size = 0
    if buffer:
        chunks.append(
            Chunk(
                text="\n".join([opener, *buffer, closer]),
                heading_path=heading_path,
                recall=recall,
            )
        )
    return chunks


def chunk_markdown(body: str) -> list[Chunk]:
    """Split page body into chunks; fenced/ground regions stay atomic.

    ``recall=False`` chunks are for human display only: they must not be
    embedded or used in lexical/vector recall. Triggers: page frontmatter
    ``recall: false``; headings in the display-zone set (and their children);
    fences ``wiki:display`` / ``display``.
    """
    page_recall = body_recall_flag(body)
    chunks: list[Chunk] = []
    heading_stack: list[tuple[int, str]] = []
    section: list[str] = []
    norecall_from: int | None = None

    def heading_path() -> str:
        return " > ".join(f"{'#' * level} {title}" for level, title in heading_stack)

    def region_recall() -> bool:
        return page_recall and norecall_from is None

    def flush_prose() -> None:
        text = "\n".join(section).strip()
        section.clear()
        if not text:
            return
        flag = region_recall()
        for piece in _split_with_overlap(text.splitlines()):
            chunks.append(
                Chunk(text=piece, heading_path=heading_path(), recall=flag)
            )

    in_fence = False
    fence_open = ""
    atomic: list[str] = []
    for line in body.splitlines():
        if in_fence:
            atomic.append(line)
            if _FENCE_RE.match(line):
                in_fence = False
                fence_recall = region_recall() and not _is_display_fence(fence_open)
                chunks.extend(
                    _split_long_fence(
                        atomic,
                        fence_open,
                        heading_path(),
                        recall=fence_recall,
                    )
                )
                atomic.clear()
            continue
        if _FENCE_RE.match(line):
            flush_prose()
            in_fence = True
            atomic = [line]
            fence_open = line
            continue
        heading = _HEADING_RE.match(line)
        if heading:
            flush_prose()
            level = len(heading.group(1))
            title = heading.group(2).strip()
            while heading_stack and heading_stack[-1][0] >= level:
                heading_stack.pop()
            if norecall_from is not None and level <= norecall_from:
                norecall_from = None
            heading_stack.append((level, title))
            if _is_norecall_heading(title):
                norecall_from = level
            chunks.append(
                Chunk(
                    text=line,
                    heading_path=heading_path(),
                    recall=region_recall(),
                )
            )
            continue
        section.append(line)
    if in_fence:  # unterminated atomic block — keep whole
        fence_recall = region_recall() and not _is_display_fence(fence_open)
        chunks.append(
            Chunk(
                text="\n".join(atomic),
                heading_path=heading_path(),
                recall=fence_recall,
            )
        )
    flush_prose()
    return chunks
