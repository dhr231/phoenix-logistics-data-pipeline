# Phoenix Logistics Data Pipeline

## Project Overview

A Python-based logistics data pipeline that processes Booking and Billing datasets, normalizes LR numbers, performs reconciliation, generates exception reports, and validates invoice-level financial totals.

## Technology Stack

- Python
- Pandas
- OpenPyXL
- CSV and Excel data processing
- Git and GitHub

## Setup

**Prerequisites:** Python installed on your system.

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the pipeline from the project directory:

```bash
python load_logistics_data.py
```

## Pipeline Workflow

1. Load the Booking and Billing datasets.
2. Inspect and normalize LR identifiers.
3. Expand multi-LR billing records into LR-level detail.
4. Reconcile Booking and Billing records.
5. Generate master reconciliation and exception reports.
6. Preserve invoice-level financial totals separately.
7. Run validation checks and audit the generated CSV files.

## Key Engineering Decisions

- Preserve invoice-level financial values separately from exploded LR-level records.
- Avoid summing repeated invoice amounts across LR-level rows.
- Validate invoice counts, unique billing record IDs, financial totals, LR keys, and reconciliation statuses.
- Report unmatched records instead of forcing an unreliable join.

## Current Limitation

The supplied datasets currently have zero common LR numbers. The pipeline reports unmatched records, but successful Booking–Billing matching has not yet been demonstrated against overlapping source data.

## Generated Outputs

- `master_reconciliation.csv`
- `billing_financials.csv`
- `reconciliation_report.csv`
- `data_quality_report.csv`
- `exception_summary.csv`



## Pipeline Validation and Outputs

# Phoenix Logistics Data Pipeline

## Project Overview

A Python and Pandas pipeline for logistics Booking and Billing
data normalization, LR-level reconciliation, exception reporting,
and invoice-level financial validation.

## Architecture

Booking Source ──> LR Normalization ──┐
                                     ├──> Master Reconciliation
Billing Source ──> LR Expansion ─────┘          |
                                                v
                                     Reconciliation Statuses
                                                |
                         ┌──────────────────────┴─────────────┐
                         v                                    v
                Quality Reports                     Financial Output

## Technology Stack

- Python
- Pandas
- CSV and Excel data processing
- Git and GitHub

## Setup and Execution

1. Clone this repository.
2. Create and activate a Python virtual environment.
3. Install dependencies:

   pip install -r requirements.txt

4. Run the pipeline:

   python load_logistics_data.py

5. Review the generated CSV reports.


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
