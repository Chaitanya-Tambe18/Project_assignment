# Distilled Prompt

## Objective

Build a production-style Python reconciliation system for a payments company.

The system should compare:

- platform transactions
- bank settlement records

and explain why reconciliation mismatches occur.

---

## Core Requirements

### Synthetic Data

Generate:

1. transactions dataset
2. settlement dataset

Requirements:

- 150–250 records
- realistic timestamps
- settlement delay of 1–2 days
- mostly successful reconciliation

---

### Inject Required Anomalies

Mandatory:

#### Cross-Month Settlement

Example:

Jan 31 transaction

→ Feb 2 settlement

Category:

`cross_month_timing_issue`

---

#### Aggregate Rounding Difference

Tiny decimal precision mismatches.

Visible only after summation.

Category:

`aggregate_rounding_difference`

---

#### Duplicate Settlement

Duplicate one settlement record.

Category:

`duplicate_entry`

---

#### Refund Without Original Transaction

Refund references missing transaction.

Category:

`orphan_refund`

---

## Reconciliation Engine

Detect:

- matched
- missing settlements
- duplicate entries
- orphan refunds
- cross-month timing issues
- rounding discrepancies

Each anomaly must include:

- reason
- impact
- recommendation

---

## Output Requirements

Generate:

### Reports

- TXT report
- Excel report

### Charts

- anomaly distribution
- matched vs unmatched
- settlement timing
- reconciliation summary

---

## Engineering Requirements

Use:

- pandas
- numpy
- matplotlib
- pytest

Include:

- modular architecture
- logging
- reusable functions
- clean code
- type hints
- documentation

---

## Execution

Run end-to-end via:

```bash
python src/main.py
```

Expected flow:

1. generate data
2. reconcile
3. detect anomalies
4. generate reports
5. generate charts
6. print summary