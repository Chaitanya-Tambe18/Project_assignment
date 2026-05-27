"""
Comprehensive Tests for Payments Reconciliation System

Tests cover:
- Normal reconciliation
- Duplicate detection
- Orphan refund detection
- Cross-month settlement detection
- Rounding discrepancy detection
- Aggregate reconciliation correctness
"""

import pytest
import pandas as pd
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_generator import DataGenerator
from src.reconciliation_engine import ReconciliationEngine, ReconciliationResult
from src.anomaly_detection import AnomalyDetector


class TestDataGenerator:
    """Tests for data generator."""
    
    def test_generate_transactions(self):
        """Test transaction generation creates expected columns."""
        generator = DataGenerator(seed=42)
        transactions = generator.generate_transactions(num_records=50)
        
        assert len(transactions) == 50
        expected_columns = [
            "transaction_id", "customer_id", "transaction_date",
            "amount", "currency", "type", "original_transaction_id", "status"
        ]
        for col in expected_columns:
            assert col in transactions.columns
        
        # Check all amounts are positive
        assert all(transactions["amount"] > 0)
        
        # Check all dates are in January 2026
        for date_str in transactions["transaction_date"]:
            assert "2026-01" in date_str
    
    def test_generate_settlements(self):
        """Test settlement generation matches transactions."""
        generator = DataGenerator(seed=42)
        transactions = generator.generate_transactions(num_records=50)
        transactions, settlements = generator.generate_settlements(transactions)
        
        assert len(settlements) > 0
        expected_columns = [
            "settlement_id", "transaction_id", "settlement_date",
            "settled_amount", "settlement_status", "bank_reference"
        ]
        for col in expected_columns:
            assert col in settlements.columns


