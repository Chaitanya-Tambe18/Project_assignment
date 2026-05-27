import os
from datetime import datetime
from typing import Dict, List

import pandas as pd

from reconciliation_engine import ReconciliationResult


class ReportGenerator:
    """Generates reconciliation reports."""

    def __init__(self):
        pass

    def generate_report(
        self,
        results: List[ReconciliationResult],
        summary_stats: Dict,
        anomaly_summary: Dict,
        rounding_analysis: Dict,
        recommendations: List[str],
        output_path: str = "output/reconciliation_report.txt",
    ):
        """Generate TXT reconciliation report."""

        print(f"Generating reconciliation report at {output_path}...")

        report_lines = []

        report_lines.append("=" * 80)
        report_lines.append(
            "PAYMENTS RECONCILIATION & ANOMALY DETECTION REPORT"
        )
        report_lines.append("=" * 80)
        report_lines.append(
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        report_lines.append(
            "Reconciliation Period: January 2026"
        )
        report_lines.append("")

        report_lines.append("EXECUTIVE SUMMARY")
        report_lines.append("-" * 80)

        report_lines.append(
            f"Total Transactions Processed: "
            f"{summary_stats.get('total_transactions', 0)}"
        )

        report_lines.append(
            f"Successfully Matched: "
            f"{summary_stats.get('matched_count', 0)} "
            f"({summary_stats.get('matched_percentage', 0):.1f}%)"
        )

        report_lines.append(
            f"Anomalies Detected: "
            f"{anomaly_summary.get('total_anomaly_records', 0)}"
        )

        report_lines.append(
            f"Anomaly Categories: "
            f"{anomaly_summary.get('total_anomaly_categories', 0)}"
        )

        report_lines.append("")

        report_lines.append("DATASET STATISTICS")
        report_lines.append("-" * 80)

        stats = {
            "Matched Transactions":
                summary_stats.get("matched_count", 0),
            "Missing Settlements":
                summary_stats.get("missing_settlement_count", 0),
            "Cross-Month Settlements":
                summary_stats.get("cross_month_count", 0),
            "Duplicate Entries":
                summary_stats.get("duplicate_count", 0),
            "Orphan Refunds":
                summary_stats.get("orphan_refund_count", 0),
            "Pending Transactions":
                summary_stats.get("pending_count", 0),
        }

        for k, v in stats.items():
            report_lines.append(f"{k}: {v}")

        report_lines.append("")

        report_lines.append("RECOMMENDATIONS")
        report_lines.append("-" * 80)

        for i, rec in enumerate(recommendations, start=1):
            report_lines.append(f"{i}. {rec}")

        report_lines.append("")
        report_lines.append("=" * 80)
        report_lines.append("END OF REPORT")
        report_lines.append("=" * 80)

        report_text = "\n".join(report_lines)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report_text)

        print(f"Report saved to {output_path}")

        return report_text

    def generate_excel_report(
        self,
        results,
        summary_stats,
        anomaly_summary,
        rounding_analysis,
        recommendations,
        output_path="output/reconciliation_results.xlsx"
    ):
        """Generate professional Excel report."""

        print(f"Generating Excel report at {output_path}...")

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        run_time = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        summary_df = pd.DataFrame([{
            "Run Time": run_time,
            "Total Transactions":
                summary_stats.get("total_transactions", 0),
            "Matched":
                summary_stats.get("matched_count", 0),
            "Pending":
                summary_stats.get("pending_count", 0),
            "Cross Month":
                summary_stats.get("cross_month_count", 0),
            "Duplicate Entries":
                summary_stats.get("duplicate_count", 0),
            "Orphan Refunds":
                summary_stats.get("orphan_refund_count", 0),
            "Rounding Difference":
                rounding_analysis.get("difference", 0),
        }])

        transaction_rows = []

        for result in results:
            transaction_rows.append({
                "transaction_id":
                    result.transaction_id,

                "status":
                    result.status,

                "transaction_amount":
                    result.transaction_amount,

                "settlement_amount":
                    result.settlement_amount,

                "settlement_date":
                    result.settlement_date,

                "reason":
                    result.reason,

                "recommendation":
                    result.recommendation
            })

        transactions_df = pd.DataFrame(
            transaction_rows
        )

        anomalies_df = transactions_df[
            transactions_df["status"] != "matched"
        ]

        rounding_df = pd.DataFrame([{
            "Transaction Total":
                rounding_analysis.get(
                    "total_transaction_amount", 0
                ),

            "Settlement Total":
                rounding_analysis.get(
                    "total_settlement_amount", 0
                ),

            "Difference":
                rounding_analysis.get(
                    "difference", 0
                ),

            "Category":
                rounding_analysis.get(
                    "category", "none"
                )
        }])

        recommendations_df = pd.DataFrame({
            "Recommendations":
                recommendations
        })

        run_history_df = pd.DataFrame([{
            "Run Time": run_time,
            "Records Processed":
                summary_stats.get(
                    "total_transactions", 0
                ),
            "Anomalies":
                anomaly_summary.get(
                    "total_anomaly_records", 0
                ),
            "Status": "Success"
        }])

        if os.path.exists(output_path):
            try:
                existing_history = pd.read_excel(
                    output_path,
                    sheet_name="Run_History"
                )

                run_history_df = pd.concat(
                    [existing_history, run_history_df],
                    ignore_index=True
                )
            except Exception:
                pass

        with pd.ExcelWriter(
            output_path,
            engine="openpyxl"
        ) as writer:

            summary_df.to_excel(
                writer,
                sheet_name="Executive_Summary",
                index=False
            )

            transactions_df.to_excel(
                writer,
                sheet_name="Transaction_Results",
                index=False
            )

            anomalies_df.to_excel(
                writer,
                sheet_name="Anomalies",
                index=False
            )

            rounding_df.to_excel(
                writer,
                sheet_name="Rounding_Analysis",
                index=False
            )

            recommendations_df.to_excel(
                writer,
                sheet_name="Recommendations",
                index=False
            )

            run_history_df.to_excel(
                writer,
                sheet_name="Run_History",
                index=False
            )

        print("Excel report generated successfully.")

    def print_summary(
        self,
        summary_stats,
        anomaly_summary,
        rounding_analysis
    ):
        """Print terminal summary."""

        print("\n" + "=" * 80)
        print("RECONCILIATION SUMMARY")
        print("=" * 80)

        print(
            f"Total Transactions: "
            f"{summary_stats.get('total_transactions', 0)}"
        )

        print(
            f"Matched: "
            f"{summary_stats.get('matched_count', 0)}"
        )

        print(
            f"Cross-Month Issues: "
            f"{summary_stats.get('cross_month_count', 0)}"
        )

        print(
            f"Duplicate Entries: "
            f"{summary_stats.get('duplicate_count', 0)}"
        )

        print(
            f"Orphan Refunds: "
            f"{summary_stats.get('orphan_refund_count', 0)}"
        )

        print(
            f"Pending: "
            f"{summary_stats.get('pending_count', 0)}"
        )

        print(
            f"Total Anomalies: "
            f"{anomaly_summary.get('total_anomaly_records', 0)}"
        )

        if rounding_analysis.get("has_discrepancy"):
            print(
                f"Rounding Discrepancy: "
                f"${rounding_analysis.get('difference', 0):.6f}"
            )

        print("=" * 80)