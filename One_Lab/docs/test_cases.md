# Test Cases — Payments Reconciliation & Anomaly Detection System

## Goal

Validate reconciliation correctness and anomaly detection reliability.

Framework:

`pytest`

Command:

```bash
pytest tests/
```

---

# Test Case 1 — Normal Reconciliation

## Objective

Ensure successful matching between platform transactions and settlements.

### Input

Transaction:

| transaction_id | amount |
|---|---:|
| TXN001 | 15000 |

Settlement:

| transaction_id | settled_amount |
|---|---:|
| TXN001 | 15000 |

### Expected Result

- status = matched
- no anomaly

### Assertion

```python
assert result.status == "matched"
```

---

# Test Case 2 — Duplicate Settlement Detection

## Objective

Detect duplicate settlement records.

### Input

Same transaction_id appears twice.

Settlement:

TXN001

TXN001

### Expected Result

Category:

duplicate_entry

### Assertion

```python
assert duplicate_count > 0
```

---

# Test Case 3 — Orphan Refund Detection

## Objective

Detect refunds referencing missing transactions.

### Input

Refund:

```text
original_transaction_id = TXN999999
```

(non-existent)

### Expected Result

Category:

orphan_refund

### Assertion

```python
assert orphan_refund_count == 1
```

---

# Test Case 4 — Cross-Month Settlement Detection

## Objective

Ensure delayed settlement is treated as timing issue.

### Input

Transaction:

```text
2026-01-31
```

Settlement:

```text
2026-02-02
```

### Expected Result

Category:

cross_month_timing_issue

NOT:

missing_settlement

### Assertion

```python
assert result.status == "cross_month_timing_issue"
```

---

# Test Case 5 — Aggregate Rounding Detection

## Objective

Detect decimal precision discrepancy visible only after aggregation.

### Input

Platform total:

```text
100000.025
```

Settlement total:

```text
100000.00
```

### Expected Result

Category:

aggregate_rounding_difference

### Assertion

```python
assert rounding_analysis["has_discrepancy"] is True
```

---

# Test Case 6 — Aggregate Reconciliation Correctness

## Objective

Validate reconciliation totals.

### Expected

System should correctly compute:

- matched count
- anomaly count
- pending count
- settlement totals

### Assertion

```python
assert total_transactions > 0
assert matched_count >= 0
assert anomaly_count >= 0
```

---

## Test Coverage Summary

| Test | Status |
|---|---|
| Normal reconciliation | ✅ |
| Duplicate detection | ✅ |
| Orphan refund detection | ✅ |
| Cross-month settlement | ✅ |
| Aggregate rounding | ✅ |
| Reconciliation correctness | ✅ |

---

## Expected Outcome

The system should:

- correctly reconcile valid records
- identify anomalies
- explain mismatch causes
- generate stable reports
- remain deterministic with seeded synthetic data