# Business Rules Summary (Anonymised)

## PO → SO ETA Allocation
- Parse ETD from PO line comments (first non-empty line).
- If comment contains "No ETD", mark as No ETD.
- Only parse dates when the first cleaned line begins with a digit.
- Allocate PO remaining quantity to SO outstanding quantity by SKU.
- Dropship binding: if PO internal comment contains DS-<SO>, bind to that SO and prevent PO reuse.
- Final ETA logic:
  - If any contributing PO line is explicit "No ETD", SO note becomes "No ETD - <most recent note-added date>".
  - Otherwise, latest real ETA among contributing POs + 1 day, push to Monday if weekend.
- Only update SO lines where (qty - holdingQty) > 0.
- Note constraints: insert ETA at top line, de-duplicate, enforce soft/hard length limits.

## Customer ETA Notification (Events)
- Skip eBay customers.
- Skip orders where all items are fully dispatched or fully held.
- Skip if any active line item is marked discontinued.
- Skip if any active line has blank / invalid ETD.
- Classify into:
  - normal
  - no_etd
  - long_etd (created → estimated delivery > 28 days)
  - mixed (no_etd + long_etd) → manual follow-up
