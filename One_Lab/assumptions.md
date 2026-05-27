# Assumptions for Payments Reconciliation System

## Core Assumptions

1. **Transaction Recording**: Platform records transactions instantly when a customer pays.

2. **Settlement Timing**: Bank settles funds in batches after 1-2 days from transaction date.

3. **Reconciliation Period**: Month-end reconciliation period is January 2026.

4. **Unique Identifiers**: Each transaction has a unique transaction_id.

5. **Refund Handling**: Refunds reference an original transaction_id for traceability.

6. **Rounding**: Small rounding discrepancies are possible due to decimal precision handling.

7. **Settlement Amount**: Settlements should match platform transaction amount exactly.

8. **Duplicate Records**: Duplicate records can exist due to bookkeeping or system errors.

9. **Currency**: All transactions are in USD for simplicity.

10. **Status Values**: 
    - Transaction status: completed, pending, failed
    - Settlement status: settled, pending, failed

## Data Generation Assumptions

- **Transaction Volume**: 150-250 records generated for January 2026.
- **Normal Settlement**: 90-95% of transactions settle within 1-2 days.
- **Cross-Month Settlement**: ~2-3% of transactions settle in the next month.
- **Refund Rate**: ~5-10% of transactions have refunds.
- **Duplicate Rate**: ~1-2% duplicate records in settlements.
- **Rounding Precision**: Amounts stored with 2 decimal places, but calculations may have 3+ decimal precision.

## Anomaly Injection Assumptions

1. **Cross-Month Settlement**: Transactions on Jan 31 settling on Feb 2 are classified as timing issues, not failures.

2. **Rounding Difference**: Tiny decimal inconsistencies (e.g., 100.005) that only appear when summed, not row-by-row.

3. **Duplicate Entry**: Same transaction_id appearing twice in bank settlements dataset.

4. **Orphan Refund**: Refund records referencing non-existent original transaction_id.

## Reconciliation Logic Assumptions

- **Matching Criteria**: transaction_id is the primary key for matching.
- **Timing Window**: Settlements within 2 days are considered normal.
- **Cross-Month Threshold**: Settlements in February for January transactions are flagged but not considered failures.
- **Rounding Tolerance**: Aggregate differences < 0.01 per transaction are considered rounding discrepancies.
- **Duplicate Detection**: Same transaction_id appearing more than once in settlements is flagged.

## Production Limitations

1. **Delayed Settlements Beyond Assumptions**: Real-world settlements may be delayed beyond 2 days due to bank holidays, system outages, or regulatory holds.

2. **Partial Settlements**: The current system assumes full settlement amounts, but real-world scenarios may involve partial settlements or split payments.

3. **FX/Currency Adjustments**: Multi-currency transactions with foreign exchange rate fluctuations are not handled in this implementation.

4. **Bank Fees and Taxes**: Deductions for bank processing fees, taxes, or other charges are not accounted for in the current model.

5. **Timezone Inconsistencies**: Transaction and settlement timestamps may be in different timezones, causing apparent timing mismatches.

## Data Quality Assumptions

- **No Missing Values**: All required fields are populated in synthetic data.
- **Valid References**: Refund original_transaction_id references valid transactions (except for intentional orphan refunds).
- **Date Ranges**: All transaction dates fall within January 2026.
- **Amount Ranges**: Transaction amounts are realistic (e.g., $10-$1000 for typical payments).
