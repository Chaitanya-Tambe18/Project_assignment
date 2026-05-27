"""
Data Generator for Payments Reconciliation System

Generates synthetic transaction and settlement data with intentional anomalies
for testing the reconciliation engine.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Tuple
import random


class DataGenerator:
    """Generates synthetic payment transaction and settlement data."""
    
    def __init__(self, seed: int = 42):
        """Initialize the data generator with a random seed for reproducibility."""
        np.random.seed(seed)
        random.seed(seed)
        
    def generate_transactions(self, num_records: int = 200) -> pd.DataFrame:
        """
        Generate synthetic transaction data for January 2026.
        
        Args:
            num_records: Number of transaction records to generate
            
        Returns:
            DataFrame with transaction data
        """
        print(f"Generating {num_records} transaction records...")
        
        # Generate dates throughout January 2026
        start_date = datetime(2026, 1, 1)
        end_date = datetime(2026, 1, 31)
        
        transactions = []
        transaction_ids = []
        
        for i in range(num_records):
            # Generate unique transaction ID
            transaction_id = f"TXN{i+1:06d}"
            transaction_ids.append(transaction_id)
            
            # Random customer ID
            customer_id = f"CUST{random.randint(1, 50):04d}"
            
            # Random date in January
            days_diff = random.randint(0, 30)
            transaction_date = start_date + timedelta(days=days_diff)
            
            # Random amount between $10 and $1000
            # Realistic payment amounts (₹5,000 to ₹1,50,000)
            amount = round(random.uniform(5000, 150000), 2)

            # Make some values realistic business-like numbers
            if random.random() < 0.35:
                amount = random.choice([
                    10000,
                    15000,
                    20000,
                    25000,
                    30000,
                    35000,
                    40000,
                    45000,
                    50000,
                    75000,
                    100000
                ])
            
            # Currency (all USD for simplicity)
            currency = "USD"
            
            # Transaction type (mostly payments, some refunds)
            is_refund = random.random() < 0.08  # 8% refund rate
            if is_refund and i > 10:  # Ensure some transactions exist for refunds
                trans_type = "refund"
                # Reference a random earlier transaction
                original_txn_idx = random.randint(0, min(i-1, len(transaction_ids)-1))
                original_transaction_id = transaction_ids[original_txn_idx]
                status = "completed"
            else:
                trans_type = "payment"
                original_transaction_id = None
                status = random.choice(["completed", "completed", "completed", "pending"])
            
            transactions.append({
                "transaction_id": transaction_id,
                "customer_id": customer_id,
                "transaction_date": transaction_date.strftime("%Y-%m-%d"),
                "amount": amount,
                "currency": currency,
                "type": trans_type,
                "original_transaction_id": original_transaction_id,
                "status": status
            })
        
        df = pd.DataFrame(transactions)
        print(f"Generated {len(df)} transactions")
        return df
    
    def generate_settlements(self, transactions: pd.DataFrame) -> pd.DataFrame:
        """
        Generate synthetic settlement data based on transactions.
        
        Args:
            transactions: DataFrame of transactions
            
        Returns:
            DataFrame with settlement data
        """
        print("Generating settlement records...")
        
        settlements = []
        settlement_id_counter = 1
        
        # Process each transaction
        for _, txn in transactions.iterrows():
            # Skip pending transactions (they won't have settlements yet)
            if txn["status"] == "pending":
                continue
                
            # Skip refunds for now (they're handled separately)
            if txn["type"] == "refund":
                continue
            
            # Determine settlement date (1-2 days later normally)
            txn_date = datetime.strptime(txn["transaction_date"], "%Y-%m-%d")
            
            # Inject cross-month settlement anomaly
            # Transactions on Jan 31 that settle on Feb 2
            is_cross_month = (txn_date.day == 31 and random.random() < 0.3)
            
            if is_cross_month:
                settlement_date = txn_date + timedelta(days=2)  # Feb 2
            else:
                # Normal settlement: 1-2 days
                settlement_delay = random.randint(1, 2)
                settlement_date = txn_date + timedelta(days=settlement_delay)
            
            # Inject rounding anomaly (tiny decimal differences)
            # Only affects some transactions
            is_rounding_anomaly = random.random() < 0.15
            if is_rounding_anomaly:
                # Add tiny decimal that only shows in aggregation
                settled_amount = round(txn["amount"] + random.choice([0.005, -0.005]), 3)
            else:
                settled_amount = txn["amount"]
            
            # Settlement status
            settlement_status = "settled"
            
            # Bank reference
            bank_reference = f"BANK{settlement_id_counter:08d}"
            
            settlements.append({
                "settlement_id": f"STL{settlement_id_counter:06d}",
                "transaction_id": txn["transaction_id"],
                "settlement_date": settlement_date.strftime("%Y-%m-%d"),
                "settled_amount": settled_amount,
                "settlement_status": settlement_status,
                "bank_reference": bank_reference
            })
            
            settlement_id_counter += 1
        
        # Inject duplicate settlement anomaly
        # Duplicate one of the existing settlements
        if len(settlements) > 10:
            duplicate_idx = random.randint(0, len(settlements) - 1)
            duplicate_settlement = settlements[duplicate_idx].copy()
            duplicate_settlement["settlement_id"] = f"STL{settlement_id_counter:06d}"
            duplicate_settlement["bank_reference"] = f"BANK{settlement_id_counter:08d}"
            settlements.append(duplicate_settlement)
            settlement_id_counter += 1
            print(f"Injected duplicate settlement for transaction: {duplicate_settlement['transaction_id']}")
        
        # Process refunds
        for _, txn in transactions.iterrows():
            if txn["type"] == "refund" and txn["status"] == "completed":
                txn_date = datetime.strptime(txn["transaction_date"], "%Y-%m-%d")
                settlement_date = txn_date + timedelta(days=random.randint(1, 2))
                
                settlements.append({
                    "settlement_id": f"STL{settlement_id_counter:06d}",
                    "transaction_id": txn["transaction_id"],
                    "settlement_date": settlement_date.strftime("%Y-%m-%d"),
                    "settled_amount": -txn["amount"],  # Refunds are negative
                    "settlement_status": "settled",
                    "bank_reference": f"BANK{settlement_id_counter:08d}"
                })
                settlement_id_counter += 1
        
        # Inject orphan refund anomaly
        # Create a refund that references a non-existent transaction
        orphan_refund_txn = {
            "transaction_id": "TXNORPH001",
            "customer_id": "CUST9999",
            "transaction_date": "2026-01-15",
            "amount": 150.00,
            "currency": "USD",
            "type": "refund",
            "original_transaction_id": "TXN999999",  # Non-existent
            "status": "completed"
        }
        
        # Add to transactions
        transactions = pd.concat([transactions, pd.DataFrame([orphan_refund_txn])], ignore_index=True)
        
        # Add settlement for the orphan refund
        settlements.append({
            "settlement_id": f"STL{settlement_id_counter:06d}",
            "transaction_id": "TXNORPH001",
            "settlement_date": "2026-01-17",
            "settled_amount": -150.00,
            "settlement_status": "settled",
            "bank_reference": f"BANK{settlement_id_counter:08d}"
        })
        
        print(f"Injected orphan refund: TXNORPH001 referencing non-existent TXN999999")
        
        df_settlements = pd.DataFrame(settlements)
        print(f"Generated {len(df_settlements)} settlement records")
        
        return transactions, df_settlements
    
    def generate_data(self, num_transactions: int = 200) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Generate complete transaction and settlement datasets.
        
        Args:
            num_transactions: Number of transactions to generate
            
        Returns:
            Tuple of (transactions_df, settlements_df)
        """
        transactions = self.generate_transactions(num_transactions)
        transactions, settlements = self.generate_settlements(transactions)
        
        return transactions, settlements
    
    def save_data(self, transactions: pd.DataFrame, settlements: pd.DataFrame, 
                  output_dir: str = "../data"):
        """
        Save generated data to CSV files.
        
        Args:
            transactions: DataFrame of transactions
            settlements: DataFrame of settlements
            output_dir: Directory to save files
        """
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        transactions_path = f"{output_dir}/transactions.csv"
        settlements_path = f"{output_dir}/settlements.csv"
        
        transactions.to_csv(transactions_path, index=False)
        settlements.to_csv(settlements_path, index=False)
        
        print(f"Saved transactions to {transactions_path}")
        print(f"Saved settlements to {settlements_path}")


if __name__ == "__main__":
    generator = DataGenerator()
    transactions, settlements = generator.generate_data(200)
    generator.save_data(transactions, settlements)
    
    print("\n=== Data Generation Summary ===")
    print(f"Total transactions: {len(transactions)}")
    print(f"Total settlements: {len(settlements)}")
    print(f"Payment transactions: {len(transactions[transactions['type'] == 'payment'])}")
    print(f"Refund transactions: {len(transactions[transactions['type'] == 'refund'])}")
