"""
Populate the database with test transaction data
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.database import DatabaseManager
from core.transaction_generator import TransactionGenerator
from datetime import datetime

def populate_database():
    print("Populating database with test data...")
    
    # Create database manager
    db = DatabaseManager()
    
    # Connect to database
    if not db.connect():
        print("Failed to connect to database")
        return
        
    print("Database connected successfully")
    
    # Generate transactions
    print("Generating 500 test transactions...")
    transactions = TransactionGenerator.generate_batch(500)
    
    # Add some suspicious patterns
    print("Adding suspicious transaction patterns...")
    suspicious = TransactionGenerator.generate_suspicious_pattern()
    transactions.extend(suspicious)
    
    # Insert transactions
    success_count = 0
    for i, transaction in enumerate(transactions):
        if db.add_transaction(transaction):
            success_count += 1
        
        if (i + 1) % 50 == 0:
            print(f"Processed {i + 1} transactions...")
    
    print(f"\nSuccessfully added {success_count} transactions to the database")
    
    # Get summary
    metrics = db.get_metrics_summary()
    print("\nDatabase Summary:")
    print(f"- Total Transactions: {metrics['total_transactions']}")
    print(f"- Fraud Detected: {metrics['fraud_detected']}")
    print(f"- Blocked Transactions: {metrics['blocked_transactions']}")
    print(f"- Average Risk Score: {metrics['average_risk_score']}")
    
    # Close database
    db.close()
    print("\nDatabase populated successfully!")

if __name__ == "__main__":
    populate_database()