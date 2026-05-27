"""
Anomaly Detection Module for Payments Reconciliation

Categorizes and analyzes reconciliation anomalies.
"""

from typing import Dict, List
from dataclasses import dataclass
from reconciliation_engine import ReconciliationResult


@dataclass
class Anomaly:
    """Data class representing a detected anomaly."""
    category: str
    transaction_id: str
    description: str
    severity: str
    count: int = 1


class AnomalyDetector:
    """Detects and categorizes reconciliation anomalies."""
    
    def __init__(self):
        """Initialize the anomaly detector."""
        self.anomalies: List[Anomaly] = []
        
    def detect_anomalies(self, results: List[ReconciliationResult]) -> List[Anomaly]:
        """
        Detect and categorize anomalies from reconciliation results.
        
        Args:
            results: List of ReconciliationResult objects
            
        Returns:
            List of Anomaly objects
        """
        print("Detecting anomalies...")
        self.anomalies = []
        
        # Group by category
        anomaly_groups: Dict[str, List[ReconciliationResult]] = {}
        
        for result in results:
            if result.status != "matched" and result.status != "pending":
                category = result.status
                if category not in anomaly_groups:
                    anomaly_groups[category] = []
                anomaly_groups[category].append(result)
        
        # Create anomaly objects for each category
        for category, results_list in anomaly_groups.items():
            anomaly = self._create_anomaly(category, results_list)
            self.anomalies.append(anomaly)
        
        print(f"Detected {len(self.anomalies)} anomaly categories")
        return self.anomalies
    
    def _create_anomaly(self, category: str, 
                        results: List[ReconciliationResult]) -> Anomaly:
        """
        Create an anomaly object from a group of results.
        
        Args:
            category: Anomaly category
            results: List of reconciliation results for this category
            
        Returns:
            Anomaly object
        """
        # Map categories to descriptions and severity
        category_info = {
            "missing_settlement": {
                "description": "Transactions without matching bank settlements",
                "severity": "high"
            },
            "cross_month_timing_issue": {
                "description": "Transactions settling in the next month",
                "severity": "medium"
            },
            "duplicate_entry": {
                "description": "Duplicate settlement records for same transaction",
                "severity": "high"
            },
            "orphan_refund": {
                "description": "Refunds referencing non-existent original transactions",
                "severity": "high"
            },
            "orphan_settlement": {
                "description": "Bank settlements without matching platform transactions",
                "severity": "high"
            },
            "amount_mismatch": {
                "description": "Settlement amounts differ from transaction amounts",
                "severity": "medium"
            }
        }
        
        info = category_info.get(category, {
            "description": f"Uncategorized anomaly: {category}",
            "severity": "medium"
        })
        
        # Get example transaction ID
        example_id = results[0].transaction_id if results else "N/A"
        
        return Anomaly(
            category=category,
            transaction_id=example_id,
            description=info["description"],
            severity=info["severity"],
            count=len(results)
        )
    
    def get_anomaly_summary(self) -> Dict:
        """
        Generate a summary of detected anomalies.
        
        Returns:
            Dictionary with anomaly summary
        """
        summary = {
            "total_anomaly_categories": len(self.anomalies),
            "total_anomaly_records": sum(a.count for a in self.anomalies),
            "by_category": {},
            "by_severity": {"high": 0, "medium": 0, "low": 0}
        }
        
        for anomaly in self.anomalies:
            summary["by_category"][anomaly.category] = {
                "count": anomaly.count,
                "description": anomaly.description,
                "severity": anomaly.severity
            }
            summary["by_severity"][anomaly.severity] += anomaly.count
        
        return summary
    
    def get_recommendations(self) -> List[str]:
        """
        Generate recommendations based on detected anomalies.
        
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        for anomaly in self.anomalies:
            if anomaly.category == "missing_settlement":
                recommendations.append(
                    f"MISSING SETTLEMENT: Investigate {anomaly.count} transactions "
                    "without settlements. Check with bank for delayed or failed settlements."
                )
            elif anomaly.category == "cross_month_timing_issue":
                recommendations.append(
                    f"CROSS-MONTH TIMING: {anomaly.count} transactions settled in next month. "
                    "Implement carry-forward logic or adjust reconciliation period."
                )
            elif anomaly.category == "duplicate_entry":
                recommendations.append(
                    f"DUPLICATE ENTRY: {anomaly.count} transactions have duplicate settlements. "
                    "Review settlement records and remove duplicates to prevent double-counting."
                )
            elif anomaly.category == "orphan_refund":
                recommendations.append(
                    f"ORPHAN REFUND: {anomaly.count} refunds reference non-existent transactions. "
                    "Investigate data integrity issues and correct transaction references."
                )
            elif anomaly.category == "orphan_settlement":
                recommendations.append(
                    f"ORPHAN SETTLEMENT: Bank settlements without matching platform transactions. "
                    "Review transaction recording process for missing records."
                )
            elif anomaly.category == "amount_mismatch":
                recommendations.append(
                    f"AMOUNT MISMATCH: {anomaly.count} transactions have settlement amount differences. "
                    "Investigate partial settlements, fees, or data entry errors."
                )
        
        return recommendations


if __name__ == "__main__":
    # Test the detector
    from .reconciliation_engine import ReconciliationEngine, ReconciliationResult
    
    # Create sample results
    sample_results = [
        ReconciliationResult("TXN001", "matched", "OK", "None", "None", 100.0, 100.0, "2026-01-02"),
        ReconciliationResult("TXN002", "missing_settlement", "No settlement", "High", "Check bank", 200.0),
        ReconciliationResult("TXN003", "cross_month_timing_issue", "Late settlement", "Medium", "Carry forward", 150.0, 150.0, "2026-02-02"),
        ReconciliationResult("TXN004", "duplicate_entry", "Duplicate", "High", "Remove duplicate", 300.0, 300.0, "2026-01-03"),
        ReconciliationResult("TXN005", "orphan_refund", "Bad reference", "High", "Fix reference", 50.0),
    ]
    
    detector = AnomalyDetector()
    anomalies = detector.detect_anomalies(sample_results)
    
    print("\n=== Detected Anomalies ===")
    for anomaly in anomalies:
        print(f"{anomaly.category}: {anomaly.count} records ({anomaly.severity} severity)")
    
    print("\n=== Recommendations ===")
    for rec in detector.get_recommendations():
        print(f"- {rec}")
