# Payments Reconciliation & Anomaly Detection System

## Project Overview
A production-style Python system for reconciling payment platform transactions with bank settlement records, 
identifying mismatches, detecting anomalies, and generating detailed reconciliation reports with visual analytics.

The system performs the following operations:

- Generates realistic synthetic transaction and settlement datasets
- Performs intelligent reconciliation between platform and bank records
- Detects and categorizes reconciliation anomalies
- Provides detailed explanations and recommendations
- Generates reports and visualization charts

---

# System Workflow (Flow Chart)

```plaintext
+-----------------------------+
| Generate Transaction Data   |
+-------------+---------------+
              |
              v
+-----------------------------+
| Generate Settlement Data    |
+-------------+---------------+
              |
              v
+-----------------------------+
| Inject Synthetic Anomalies  |
+-------------+---------------+
              |
              v
+-----------------------------+
| Perform Reconciliation      |
+-------------+---------------+
              |
              v
+-----------------------------+
| Detect Anomalies            |
+-------------+---------------+
              |
              v
+-----------------------------+
| Generate Reports            |
+-------------+---------------+
              |
              v
+-----------------------------+
| Create Visualization Charts |
+-------------+---------------+
              |
              v
+-----------------------------+
| Display Final Summary       |
+-----------------------------+
```

---

# Features

## 1. Synthetic Data Generation
- Generates realistic transaction records
- Generates settlement records
- Injects intentional anomalies for testing

## 2. Intelligent Reconciliation
- Matches transactions with settlement records
- Handles delayed settlements
- Verifies transaction amounts

## 3. Anomaly Detection

Detects:
- Missing settlements
- Duplicate settlements
- Orphan refunds
- Cross-month settlements
- Amount mismatches
- Aggregate rounding discrepancies

## 4. Detailed Reporting
- Executive summary
- Reconciliation statistics
- Anomaly analysis
- Recommendations

## 5. Data Visualization

Creates:
- Match vs unmatched chart
- Anomaly distribution chart
- Settlement timing chart
- Severity analysis chart

## 6. Comprehensive Testing
- Unit testing
- Integration testing
- Validation testing

---

# Assumptions

- Platform records transactions instantly
- Bank settlements occur after 1–2 days
- Reconciliation period is January 2026
- Every transaction has a unique `transaction_id`
- Refunds reference original transactions
- Small rounding differences may occur
- Settlement amount should equal transaction amount
- Duplicate records may occur due to system failures

---

# Anomaly Types

## 1. Cross-Month Settlement

### Description
Transactions occurring in January but settling in February.

### Example
Transaction on Jan 31 settled on Feb 2.

### Details
- Category: `cross_month_timing_issue`
- Severity: Medium
- Impact: Month-end mismatch
- Recommendation: Carry-forward reconciliation logic

---

## 2. Aggregate Rounding Discrepancy

### Description
Tiny decimal precision inconsistencies after aggregation.

### Example
100.005 rounded differently during settlement.

### Details
- Category: `aggregate_rounding_difference`
- Severity: Low
- Impact: Minor accounting variance
- Recommendation: Standardized rounding rules

---

## 3. Duplicate Entry

### Description
Same transaction appears multiple times in settlement records.

### Example
Duplicate settlement for TXN000047.

### Details
- Category: `duplicate_entry`
- Severity: High
- Impact: Double counting
- Recommendation: Remove duplicate records

---

## 4. Orphan Refund

### Description
Refund references a non-existent original transaction.

### Example
Refund references TXN999999.

### Details
- Category: `orphan_refund`
- Severity: High
- Impact: Data integrity issue
- Recommendation: Validate refund references

---

## 5. Missing Settlement

### Description
Platform transaction without matching settlement.

### Example
Transaction exists but no bank settlement found.

### Details
- Category: `missing_settlement`
- Severity: High
- Impact: Funds may not be received
- Recommendation: Investigate bank settlement

---

## 6. Amount Mismatch

### Description
Settlement amount differs from transaction amount.

### Example
Partial settlement or bank fee deduction.

