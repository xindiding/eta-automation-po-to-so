from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple


@dataclass(frozen=True)
class ParsedETD:
    """
    Result of parsing an ETD from a PO line comment.

    etd_date:
        - datetime if a real date exists
        - None if date is missing / not usable
        - the string "No ETD" is represented by is_no_etd=True
    note_added_date:
        Optional datetime inferred from bracket pattern like: "[12/12]"
    """
    etd_date: Optional[datetime]
    is_no_etd: bool
    note_added_date: Optional[datetime]


def _parse_note_added_date(first_line: str, default_year: int) -> Optional[datetime]:
    """
    Extract the first bracket date like [12/12] or [12-12] and convert to a date.
    """
    m = re.search(r"\[.*?(\d{1,2})[/-](\d{1,2})\]", first_line)
    if not m:
        return None
    d, mo = m.groups()
    return datetime.strptime(f"{int(d):02d}/{int(mo):02d}/{default_year}", "%d/%m/%Y")


def parse_etd_from_comment(
    comment: str | None,
    *,
    fallback_etd: Optional[datetime] = None,
    default_year: int = 2025,
) -> ParsedETD:
    """
    Portfolio-safe version of your logic:
    - Use first non-empty line in comment
    - If first line contains "No ETD" -> mark is_no_etd=True
    - Only use a date if the first cleaned line starts with a digit
    - Extract dd/mm/yyyy or dd/mm/yy
    - Return note_added_date if bracket date exists (e.g. [12/12])

    NOTE: This function is intentionally independent from any API or pandas.
    """
    if not comment or not str(comment).strip():
        return ParsedETD(etd_date=fallback_etd, is_no_etd=False, note_added_date=None)

    lines = [ln.strip() for ln in str(comment).splitlines() if ln.strip()]
    first_line = lines[0] if lines else ""
    note_added = _parse_note_added_date(first_line, default_year)

    # Remove tags like [API] or [12/12] from display parsing
    first_line_clean = re.sub(r"\[.*?\]", "", first_line).strip()

    # Handle "No ETD"
    if "no etd" in first_line_clean.lower():
        return ParsedETD(etd_date=None, is_no_etd=True, note_added_date=note_added)

    # If first clean line does not start with a digit, do not treat as a date line
    if not re.match(r"^\d", first_line_clean):
        return ParsedETD(etd_date=None, is_no_etd=False, note_added_date=note_added)

    # Date patterns: dd/mm/yyyy, dd-mm-yy, etc.
    m = re.search(r"(\d{1,2})[/-](\d{1,2})(?:[/-](\d{2,4}))", first_line_clean)
    if not m:
        return ParsedETD(etd_date=None, is_no_etd=False, note_added_date=note_added)

    day, month, year = m.groups()
    if year and len(year) == 2:
        year = f"20{year}"
    if not year:
        year = str(default_year)

    try:
        dt = datetime.strptime(f"{int(day):02d}/{int(month):02d}/{year}", "%d/%m/%Y")
        return ParsedETD(etd_date=dt, is_no_etd=False, note_added_date=note_added)
    except ValueError:
        return ParsedETD(etd_date=None, is_no_etd=False, note_added_date=note_added)
