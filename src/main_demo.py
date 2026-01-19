import pandas as pd

def run():
    df_po = pd.read_csv("data/sample_pos.csv")
    df_so = pd.read_csv("data/sample_sos.csv")

    # TODO: implement:
    # 1) parse ETD from etd_note
    # 2) compute remaining qty
    # 3) allocate PO -> SO by sku
    # 4) build SO line notes (top line ETA + keep old note)
    # 5) print "updates" as demo output

    print("PO rows:", len(df_po))
    print("SO rows:", len(df_so))
    print("Demo run complete (no external APIs used).")

if __name__ == "__main__":
    run()