class TestReconciliationEngine:
    """Tests for reconciliation engine."""
    
    def test_normal_reconciliation(self):
        """Test normal reconciliation with matching transactions."""
        # Create simple test data
        transactions = pd.DataFrame([
            {
                "transaction_id": "TXN001",
                "customer_id": "CUST0001",
                "transaction_date": "2026-01-01",
                "amount": 100.0,
                "currency": "USD",
                "type": "payment",
                "original_transaction_id": None,
                "status": "completed"
            }
        ])
        
        settlements = pd.DataFrame([
            {
                "settlement_id": "STL000001",
                "transaction_id": "TXN001",
                "settlement_date": "2026-01-02",
                "settled_amount": 100.0,
                "settlement_status": "settled",
                "bank_reference": "BANK00000001"
            }
        ])
        
        engine = ReconciliationEngine()
        results = engine.reconcile(transactions, settlements)
        
        assert len(results) == 1
        assert results[0].status == "matched"
        assert results[0].transaction_amount == 100.0
        assert results[0].settlement_amount == 100.0
    
    def test_duplicate_detection(self):
        """Test detection of duplicate settlement records."""
        transactions = pd.DataFrame([
            {
                "transaction_id": "TXN001",
                "customer_id": "CUST0001",
                "transaction_date": "2026-01-01",
                "amount": 100.0,
                "currency": "USD",
                "type": "payment",
                "original_transaction_id": None,
                "status": "completed"
            }
        ])
        
        # Create duplicate settlements
        settlements = pd.DataFrame([
            {
                "settlement_id": "STL000001",
                "transaction_id": "TXN001",
                "settlement_date": "2026-01-02",
                "settled_amount": 100.0,
                "settlement_status": "settled",
                "bank_reference": "BANK00000001"
            },
            {
                "settlement_id": "STL000002",
                "transaction_id": "TXN001",
                "settlement_date": "2026-01-02",
                "settled_amount": 100.0,
                "settlement_status": "settled",
                "bank_reference": "BANK00000002"
            }
        ])
        
        engine = ReconciliationEngine()
        results = engine.reconcile(transactions, settlements)
        
        assert len(results) == 1
        assert results[0].status == "duplicate_entry"
        assert "settlement" in results[0].reason.lower()
    
    def test_orphan_refund_detection(self):
        """Test detection of orphan refunds (refunds without original transaction)."""
        transactions = pd.DataFrame([
            {
                "transaction_id": "TXNREF001",
                "customer_id": "CUST0001",
                "transaction_date": "2026-01-15",
                "amount": 50.0,
                "currency": "USD",
                "type": "refund",
                "original_transaction_id": "TXN999999",  # Non-existent
                "status": "completed"
            }
        ])
        
        settlements = pd.DataFrame([
            {
                "settlement_id": "STL000001",
                "transaction_id": "TXNREF001",
                "settlement_date": "2026-01-17",
                "settled_amount": -50.0,
                "settlement_status": "settled",
                "bank_reference": "BANK00000001"
            }
        ])
        
        engine = ReconciliationEngine()
        results = engine.reconcile(transactions, settlements)
        
        assert len(results) == 1
        assert results[0].status == "orphan_refund"
        assert "non-existent" in results[0].reason.lower()
    
    def test_cross_month_settlement_detection(self):
        """Test detection of cross-month settlements."""
        transactions = pd.DataFrame([
            {
                "transaction_id": "TXN001",
                "customer_id": "CUST0001",
                "transaction_date": "2026-01-31",
                "amount": 100.0,
                "currency": "USD",
                "type": "payment",
                "original_transaction_id": None,
                "status": "completed"
            }
        ])
        
        settlements = pd.DataFrame([
            {
                "settlement_id": "STL000001",
                "transaction_id": "TXN001",
                "settlement_date": "2026-02-02",  # Next month
                "settled_amount": 100.0,
                "settlement_status": "settled",
                "bank_reference": "BANK00000001"
            }
        ])
        
        engine = ReconciliationEngine()
        results = engine.reconcile(transactions, settlements)
        
        assert len(results) == 1
        assert results[0].status == "cross_month_timing_issue"
        assert "next month" in results[0].reason.lower()
    
    def test_missing_settlement_detection(self):
        """Test detection of missing settlements."""
        transactions = pd.DataFrame([
            {
                "transaction_id": "TXN001",
                "customer_id": "CUST0001",
                "transaction_date": "2026-01-01",
                "amount": 100.0,
                "currency": "USD",
                "type": "payment",
                "original_transaction_id": None,
                "status": "completed"
            }
        ])
        
        # Empty settlements
        settlements = pd.DataFrame(columns=[
            "settlement_id", "transaction_id", "settlement_date",
            "settled_amount", "settlement_status", "bank_reference"
        ])
        
        engine = ReconciliationEngine()
        results = engine.reconcile(transactions, settlements)
        
        assert len(results) == 1
        assert results[0].status == "missing_settlement"
        assert "no matching settlement" in results[0].reason.lower()
    
    def test_rounding_discrepancy_detection(self):
        """Test detection of aggregate rounding discrepancies."""
        # Create transactions with amounts that will have rounding issues
        transactions = pd.DataFrame([
            {
                "transaction_id": f"TXN{i:03d}",
                "customer_id": "CUST0001",
                "transaction_date": "2026-01-01",
                "amount": 100.00 + (i * 0.005),  # Creates rounding issues
                "currency": "USD",
                "type": "payment",
                "original_transaction_id": None,
                "status": "completed"
            }
            for i in range(10)
        ])
        
        # Create settlements with slightly different amounts
        settlements = pd.DataFrame([
            {
                "settlement_id": f"STL{i:06d}",
                "transaction_id": f"TXN{i:03d}",
                "settlement_date": "2026-01-02",
                "settled_amount": 100.00 + (i * 0.005) + 0.001,  # Tiny difference
                "settlement_status": "settled",
                "bank_reference": f"BANK{i:08d}"
            }
            for i in range(10)
        ])
        
        engine = ReconciliationEngine()
        results = engine.reconcile(transactions, settlements)
        
        # These should still match (differences are small)
        matched = [r for r in results if r.status == "matched"]
        assert len(matched) == 10
        
        # But aggregate should show discrepancy
        rounding_analysis = engine.detect_aggregate_rounding_discrepancy(transactions, settlements)
        assert rounding_analysis["has_discrepancy"] == True
        assert rounding_analysis["difference"] > 0
    
    def test_aggregate_reconciliation_correctness(self):
        """Test that aggregate reconciliation is mathematically correct."""
        # Create simple matching data
        transactions = pd.DataFrame([
            {
                "transaction_id": f"TXN{i:03d}",
                "customer_id": "CUST0001",
                "transaction_date": "2026-01-01",
                "amount": 100.0 * (i + 1),
                "currency": "USD",
                "type": "payment",
                "original_transaction_id": None,
                "status": "completed"
            }
            for i in range(5)
        ])
        
        settlements = pd.DataFrame([
            {
                "settlement_id": f"STL{i:06d}",
                "transaction_id": f"TXN{i:03d}",
                "settlement_date": "2026-01-02",
                "settled_amount": 100.0 * (i + 1),
                "settlement_status": "settled",
                "bank_reference": f"BANK{i:08d}"
            }
            for i in range(5)
        ])
        
        engine = ReconciliationEngine()
        results = engine.reconcile(transactions, settlements)
        
        # All should match
        matched = [r for r in results if r.status == "matched"]
        assert len(matched) == 5
        
        # Aggregate should have no discrepancy
        rounding_analysis = engine.detect_aggregate_rounding_discrepancy(transactions, settlements)
        assert rounding_analysis["has_discrepancy"] == False
        assert rounding_analysis["difference"] == 0.0
    
    def test_summary_statistics(self):
        """Test that summary statistics are calculated correctly."""
        generator = DataGenerator(seed=42)
        transactions, settlements = generator.generate_data(50)
        
        engine = ReconciliationEngine()
        results = engine.reconcile(transactions, settlements)
        summary = engine.get_summary_statistics()
        
        assert summary["total_transactions"] == len(results)
        assert summary["matched_count"] >= 0
        assert summary["matched_percentage"] >= 0
        assert summary["matched_percentage"] <= 100


