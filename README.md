## Pipeline Validation and Outputs

### Overview

This project processes logistics Booking and Billing data, normalizes LR numbers, performs reconciliation, and generates data-quality and financial outputs.

### Key Outputs

| Output file | Purpose |
|---|---|
| `master_reconciliation.csv` | Booking and Billing LR-level reconciliation with status |
| `billing_financials.csv` | Invoice-level financial records with original billing amounts |
| `reconciliation_report.csv` | High-level reconciliation metrics |
| `data_quality_report.csv` | Individual data-quality exceptions |
| `exception_summary.csv` | Aggregated exception counts |

### Data Integrity

The pipeline validates:
- Invoice-level row counts and unique billing record IDs.
- Preservation of the source-to-output financial total.
- Missing or blank LR keys.
- Valid reconciliation statuses.
- Expected master output row counts for the current zero-overlap dataset.

### Current Dataset Limitation

The current Booking dataset contains 7 valid LR records, while the Billing dataset expands from 16 original rows to 78 LR-level rows.

The current datasets have zero common LR numbers. The generated reconciliation therefore contains:
- 78 `BILLING_ONLY` rows
- 7 `BOOKING_ONLY` rows
- 0 `MATCHED` rows

These results describe the supplied datasets; they do not establish that the reconciliation logic has been validated against successful real-world matches.

### Financial Grain

Invoice-level financial values are preserved separately from exploded LR-level details. A billing amount must not be summed across exploded LR rows because the same invoice amount can repeat for multiple LRs.

LR-level amount allocation requires a verified business rule or reliable LR-level financial data.
