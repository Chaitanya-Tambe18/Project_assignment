# Payments Reconciliation & Anomaly Detection System

A production-style Python system for reconciling payment platform transactions with bank settlements, identifying gaps, and explaining why reconciliation fails.

## Project Overview

This system addresses a common problem in payments companies: platform transaction records don't always match bank settlement records at month-end. The system:

- Generates realistic synthetic transaction and settlement data
- Performs intelligent reconciliation between platform and bank records
- Detects and categorizes various types of anomalies
- Provides detailed explanations and recommendations
- Generates comprehensive reports and visualizations

## Features

- **Synthetic Data Generation**: Creates realistic transaction and settlement datasets with intentional anomalies
- **Intelligent Reconciliation**: Matches platform transactions with bank settlements using multiple criteria
- **Anomaly Detection**: Identifies and categorizes 6+ types of reconciliation anomalies
- **Detailed Reporting**: Generates comprehensive reconciliation reports with actionable insights
- **Data Visualization**: Creates professional charts for analysis and presentation
- **Comprehensive Testing**: Full pytest test suite covering all functionality

## Assumptions

See [assumptions.md](assumptions.md) for detailed assumptions including:

1. Platform records transactions instantly
2. Bank settles after 1-2 days
3. Reconciliation period: January 2026
4. Each transaction has a unique transaction_id
5. Refunds reference an original transaction_id
6. Small rounding discrepancies are possible
7. Settlements should match platform transaction amount
8. Duplicate records can exist due to system errors

## Anomaly Types

The system detects and categorizes the following anomalies:

### 1. Cross-Month Settlement
- **Description**: Transactions in January that settle in February
- **Example**: Transaction on Jan 31 settling on Feb 2
- **Category**: `cross_month_timing_issue`
- **Severity**: Medium
- **Impact**: Month-end reconciliation mismatch
- **Recommendation**: Use carry-forward logic or delay reconciliation finalization

### 2. Aggregate Rounding Discrepancy
- **Description**: Tiny decimal precision inconsistencies visible only after aggregation
- **Example**: 100.005 values becoming rounded at settlement
- **Category**: `aggregate_rounding_difference`
- **Severity**: Low
- **Impact**: Small accounting discrepancies in totals
- **Recommendation**: Implement rounding rules at aggregation level

### 3. Duplicate Entry
- **Description**: Same transaction_id appearing multiple times in settlements
- **Example**: Duplicate settlement records in bank data
- **Category**: `duplicate_entry`
- **Severity**: High
- **Impact**: Potential double-counting of funds
- **Recommendation**: Investigate and remove duplicate settlement records

### 4. Orphan Refund
- **Description**: Refund records referencing non-existent original transactions
- **Example**: Refund for transaction_id that doesn't exist
- **Category**: `orphan_refund`
- **Severity**: High
- **Impact**: Data integrity issue
- **Recommendation**: Investigate and correct transaction references

### 5. Missing Settlement
- **Description**: Transactions without matching bank settlements
- **Example**: Platform transaction with no corresponding settlement
- **Category**: `missing_settlement`
- **Severity**: High
- **Impact**: Funds may not have been received
- **Recommendation**: Investigate with bank for delayed or failed settlements

### 6. Amount Mismatch
- **Description**: Settlement amounts differ from transaction amounts
- **Example**: Partial settlement or fee deduction
- **Category**: `amount_mismatch`
- **Severity**: Medium
- **Impact**: Accounting discrepancy
- **Recommendation**: Investigate partial settlements, fees, or data entry errors

## Project Structure

```
project_root/
│
├── data/
│   ├── transactions.csv          # Generated transaction data
│   ├── settlements.csv           # Generated settlement data
│
├── output/
│   ├── reconciliation_report.txt # Detailed reconciliation report
│   ├── charts/
│       ├── matched_vs_unmatched.png
│       ├── anomaly_distribution.png
│       ├── settlement_timing.png
│       ├── reconciliation_summary.png
│       └── anomaly_severity.png
│
├── src/
│   ├── data_generator.py         # Synthetic data generation
│   ├── reconciliation_engine.py  # Reconciliation logic
│   ├── anomaly_detection.py      # Anomaly categorization
│   ├── reporting.py              # Report generation
│   ├── visualization.py          # Chart generation
│   └── main.py                   # Main orchestration script
│
├── tests/
│   └── test_reconciliation.py    # Comprehensive test suite
│
├── README.md                     # This file
├── requirements.txt              # Python dependencies
└── assumptions.md               # Detailed assumptions
```

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. Clone or download the project

2. Install dependencies:
```bash
pip install -r requirements.txt
```

The required packages are:
- pandas>=2.0.0
- numpy>=1.24.0
- matplotlib>=3.7.0
- pytest>=7.4.0
- python-dateutil>=2.8.2

## How to Run

### Run the Complete System

Execute the main orchestration script:

```bash
python src/main.py
```

This will:
1. Generate synthetic transaction and settlement data
2. Perform reconciliation
3. Detect and categorize anomalies
4. Generate a detailed report
5. Create visualization charts
6. Print a summary to the terminal

### Expected Output

The script generates:
- **Data files**: `data/transactions.csv`, `data/settlements.csv`
- **Report**: `output/reconciliation_report.txt`
- **Charts**: 5 PNG files in `output/charts/`
- **Terminal output**: Summary statistics and recommendations

### Sample Terminal Output

