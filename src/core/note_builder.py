from __future__ import annotations

import re
from typing import List


def _norm_lines(s: str) -> List[str]:
    s = (s or "")
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    return [re.sub(r"\s+", " ", ln).strip() for ln in s.split("\n") if ln.strip()]


def insert_top_line_with_limits(
    existing_note: str,
    new_top_line: str,
    *,
    soft_limit: int = 230,
    hard_limit: int = 256,
) -> str:
    """
    Insert a new top line into an existing note with:
    - case-insensitive de-duplication of the top line
    - soft limit: drop from bottom until <= soft_limit
    - hard limit: absolute maximum length

    This is a portfolio-safe extraction of your Cin7 note constraints logic.
    """
    old_lines = _norm_lines(existing_note)
    top = re.sub(r"\s+", " ", (new_top_line or "").strip())
    if not top:
        return "\n".join(old_lines)

    # remove duplicates of the same line (case-insensitive)
    old_lines = [ln for ln in old_lines if ln.lower() != top.lower()]
    lines = [top] + old_lines

    # defensive trimming if a single line is too long
    if len(lines[0]) > hard_limit:
        lines[0] = lines[0][: hard_limit - 1] + "…"

    def joined(ls: List[str]) -> str:
        return "\n".join(ls)

    # soft limit trimming: drop from bottom
    while len(joined(lines)) > soft_limit and len(lines) > 1:
        lines.pop()

    note = joined(lines)

    # hard limit guard (rare if soft < hard)
    while len(note) > hard_limit and len(lines) > 1:
        lines.pop()
        note = joined(lines)

    if len(note) > hard_limit:
        note = note[: hard_limit - 1] + "…"

    return note
