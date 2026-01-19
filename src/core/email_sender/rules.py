from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional

import pandas as pd


@dataclass(frozen=True)
class EmailDecision:
    should_send: bool
    reason: str  # normal / no_etd / long_etd / skip_*
    eta: Optional[pd.Timestamp]  # may be None for no_etd


def should_send_email_for_so(so_lines: pd.DataFrame) -> EmailDecision:
    """
    Demo-safe rules based on your real logic.
    Expects so_lines = all line rows for ONE sales order.

    Required columns (demo version):
      - Email
      - qtyOrdered
      - holdingQty
      - dispatchQty
      - ETD  (lineComments top line)
      - SO_EstimatedDelivery
      - SO_CreatedDate
    """
    if so_lines.empty:
        return EmailDecision(False, "skip_empty", None)

    # Rule: skip eBay
    if so_lines["Email"].astype(str).str.endswith("@members.ebay.com").any():
        return EmailDecision(False, "skip_ebay", None)

    # compute satisfied lines (fully dispatched or fully held)
    q_ordered = pd.to_numeric(so_lines["qtyOrdered"], errors="coerce").fillna(0)
    q_dispatched = pd.to_numeric(so_lines["dispatchQty"], errors="coerce").fillna(0)
    q_holding = pd.to_numeric(so_lines["holdingQty"], errors="coerce").fillna(0)

    line_satisfied = (q_dispatched >= q_ordered) | (q_holding >= q_ordered)
    if line_satisfied.all():
        return EmailDecision(False, "skip_all_satisfied", None)

    active_lines = so_lines[~line_satisfied].copy()

    # Rule: skip discontinued notes (line note starts with "dis")
    for _, r in active_lines.iterrows():
        note = str(r.get("ETD", "")).strip().lower()
        if note.startswith("dis"):
            return EmailDecision(False, "skip_discontinued", None)

    # SO-level ETD
    etd = active_lines["SO_EstimatedDelivery"].iloc[0]
    etd = pd.to_datetime(etd, errors="coerce")
    so_created = pd.to_datetime(active_lines["SO_CreatedDate"].iloc[0], errors="coerce")

    # if SO estimated delivery is in the past, skip
    today = pd.Timestamp.today().normalize()
    if pd.notna(etd) and etd < today:
        return EmailDecision(False, "skip_past_etd", None)

    # Check line note ETDs
    blank_etd = False
    has_no_etd = False
    note_dates: list[pd.Timestamp] = []

    for _, r in active_lines.iterrows():
        raw = str(r.get("ETD", "")).strip()
        low = raw.lower()

        if not raw:
            blank_etd = True
        elif low.startswith("no etd"):
            has_no_etd = True
        else:
            parsed = pd.to_datetime(raw, errors="coerce", dayfirst=True)
            if pd.notna(parsed):
                note_dates.append(parsed)
            else:
                blank_etd = True

    if blank_etd:
        return EmailDecision(False, "skip_blank_or_unparseable_line_etd", None)

    # Long ETD rule (4+ weeks between created and SO ETD)
    has_long_etd = False
    if pd.notna(etd) and pd.notna(so_created):
        has_long_etd = (etd - so_created).days > 28

    # Mixed no_etd + long_etd -> manual follow-up
    if has_no_etd and has_long_etd:
        return EmailDecision(False, "skip_mixed_etd_manual", etd)

    if has_no_etd:
        return EmailDecision(True, "no_etd", None)

    if has_long_etd:
        return EmailDecision(True, "long_etd", etd)

    return EmailDecision(True, "normal", etd)