```
================================================================================
PAYMENTS RECONCILIATION & ANOMALY DETECTION SYSTEM
================================================================================

STEP 1: Generating synthetic data...
--------------------------------------------------------------------------------
Generating 200 transaction records...
Generated 200 transactions
Generated 195 settlement records
Injected duplicate settlement for transaction: TXN000047
Injected orphan refund: TXNORPH001 referencing non-existent TXN999999
Saved transactions to data/transactions.csv
Saved settlements to data/settlements.csv

STEP 2: Performing reconciliation...
--------------------------------------------------------------------------------
Starting reconciliation process...
Found 1 transactions with duplicate settlements
  - TXN000047: 2 settlements
Reconciliation complete. Processed 201 records.

STEP 3: Detecting anomalies...
--------------------------------------------------------------------------------
Detecting anomalies...
Detected 5 anomaly categories

STEP 4: Generating reconciliation report...
--------------------------------------------------------------------------------
Generating reconciliation report at output/reconciliation_report.txt...
Report saved to output/reconciliation_report.txt

STEP 5: Creating visualizations...
--------------------------------------------------------------------------------
Generating visualization charts...
Chart saved: output/charts/matched_vs_unmatched.png
Chart saved: output/charts/anomaly_distribution.png
Chart saved: output/charts/settlement_timing.png
Chart saved: output/charts/reconciliation_summary.png
Chart saved: output/charts/anomaly_severity.png
All charts saved to output/charts

STEP 6: Terminal Summary
--------------------------------------------------------------------------------
================================================================================
RECONCILIATION SUMMARY
================================================================================
Total Transactions: 201
Matched: 185 (92.0%)
Missing Settlements: 5
Cross-Month Issues: 3
Duplicate Entries: 1
Orphan Refunds: 1
Pending: 6
Total Anomalies: 10
Rounding Discrepancy: $0.015000
================================================================================
```

## How to Run Tests

Run the complete test suite:

```bash
pytest tests/test_reconciliation.py -v
```

Run specific test classes:

```bash
pytest tests/test_reconciliation.py::TestReconciliationEngine -v
```

Run specific test methods:

```bash
pytest tests/test_reconciliation.py::TestReconciliationEngine::test_normal_reconciliation -v
```

### Test Coverage

The test suite includes:

1. **Normal Reconciliation**: Tests matching transactions with settlements
2. **Duplicate Detection**: Verifies detection of duplicate settlement records
3. **Orphan Refund Detection**: Tests identification of refunds without original transactions
4. **Cross-Month Settlement Detection**: Validates detection of timing issues
5. **Rounding Discrepancy Detection**: Tests aggregate-level rounding analysis
6. **Aggregate Reconciliation Correctness**: Verifies mathematical correctness
7. **Integration Tests**: End-to-end system testing

## Sample Outputs

### Reconciliation Report

The detailed report includes:
- Executive summary with key metrics
- Dataset statistics
- Anomaly details by category
- Rounding discrepancy analysis
- Detailed transaction results
- Recommendations
- Production limitations

### Charts

1. **Matched vs Unmatched**: Pie chart showing reconciliation success rate
2. **Anomaly Distribution**: Bar chart showing count of each anomaly type
3. **Settlement Timing**: Histogram showing settlement delay distribution
4. **Reconciliation Summary**: Comprehensive bar chart of all categories
5. **Anomaly Severity**: Pie chart showing severity distribution

## Production Limitations

The current implementation has the following limitations:

1. **Delayed Settlements Beyond Assumptions**
   - Real-world settlements may be delayed beyond 2 days due to bank holidays, system outages, or regulatory holds
   - The current system assumes settlements occur within 1-2 days

2. **Partial Settlements**
   - The current system assumes full settlement amounts
   - Real-world scenarios may involve partial settlements or split payments

3. **FX/Currency Adjustments**
   - Multi-currency transactions with foreign exchange rate fluctuations are not handled
   - All transactions are assumed to be in USD

4. **Bank Fees and Taxes**
   - Deductions for bank processing fees, taxes, or other charges are not accounted for
   - Settlement amounts may differ from transaction amounts due to these deductions

5. **Timezone Inconsistencies**
   - Transaction and settlement timestamps may be in different timezones
   - This can cause apparent timing mismatches

## Code Quality

The project follows production-quality standards:

- **Type Hints**: All functions use Python type hints
- **Docstrings**: Comprehensive docstrings for all modules and functions
- **Comments**: Inline comments explain complex logic
- **Modular Design**: Clean separation of concerns across modules
- **Logging**: Informative console output for debugging
- **Error Handling**: Robust error handling where applicable
- **Constants**: Configuration constants defined at module level

## Dependencies

- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computations
- **matplotlib**: Data visualization
- **pytest**: Testing framework
- **python-dateutil**: Date parsing utilities

## Extending the System

To extend the system for production use:

1. **Database Integration**: Replace CSV files with database connections
2. **Real Data Sources**: Connect to actual payment platform and bank APIs
3. **Additional Anomaly Types**: Add detection for other anomaly patterns
4. **Machine Learning**: Implement ML models for anomaly prediction
5. **Real-time Processing**: Add streaming data processing capabilities
6. **Alert System**: Implement automated alerts for critical anomalies
7. **Web Interface**: Build a dashboard for monitoring and investigation

## License

This is a demonstration project for educational purposes.

## Contact

For questions or issues, please refer to the project documentation or create an issue in the project repository.
