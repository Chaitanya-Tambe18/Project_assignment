# Production Limitations

Although this implementation is production-inspired, several real-world complexities are intentionally simplified.

---

## 1. Delayed Settlements Beyond Assumptions

### Current Assumption

Settlement delay:

1–2 days

### Real-World Issue

Banks may settle after:

- weekends
- holidays
- outages
- regulatory holds
- payment investigations

Example:

A payment processed on Jan 28 may settle on Feb 5.

### Impact

The system may incorrectly classify delayed settlements.

### Future Improvement

Implement configurable settlement SLA windows.

---

## 2. Partial Settlements

### Current Assumption

Transaction amount equals settlement amount.

### Real-World Issue

Banks may partially settle.

Example:

Platform:

₹100,000

Settlement batch:

₹80,000

Remaining:

₹20,000 later

### Impact

System may classify legitimate settlements as mismatches.

### Future Improvement

Support split settlement mapping.

---

## 3. Foreign Exchange (FX) Adjustments

### Current Assumption

Single currency.

USD only.

### Real-World Issue

International payments involve:

- FX conversion
- exchange-rate movement
- conversion fees

Example:

Platform:

USD 1,000

Settlement:

INR equivalent

### Impact

False mismatches possible.

### Future Improvement

FX-aware reconciliation.

---

## 4. Bank Fees & Taxes

### Current Assumption

Settlement amount equals transaction amount.

### Real-World Issue

Banks deduct:

- gateway fees
- taxes
- commissions
- processing costs

Example:

Platform:

₹50,000

Settlement:

₹49,850

### Impact

Amount mismatch false positives.

### Future Improvement

Fee-aware reconciliation rules.

---

## 5. Timezone Inconsistency

### Current Assumption

Single normalized timezone.

### Real-World Issue

Transaction systems may operate across:

- UTC
- IST
- PST
- banking cutoffs

### Impact

Incorrect timing mismatch classification.

### Future Improvement

Timezone normalization.

---

## 6. High-Volume Scaling

### Current Assumption

~200 records

### Real-World Issue

Payment processors handle:

millions of rows/day

### Impact

Pandas may become memory-heavy.

### Future Improvement

Use:

- Spark
- DuckDB
- BigQuery
- streaming reconciliation pipelines

---

## Final Engineering Note

This system was intentionally designed to balance:

**assessment clarity + engineering realism**

rather than implementing full-scale financial infrastructure.