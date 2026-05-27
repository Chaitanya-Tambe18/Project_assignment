"""
Reconciliation Engine for Payments System

Matches platform transactions with bank settlements and identifies discrepancies.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class ReconciliationResult:
    """Data class to hold reconciliation results."""
    transaction_id: str
    status: str
    reason: str
    impact: str
    recommendation: str
    transaction_amount: float
    settlement_amount: float = None
    settlement_date: str = None


class ReconciliationEngine:
    """Engine for reconciling platform transactions with bank settlements."""
    
    def __init__(self):
        """Initialize the reconciliation engine."""
        self.results: List[ReconciliationResult] = []
        
    def reconcile(self, transactions: pd.DataFrame, 
                  settlements: pd.DataFrame) -> List[ReconciliationResult]:
        """
        Perform reconciliation between transactions and settlements.
        
        Args:
            transactions: DataFrame of platform transactions
            settlements: DataFrame of bank settlements
            
        Returns:
            List of ReconciliationResult objects
        """
        print("Starting reconciliation process...")
        self.results = []
        
        # Check for duplicate settlements
        duplicate_check = self._check_duplicate_settlements(settlements)
        
        # Process each transaction
        for _, txn in transactions.iterrows():
            result = self._reconcile_transaction(txn, settlements, duplicate_check, transactions)
            self.results.append(result)
        
        # Check for orphan settlements (settlements without matching transactions)
        self._check_orphan_settlements(transactions, settlements)
        
        print(f"Reconciliation complete. Processed {len(self.results)} records.")
        return self.results
    
    def _check_duplicate_settlements(self, settlements: pd.DataFrame) -> Dict[str, int]:
        """
        Check for duplicate settlement records.
        
        Args:
            settlements: DataFrame of settlements
            
        Returns:
            Dictionary mapping transaction_id to count of settlements
        """
        settlement_counts = settlements["transaction_id"].value_counts()
        duplicates = settlement_counts[settlement_counts > 1].to_dict()
        
        if duplicates:
            print(f"Found {len(duplicates)} transactions with duplicate settlements")
            for txn_id, count in duplicates.items():
                print(f"  - {txn_id}: {count} settlements")
        
        return settlement_counts.to_dict()
    
    def _reconcile_transaction(self, txn: pd.Series, 
                               settlements: pd.DataFrame,
                               duplicate_check: Dict[str, int],
                               transactions: pd.DataFrame) -> ReconciliationResult:
        """
        Reconcile a single transaction against settlements.
        
        Args:
            txn: Single transaction record
            settlements: DataFrame of all settlements
            duplicate_check: Dictionary of settlement counts per transaction
            
        Returns:
            ReconciliationResult for this transaction
        """
        txn_id = txn["transaction_id"]
        txn_amount = txn["amount"]
        txn_date = datetime.strptime(txn["transaction_date"], "%Y-%m-%d")
        
        # Find matching settlements
        matching_settlements = settlements[settlements["transaction_id"] == txn_id]
        
        # Check for duplicates
        settlement_count = duplicate_check.get(txn_id, 0)
        
        if settlement_count > 1:
            return ReconciliationResult(
                transaction_id=txn_id,
                status="duplicate_entry",
                reason=f"Transaction has {settlement_count} settlement records",
                impact="Potential double-counting of funds",
                recommendation="Investigate duplicate settlement records and remove duplicates",
                transaction_amount=txn_amount,
                settlement_amount=matching_settlements["settled_amount"].iloc[0],
                settlement_date=matching_settlements["settlement_date"].iloc[0]
            )
        
        # No matching settlement
        if len(matching_settlements) == 0:
            # Check if it's a pending transaction
            if txn["status"] == "pending":
                return ReconciliationResult(
                    transaction_id=txn_id,
                    status="pending",
                    reason="Transaction is still pending settlement",
                    impact="Expected to settle in future",
                    recommendation="Monitor for settlement in next reconciliation cycle",
                    transaction_amount=txn_amount
                )
            
            # Check if it's an orphan refund
            if txn["type"] == "refund":
                original_exists = txn["original_transaction_id"] in transactions["transaction_id"].values
                if not original_exists:
                    return ReconciliationResult(
                        transaction_id=txn_id,
                        status="orphan_refund",
                        reason=f"Refund references non-existent original transaction: {txn['original_transaction_id']}",
                        impact="Refund without valid original transaction",
                        recommendation="Investigate data integrity issue and correct original transaction reference",
                        transaction_amount=txn_amount
                    )
            
            # Missing settlement
            return ReconciliationResult(
                transaction_id=txn_id,
                status="missing_settlement",
                reason="No matching settlement found in bank records",
                impact="Funds may not have been received or settlement is delayed",
                recommendation="Investigate with bank and check for delayed settlements",
                transaction_amount=txn_amount
            )
        
        # Found matching settlement
        settlement = matching_settlements.iloc[0]
        settlement_date = datetime.strptime(settlement["settlement_date"], "%Y-%m-%d")
        settled_amount = settlement["settled_amount"]
        
        # Check for orphan refund (refund with invalid original transaction reference)
        if txn["type"] == "refund" and txn["original_transaction_id"]:
            original_exists = txn["original_transaction_id"] in transactions["transaction_id"].values
            if not original_exists:
                return ReconciliationResult(
                    transaction_id=txn_id,
                    status="orphan_refund",
                    reason=f"Refund references non-existent original transaction: {txn['original_transaction_id']}",
                    impact="Refund without valid original transaction",
                    recommendation="Investigate data integrity issue and correct original transaction reference",
                    transaction_amount=txn_amount,
                    settlement_amount=settled_amount,
                    settlement_date=settlement["settlement_date"]
                )
        
        # Check for cross-month settlement
        if settlement_date.month > txn_date.month:
            days_delay = (settlement_date - txn_date).days
            return ReconciliationResult(
                transaction_id=txn_id,
                status="cross_month_timing_issue",
                reason=f"Settlement occurred in next month ({settlement_date.strftime('%Y-%m-%d')})",
                impact="Month-end reconciliation mismatch",
                recommendation="Use carry-forward logic or delay reconciliation finalization",
                transaction_amount=txn_amount,
                settlement_amount=settled_amount,
                settlement_date=settlement["settlement_date"]
            )
        
        # Check for amount mismatch
        amount_diff = abs(abs(settled_amount) - txn_amount)
        if amount_diff > 0.01:  # More than 1 cent difference
            return ReconciliationResult(
                transaction_id=txn_id,
                status="amount_mismatch",
                reason=f"Settlement amount ({settled_amount}) differs from transaction amount ({txn_amount})",
                impact="Accounting discrepancy",
                recommendation="Investigate partial settlement, fees, or data entry error",
                transaction_amount=txn_amount,
                settlement_amount=settled_amount,
                settlement_date=settlement["settlement_date"]
            )
        
        # Successfully matched
        return ReconciliationResult(
            transaction_id=txn_id,
            status="matched",
            reason="Transaction successfully matched with settlement",
            impact="None",
            recommendation="None",
            transaction_amount=txn_amount,
            settlement_amount=settled_amount,
            settlement_date=settlement["settlement_date"]
        )
    
    def _check_orphan_settlements(self, transactions: pd.DataFrame, 
                                  settlements: pd.DataFrame):
        """
        Check for settlements without matching transactions.
        
        Args:
            transactions: DataFrame of transactions
            settlements: DataFrame of settlements
        """
        txn_ids = set(transactions["transaction_id"].values)
        settlement_txn_ids = set(settlements["transaction_id"].values)
        
        orphan_settlements = settlement_txn_ids - txn_ids
        
        if orphan_settlements:
            print(f"Found {len(orphan_settlements)} orphan settlements")
            for orphan_id in orphan_settlements:
                self.results.append(ReconciliationResult(
                    transaction_id=orphan_id,
                    status="orphan_settlement",
                    reason="Settlement exists without matching platform transaction",
                    impact="Unknown funds received",
                    recommendation="Investigate missing transaction record in platform",
                    transaction_amount=0,
                    settlement_amount=settlements[settlements["transaction_id"] == orphan_id]["settled_amount"].iloc[0]
                ))
    
    def detect_aggregate_rounding_discrepancy(self, transactions: pd.DataFrame,
                                              settlements: pd.DataFrame) -> Dict:
        """
        Detect aggregate rounding discrepancies that only appear when summed.
        
        Args:
            transactions: DataFrame of transactions
            settlements: DataFrame of settlements
            
        Returns:
            Dictionary with rounding discrepancy analysis
        """
        print("Checking for aggregate rounding discrepancies...")
        
        # Get matched transactions
        matched_results = [r for r in self.results if r.status == "matched"]
        
        if not matched_results:
            return {
                "has_discrepancy": False,
                "total_transaction_amount": 0,
                "total_settlement_amount": 0,
                "difference": 0,
                "category": "none"
            }
        
        # Sum transaction amounts
        total_txn_amount = sum(r.transaction_amount for r in matched_results)
        
        # Sum settlement amounts
        total_stl_amount = sum(abs(r.settlement_amount) for r in matched_results if r.settlement_amount)
        
        difference = abs(total_txn_amount - total_stl_amount)
        
        # Check if discrepancy exists (small but non-zero)
        has_discrepancy = 0 < difference < 0.1  # Less than 10 cents but non-zero
        
        result = {
            "has_discrepancy": has_discrepancy,
            "total_transaction_amount": total_txn_amount,
            "total_settlement_amount": total_stl_amount,
            "difference": difference,
            "category": "aggregate_rounding_difference" if has_discrepancy else "none"
        }
        
        if has_discrepancy:
            print(f"Aggregate rounding discrepancy detected: ${difference:.6f}")
        
        return result
    
    def get_summary_statistics(self) -> Dict:
        """
        Generate summary statistics from reconciliation results.
        
        Returns:
            Dictionary with summary statistics
        """
        status_counts = {}
        for result in self.results:
            status_counts[result.status] = status_counts.get(result.status, 0) + 1
        
        total = len(self.results)
        
        return {
            "total_transactions": total,
            "status_counts": status_counts,
            "matched_count": status_counts.get("matched", 0),
            "matched_percentage": (status_counts.get("matched", 0) / total * 100) if total > 0 else 0,
            "missing_settlement_count": status_counts.get("missing_settlement", 0),
            "cross_month_count": status_counts.get("cross_month_timing_issue", 0),
            "duplicate_count": status_counts.get("duplicate_entry", 0),
            "orphan_refund_count": status_counts.get("orphan_refund", 0),
            "pending_count": status_counts.get("pending", 0)
        }


if __name__ == "__main__":
    # Test the engine
    from data_generator import DataGenerator
    
    generator = DataGenerator()
    transactions, settlements = generator.generate_data(50)
    
    engine = ReconciliationEngine()
    results = engine.reconcile(transactions, settlements)
    
    print("\n=== Reconciliation Summary ===")
    summary = engine.get_summary_statistics()
    for key, value in summary.items():
        print(f"{key}: {value}")