class TestAnomalyDetector:
    """Tests for anomaly detector."""
    
    def test_anomaly_detection(self):
        """Test that anomalies are correctly detected and categorized."""
        sample_results = [
            ReconciliationResult("TXN001", "matched", "OK", "None", "None", 100.0, 100.0, "2026-01-02"),
            ReconciliationResult("TXN002", "missing_settlement", "No settlement", "High", "Check bank", 200.0),
            ReconciliationResult("TXN003", "cross_month_timing_issue", "Late", "Medium", "Carry forward", 150.0, 150.0, "2026-02-02"),
            ReconciliationResult("TXN004", "duplicate_entry", "Duplicate", "High", "Remove duplicate", 300.0, 300.0, "2026-01-03"),
            ReconciliationResult("TXN005", "orphan_refund", "Bad reference", "High", "Fix reference", 50.0),
        ]
        
        detector = AnomalyDetector()
        anomalies = detector.detect_anomalies(sample_results)
        
        # Should detect 4 anomalies (excluding matched)
        assert len(anomalies) == 4
        
        # Check categories
        categories = [a.category for a in anomalies]
        assert "missing_settlement" in categories
        assert "cross_month_timing_issue" in categories
        assert "duplicate_entry" in categories
        assert "orphan_refund" in categories
    
    def test_anomaly_summary(self):
        """Test anomaly summary generation."""
        sample_results = [
            ReconciliationResult("TXN001", "missing_settlement", "No settlement", "High", "Check bank", 200.0),
            ReconciliationResult("TXN002", "missing_settlement", "No settlement", "High", "Check bank", 300.0),
        ]
        
        detector = AnomalyDetector()
        anomalies = detector.detect_anomalies(sample_results)
        summary = detector.get_anomaly_summary()
        
        assert summary["total_anomaly_categories"] == 1
        assert summary["total_anomaly_records"] == 2
        assert "missing_settlement" in summary["by_category"]
        assert summary["by_category"]["missing_settlement"]["count"] == 2
    
    def test_recommendations_generation(self):
        """Test that recommendations are generated for anomalies."""
        sample_results = [
            ReconciliationResult("TXN001", "missing_settlement", "No settlement", "High", "Check bank", 200.0),
        ]
        
        detector = AnomalyDetector()
        anomalies = detector.detect_anomalies(sample_results)
        recommendations = detector.get_recommendations()
        
        assert len(recommendations) > 0
        assert any("missing" in rec.lower() for rec in recommendations)


class TestIntegration:
    """Integration tests for the complete system."""
    
    def test_end_to_end_reconciliation(self):
        """Test complete end-to-end reconciliation process."""
        generator = DataGenerator(seed=42)
        transactions, settlements = generator.generate_data(100)
        
        engine = ReconciliationEngine()
        results = engine.reconcile(transactions, settlements)
        
        detector = AnomalyDetector()
        anomalies = detector.detect_anomalies(results)
        
        # Verify basic invariants
        assert len(results) > 0
        assert len(results) == len(transactions)
        assert len(anomalies) >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
