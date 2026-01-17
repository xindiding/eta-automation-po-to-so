# eta-automation-po-to-so
Automates allocation of Purchase Orders to Sales Orders with ETA logic, status updates, and customer notifications.

## Business Problem
In retail and e-commerce operations, Purchase Orders (POs) and Sales Orders (SOs) are often managed in separate systems.
This creates manual work, delays, and inconsistencies when allocating incoming stock, updating ETAs, and informing customers.

This project automates the process of linking open Purchase Orders to open Sales Orders based on business rules, improving operational efficiency and data accuracy.

---

## What This Project Does
- Automatically matches open POs to open SOs using SKU and date logic
- Allocates ETAs from PO lines to corresponding SOs
- Updates order notes and statuses in downstream systems
- Triggers customer notifications when ETAs change
- Handles edge cases such as missing ETAs, partial allocations, and multiple suppliers

---

## Why It Matters
Without automation:
- ETA updates are manual and error-prone
- Customers receive late or inconsistent information
- Operations teams spend hours reconciling orders
- Data across systems becomes unreliable

This automation reduces manual intervention, improves customer communication, and creates a more reliable order management workflow.

---

## High-Level Workflow
1. Retrieve open Purchase Orders and Sales Orders
2. Apply matching rules (SKU, creation date, availability)
3. Allocate ETA from PO to SO
4. Update SO notes and status
5. Log changes and exceptions for auditing

---

## Design Decisions & Trade-offs
- Business rules are prioritised over perfect matching to reflect real operational constraints
- Edge cases are logged instead of failing the entire process
- The system is designed to be extendable for new rules and suppliers

---

## Tech Stack
- Python
- Pandas
- API integrations (structure anonymised)
- Logging & rule-based processing

---

## Notes on Data & Privacy
All data in this repository is anonymised or simulated.
No real customer, supplier, or system credentials are included.

---

## Possible Future Improvements
- Add unit tests for matching logic
- Introduce retry handling for API failures
- Add monitoring and alerting for exceptions
