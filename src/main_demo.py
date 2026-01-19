"""
Demo runner for PO → SO ETA logic and email decision rules.

"""

import pandas as pd

# ---- import your own modules ----
from core.etd_parser import parse_etd_from_comment
from core.note_builder import insert_top_line_with_limits
from email_sender.rules import should_send_email_for_so


def run_demo():
    print("=== DEMO START ===\n")

    # ----------------------------
    # 1. Load demo data
    # ----------------------------
    df_po = pd.read_csv("data/sample_pos.csv")
    df_so = pd.read_csv("data/sample_sos.csv")

    print(f"Loaded {len(df_po)} PO lines")
    print(f"Loaded {len(df_so)} SO lines\n")

    # ----------------------------
    # 2. Parse ETD from PO notes
    # ----------------------------
    print("Step 1: Parse ETD from PO comments\n")

    df_po["parsed"] = df_po["etd_note"].apply(
        lambda x: parse_etd_from_comment(x)
    )

    df_po["parsed_etd"] = df_po["parsed"].apply(
        lambda x: x.etd_date.strftime("%d/%m/%Y") if x.etd_date else None
    )
    df_po["is_no_etd"] = df_po["parsed"].apply(lambda x: x.is_no_etd)

    print(df_po[["po_id", "sku", "etd_note", "parsed_etd", "is_no_etd"]])
    print("\n")

    # ----------------------------
    # 3. Build SO line notes (demo)
    # ----------------------------
    print("Step 2: Build SO line notes\n")

    # Fake example: apply first PO ETD to all SOs with same SKU
    sku_to_etd = (
        df_po.dropna(subset=["parsed_etd"])
        .groupby("sku")["parsed_etd"]
        .first()
        .to_dict()
    )

    def build_note(row):
        existing = row.get("line_note", "")
        etd = sku_to_etd.get(row["sku"])
        if not etd:
            return existing
        return insert_top_line_with_limits(existing, etd)

    df_so["new_note"] = df_so.apply(build_note, axis=1)

    print(df_so[["so_id", "sku", "line_note", "new_note"]])
    print("\n")

    # ----------------------------
    # 4. Email decision demo
    # ----------------------------
    print("Step 3: Email decision rules\n")

    # Add required columns for email rules
    df_so["qtyOrdered"] = df_so["qty"]
    df_so["holdingQty"] = 0
    df_so["dispatchQty"] = 0
    df_so["ETD"] = df_so["new_note"]
    df_so["SO_EstimatedDelivery"] = pd.to_datetime("2026-01-25")
    df_so["SO_CreatedDate"] = pd.to_datetime("2025-12-01")

    for so_id, group in df_so.groupby("so_id"):
        decision = should_send_email_for_so(group)
        print(
            f"SO {so_id} → "
            f"send={decision.should_send}, "
            f"reason={decision.reason}, "
            f"eta={decision.eta}"
        )

    print("\n=== DEMO END ===")


if __name__ == "__main__":
    run_demo()
