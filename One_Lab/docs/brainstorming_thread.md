# Brainstorming Thread — Payments Reconciliation & Anomaly Detection System

## Problem Understanding

The business problem is that:

A payments platform records transactions immediately when a customer pays, while banks settle payments later (typically 1–2 days). At month-end, finance teams expect platform transactions and bank settlements to reconcile.

However, mismatches occur.

Goal:

Identify:

- which records match
- which do not
- why reconciliation failed
- whether the mismatch is operational or expected

---

## Initial Thinking

The first idea was:

Perform a simple transaction_id join between:

1. Platform transactions
2. Bank settlements

However, this approach immediately appeared insufficient.

Why?

Because reconciliation mismatches are not always failures.

Example:

A payment processed on:

2026-01-31

may settle on:

2026-02-02

This should NOT be classified as missing.

Instead:

Category:

`cross_month_timing_issue`

Meaning:

Expected settlement delay caused reporting mismatch.

---

## Required Gap Types Analysis

The assessment explicitly requested injected reconciliation failures.

We identified four mandatory anomaly categories.

### 1. Cross-Month Settlement

Scenario:

Transaction happens in January.

Settlement happens in February.

Example:

| Transaction Date | Settlement Date |
|-----------------|-----------------|
| 2026-01-31 | 2026-02-02 |

Observation:

This is not operational failure.

Decision:

Treat as:

`cross_month_timing_issue`

instead of:

`missing_settlement`

Business impact:

Month-end reporting mismatch.

Recommendation:

Carry-forward reconciliation logic.

---

### 2. Aggregate Rounding Difference

Observation:

Small decimal mismatches happen in financial systems.

Example:

Platform:

10000.005

Settlement:

10000.00

At row level:

Looks correct.

At total level:

Differences emerge.

Decision:

Inject tiny decimal precision inconsistencies that only appear when totals are aggregated.

Business impact:

Finance books slightly out of balance.

Recommendation:

Tolerance threshold or precision normalization.

---

### 3. Duplicate Settlement

Observation:

Sometimes settlement records duplicate due to:

- retries
- ingestion issues
- batch replay
- bookkeeping errors

Decision:

Duplicate a settlement entry.

Example:

Same `transaction_id` appears twice.

Expected category:

`duplicate_entry`

Business impact:

Double counting risk.

Recommendation:

Deduplicate settlement records.

---

### 4. Orphan Refund

Observation:

Refunds should reference a valid transaction.

Failure scenario:

Refund references non-existent payment.

Example:

original_transaction_id = TXN999999

Decision:

Inject refund mismatch.

Expected category:

`orphan_refund`

Business impact:

Broken accounting lineage.

Recommendation:

Investigate data integrity.

---

## Data Modeling Decisions

Transactions dataset:

Chosen fields:

- transaction_id
- customer_id
- transaction_date
- amount
- currency
- type
- original_transaction_id
- status

Reason:

Enough fields to simulate realistic payment workflows.

---

Settlements dataset:

Chosen fields:

- settlement_id
- transaction_id
- settlement_date
- settled_amount
- settlement_status
- bank_reference

Reason:

Reflects how settlement systems usually track bank reconciliation.

---

## Design Decisions

### Why Synthetic Data?

Assessment explicitly required:

No external files.

Therefore:

Synthetic generation was implemented.

Advantages:

- reproducibility
- anomaly injection control
- deterministic testing

---

### Why Modular Architecture?

Instead of one script:

Separated concerns:

- data generation
- reconciliation engine
- anomaly detection
- reporting
- visualization

Reason:

Production-style maintainability.

---

### Why Excel + TXT Reports?

TXT:

Readable audit report.

Excel:

Business-friendly format.

Allows finance teams to:

- filter anomalies
- inspect transactions
- review recommendations

---

## Iterative Improvements During Development

### Improvement 1

Original amounts were too small:

Example:

34.76

111.47

Issue:

Unrealistic for enterprise payment systems.

Fix:

Generate realistic high-value payments:

5000–150000

including business-style amounts:

15000

40000

45000

100000

---

### Improvement 2

Excel recommendation column showed:

`None`

Issue:

Looked incomplete and unprofessional.

Fix:

Replace empty recommendations with:

`No action required`

---

### Improvement 3

Added execution history inside Excel.

Reason:

Professional audit trail.

Each run appends:

- timestamp
- anomaly count
- records processed

---

## Final Architecture

Flow:

1. Generate synthetic transactions
2. Generate settlements
3. Inject anomalies
4. Reconcile records
5. Categorize mismatches
6. Detect anomalies
7. Generate TXT report
8. Generate Excel report
9. Generate charts
10. Print terminal summary

---

## Final Thought

The system intentionally balances:

Engineering realism

+

Assessment simplicity

rather than over-engineering financial infrastructure.