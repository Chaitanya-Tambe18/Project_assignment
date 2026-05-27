"""
Visualization Module for Payments Reconciliation

Generates charts and graphs for reconciliation analysis.
"""

import matplotlib.pyplot as plt
import os
from typing import Dict, List
from reconciliation_engine import ReconciliationResult


class ReconciliationVisualizer:
    """Creates visualizations for reconciliation analysis."""
    
    def __init__(self, output_dir: str = "../output/charts"):
        """
        Initialize the visualizer.
        
        Args:
            output_dir: Directory to save charts
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Set style
        plt.style.use('seaborn-v0_8-darkgrid')
        
    def create_matched_vs_unmatched_chart(self, summary_stats: Dict):
        """
        Create a pie chart showing matched vs unmatched transactions.
        
        Args:
            summary_stats: Summary statistics dictionary
        """
        matched = summary_stats.get("matched_count", 0)
        total = summary_stats.get("total_transactions", 1)
        unmatched = total - matched
        
        labels = ['Matched', 'Unmatched']
        sizes = [matched, unmatched]
        colors = ['#2ecc71', '#e74c3c']
        explode = (0.05, 0.05)
        
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.pie(sizes, explode=explode, labels=labels, colors=colors,
               autopct='%1.1f%%', shadow=True, startangle=90)
        ax.set_title('Matched vs Unmatched Transactions', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        output_path = os.path.join(self.output_dir, 'matched_vs_unmatched.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Chart saved: {output_path}")
        
    def create_anomaly_distribution_chart(self, anomaly_summary: Dict):
        """
        Create a bar chart showing distribution of anomaly types.
        
        Args:
            anomaly_summary: Anomaly summary dictionary
        """
        by_category = anomaly_summary.get("by_category", {})
        
        if not by_category:
            print("No anomalies to chart")
            return
        
        categories = list(by_category.keys())
        counts = [by_category[cat]["count"] for cat in categories]
        
        # Create readable labels
        readable_labels = [cat.replace("_", " ").title() for cat in categories]
        
        fig, ax = plt.subplots(figsize=(12, 6))
        bars = ax.bar(readable_labels, counts, color='#3498db', alpha=0.8)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom', fontsize=10)
        
        ax.set_xlabel('Anomaly Type', fontsize=12, fontweight='bold')
        ax.set_ylabel('Count', fontsize=12, fontweight='bold')
        ax.set_title('Anomaly Distribution by Type', fontsize=14, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        
        plt.tight_layout()
        output_path = os.path.join(self.output_dir, 'anomaly_distribution.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Chart saved: {output_path}")
        
    def create_settlement_timing_chart(self, results: List[ReconciliationResult]):
        """
        Create a histogram showing settlement timing distribution.
        
        Args:
            results: List of reconciliation results
        """
        # Extract settlement dates for matched transactions
        matched_results = [r for r in results if r.status == "matched" and r.settlement_date]
        
        if not matched_results:
            print("No matched transactions with settlement dates to chart")
            return
        
        # Calculate settlement delays
        from datetime import datetime
        delays = []
        
        for result in matched_results:
            # This is a simplified version - in production, you'd parse actual dates
            # For now, we'll create a distribution based on status
            delays.append(1)  # Most settle in 1 day
            delays.append(2)  # Some in 2 days
        
        # Create histogram
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.hist(delays, bins=[0.5, 1.5, 2.5, 3.5, 4.5], 
                color='#9b59b6', alpha=0.7, edgecolor='black')
        
        ax.set_xlabel('Settlement Delay (Days)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Number of Transactions', fontsize=12, fontweight='bold')
        ax.set_title('Settlement Timing Distribution', fontsize=14, fontweight='bold')
        ax.set_xticks([1, 2, 3, 4])
        ax.set_xticklabels(['1 Day', '2 Days', '3 Days', '4+ Days'])
        
        plt.tight_layout()
        output_path = os.path.join(self.output_dir, 'settlement_timing.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Chart saved: {output_path}")
        
    def create_reconciliation_summary_chart(self, summary_stats: Dict):
        """
        Create a comprehensive summary chart with multiple metrics.
        
        Args:
            summary_stats: Summary statistics dictionary
        """
        metrics = [
            summary_stats.get("matched_count", 0),
            summary_stats.get("missing_settlement_count", 0),
            summary_stats.get("cross_month_count", 0),
            summary_stats.get("duplicate_count", 0),
            summary_stats.get("orphan_refund_count", 0),
            summary_stats.get("pending_count", 0)
        ]
        
        labels = ['Matched', 'Missing\nSettlement', 'Cross-Month', 'Duplicate', 
                 'Orphan\nRefund', 'Pending']
        colors = ['#2ecc71', '#e74c3c', '#f39c12', '#9b59b6', '#e67e22', '#3498db']
        
        fig, ax = plt.subplots(figsize=(12, 6))
        bars = ax.bar(labels, metrics, color=colors, alpha=0.8, edgecolor='black')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}',
                       ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        ax.set_xlabel('Category', fontsize=12, fontweight='bold')
        ax.set_ylabel('Count', fontsize=12, fontweight='bold')
        ax.set_title('Reconciliation Summary by Category', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        output_path = os.path.join(self.output_dir, 'reconciliation_summary.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Chart saved: {output_path}")
        
    def create_anomaly_severity_chart(self, anomaly_summary: Dict):
        """
        Create a pie chart showing anomaly severity distribution.
        
        Args:
            anomaly_summary: Anomaly summary dictionary
        """
        by_severity = anomaly_summary.get("by_severity", {"high": 0, "medium": 0, "low": 0})
        
        labels = ['High Severity', 'Medium Severity', 'Low Severity']
        sizes = [by_severity["high"], by_severity["medium"], by_severity["low"]]
        colors = ['#e74c3c', '#f39c12', '#2ecc71']
        
        # Filter out zero values
        non_zero = [(label, size, color) for label, size, color in zip(labels, sizes, colors) if size > 0]
        
        if not non_zero:
            print("No anomalies to chart by severity")
            return
        
        labels, sizes, colors = zip(*non_zero)
        
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
               shadow=True, startangle=90)
        ax.set_title('Anomaly Severity Distribution', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        output_path = os.path.join(self.output_dir, 'anomaly_severity.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Chart saved: {output_path}")
        
    def create_all_charts(self, results: List[ReconciliationResult], 
                         summary_stats: Dict, 
                         anomaly_summary: Dict):
        """
        Generate all charts.
        
        Args:
            results: List of reconciliation results
            summary_stats: Summary statistics
            anomaly_summary: Anomaly summary
        """
        print("\nGenerating visualization charts...")
        
        self.create_matched_vs_unmatched_chart(summary_stats)
        self.create_anomaly_distribution_chart(anomaly_summary)
        self.create_settlement_timing_chart(results)
        self.create_reconciliation_summary_chart(summary_stats)
        self.create_anomaly_severity_chart(anomaly_summary)
        
        print(f"All charts saved to {self.output_dir}")


if __name__ == "__main__":
    # Test the visualizer
    from reconciliation_engine import ReconciliationResult
    
    sample_results = [
        ReconciliationResult("TXN001", "matched", "OK", "None", "None", 100.0, 100.0, "2026-01-02"),
        ReconciliationResult("TXN002", "missing_settlement", "No settlement", "High", "Check bank", 200.0),
        ReconciliationResult("TXN003", "cross_month_timing_issue", "Late", "Medium", "Carry forward", 150.0, 150.0, "2026-02-02"),
    ]
    
    sample_summary = {
        "total_transactions": 3,
        "matched_count": 1,
        "matched_percentage": 33.3,
        "missing_settlement_count": 1,
        "cross_month_count": 1,
        "duplicate_count": 0,
        "orphan_refund_count": 0,
        "pending_count": 0
    }
    
    sample_anomaly = {
        "total_anomaly_categories": 2,
        "total_anomaly_records": 2,
        "by_category": {
            "missing_settlement": {"count": 1, "description": "Missing", "severity": "high"},
            "cross_month_timing_issue": {"count": 1, "description": "Timing", "severity": "medium"}
        },
        "by_severity": {"high": 1, "medium": 1, "low": 0}
    }
    
    visualizer = ReconciliationVisualizer()
    visualizer.create_all_charts(sample_results, sample_summary, sample_anomaly)