### Details
- Category: `amount_mismatch`
- Severity: Medium
- Impact: Accounting discrepancy
- Recommendation: Investigate fees or partial payments

---

# Project Structure

```plaintext
project_root/
│
├── data/
│   ├── transactions.csv
│   └── settlements.csv
│
├── output/
│   ├── reconciliation_report.txt
│   └── charts/
│       ├── matched_vs_unmatched.png
│       ├── anomaly_distribution.png
│       ├── settlement_timing.png
│       ├── reconciliation_summary.png
│       └── anomaly_severity.png
│
├── src/
│   ├── data_generator.py
│   ├── reconciliation_engine.py
│   ├── anomaly_detection.py
│   ├── reporting.py
│   ├── visualization.py
│   └── main.py
│
├── tests/
│   └── test_reconciliation.py
│
├── README.md
├── requirements.txt
└── assumptions.md
```

---

# Setup Instructions

## Prerequisites
- Python 3.8 or higher
- pip package manager

---

# Installation

## Step 1: Clone the Project

```bash
git clone <repository_url>
cd project_root
```

## Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Required Packages

```txt
pandas>=2.0.0
numpy>=1.24.0
matplotlib>=3.7.0
pytest>=7.4.0
python-dateutil>=2.8.2
```

---

# How to Run

```bash
python src/main.py
```

---

# Output Generated

## Data Files
- data/transactions.csv
- data/settlements.csv

## Report
- output/reconciliation_report.txt

## Charts
- matched_vs_unmatched.png
- anomaly_distribution.png
- settlement_timing.png
- reconciliation_summary.png
- anomaly_severity.png

---

# Sample Terminal Output

```plaintext
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

STEP 2: Performing reconciliation...
--------------------------------------------------------------------------------
Starting reconciliation process...
Found 1 transactions with duplicate settlements

STEP 3: Detecting anomalies...
--------------------------------------------------------------------------------
Detected 5 anomaly categories

STEP 4: Generating reconciliation report...
--------------------------------------------------------------------------------
Report saved successfully

STEP 5: Creating visualizations...
--------------------------------------------------------------------------------
Charts generated successfully

STEP 6: Terminal Summary
--------------------------------------------------------------------------------
Total Transactions: 201
Matched: 185
Missing Settlements: 5
Cross-Month Issues: 3
Duplicate Entries: 1
Orphan Refunds: 1
Pending: 6
Total Anomalies: 10
================================================================================
```

---

# Testing

## Run Complete Test Suite

```bash
pytest tests/test_reconciliation.py -v
```

## Run Specific Test Class

```bash
pytest tests/test_reconciliation.py::TestReconciliationEngine -v
```

## Run Specific Test Method

```bash
pytest tests/test_reconciliation.py::TestReconciliationEngine::test_normal_reconciliation -v
```

---

# Test Coverage

The project includes testing for:

- Normal reconciliation
- Duplicate detection
- Missing settlements
- Orphan refund detection
- Cross-month settlement detection
- Amount mismatch validation
- Rounding discrepancy analysis
- Integration testing

---

# Production Limitations

## 1. Delayed Settlements
Settlements may take more than 2 days.

## 2. Partial Settlements
Partial payments are not supported.

## 3. FX and Currency Adjustments
Only USD transactions are supported.

## 4. Bank Fees and Taxes
Bank deductions are not considered.

## 5. Timezone Differences
Timezone inconsistencies are not handled.

---

# Technologies Used

| Technology | Purpose |
|------------|----------|
| Python | Programming Language |
| Pandas | Data Processing |
| NumPy | Numerical Computation |
| Matplotlib | Data Visualization |
| Pytest | Testing |
| python-dateutil | Date Handling |

---

# Future Enhancements

- Database integration
- Real payment gateway APIs
- Machine learning anomaly prediction
- Real-time processing
- Automated alert system
- Web dashboard
- Multi-currency support
- Cloud deployment

---

# Conclusion

The Payments Reconciliation & Anomaly Detection System demonstrates a real-world fintech reconciliation workflow using Python. It includes synthetic data generation, intelligent reconciliation, anomaly detection, reporting, testing, and visualization, making it suitable for learning production-style financial data engineering systems.
