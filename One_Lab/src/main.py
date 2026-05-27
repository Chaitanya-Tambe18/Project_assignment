"""
Main Orchestration Script for Payments Reconciliation System

This script orchestrates the entire reconciliation process:
1. Data generation
2. Reconciliation
3. Anomaly detection
4. Report generation
5. Visualization
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_generator import DataGenerator
from src.reconciliation_engine import ReconciliationEngine
from src.anomaly_detection import AnomalyDetector
from src.reporting import ReportGenerator
from src.visualization import ReconciliationVisualizer


def main():
    """Main execution function."""
    print("=" * 80)
    print("PAYMENTS RECONCILIATION & ANOMALY DETECTION SYSTEM")
    print("=" * 80)
    print()
    
    # Step 1: Generate synthetic data
    print("STEP 1: Generating synthetic data...")
    print("-" * 80)
    generator = DataGenerator(seed=42)
    transactions, settlements = generator.generate_data(num_transactions=200)
    generator.save_data(transactions, settlements, output_dir="data")
    print()
    
    # Step 2: Perform reconciliation
    print("STEP 2: Performing reconciliation...")
    print("-" * 80)
    engine = ReconciliationEngine()
    results = engine.reconcile(transactions, settlements)
    summary_stats = engine.get_summary_statistics()
    rounding_analysis = engine.detect_aggregate_rounding_discrepancy(transactions, settlements)
    print()
    
    # Step 3: Detect anomalies
    print("STEP 3: Detecting anomalies...")
    print("-" * 80)
    detector = AnomalyDetector()
    anomalies = detector.detect_anomalies(results)
    anomaly_summary = detector.get_anomaly_summary()
    recommendations = detector.get_recommendations()
    print()
    
    # Step 4: Generate report
    print("STEP 4: Generating reconciliation report...")
    print("-" * 80)
    report_generator = ReportGenerator()
    report_text = report_generator.generate_report(
    results=results,
    summary_stats=summary_stats,
    anomaly_summary=anomaly_summary,
    rounding_analysis=rounding_analysis,
    recommendations=recommendations,
    output_path="output/reconciliation_report.txt"
    )

    # Generate professional Excel report
    report_generator.generate_excel_report(
        results=results,
        summary_stats=summary_stats,
        anomaly_summary=anomaly_summary,
        rounding_analysis=rounding_analysis,
        recommendations=recommendations,
        output_path="output/reconciliation_results.xlsx"
    )
    print()
    
    # Step 5: Create visualizations
    print("STEP 5: Creating visualizations...")
    print("-" * 80)
    visualizer = ReconciliationVisualizer(output_dir="output/charts")
    visualizer.create_all_charts(results, summary_stats, anomaly_summary)
    print()
    
    # Print summary to terminal
    print("STEP 6: Terminal Summary")
    print("-" * 80)
    report_generator.print_summary(summary_stats, anomaly_summary, rounding_analysis)
    print()
    
    # Print recommendations
    print("RECOMMENDATIONS")
    print("-" * 80)
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")
    print()
    
    print("=" * 80)
    print("RECONCILIATION PROCESS COMPLETE")
    print("=" * 80)
    print()
    print("Outputs generated:")
    print("  - data/transactions.csv")
    print("  - data/settlements.csv")
    print("  - output/reconciliation_report.txt")
    print("  - output/charts/matched_vs_unmatched.png")
    print("  - output/charts/anomaly_distribution.png")
    print("  - output/charts/settlement_timing.png")
    print("  - output/charts/reconciliation_summary.png")
    print("  - output/charts/anomaly_severity.png")
    print()


if __name__ == "__main__":
    main() 