#!/usr/bin/env python3
"""
Train the fraud detection AI model on historical transaction data
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.database import DatabaseManager
from core.ai_model import FraudDetectionModel
from datetime import datetime, timedelta
import random

def generate_training_data(db):
    """Generate synthetic training data for the model"""
    print("Generating synthetic training data...")
    
    transactions = []
    
    # Generate 1000 normal transactions
    for i in range(800):
        transaction = {
            'transaction_id': f'TRAIN_{i:06d}',
            'account_number': f'ACC{random.randint(1000, 9999)}',
            'amount': random.uniform(10, 500),
            'transaction_type': random.choice(['purchase', 'withdrawal', 'transfer']),
            'merchant_name': random.choice(['Amazon', 'Walmart', 'Target', 'Starbucks', 'Gas Station']),
            'merchant_category': random.choice(['retail', 'grocery', 'food', 'gas', 'entertainment']),
            'location': random.choice(['New York, NY', 'Los Angeles, CA', 'Chicago, IL', 'Houston, TX']),
            'timestamp': datetime.now() - timedelta(hours=random.randint(0, 720)),
            'status': 'completed',
            'risk_score': 0.0,
            'fraud_detected': False,
            'blocked': False
        }
        transactions.append(transaction)
    
    # Generate 200 fraudulent transactions
    for i in range(200):
        transaction = {
            'transaction_id': f'FRAUD_{i:06d}',
            'account_number': f'ACC{random.randint(1000, 9999)}',
            'amount': random.uniform(1000, 10000),  # Higher amounts
            'transaction_type': random.choice(['withdrawal', 'transfer', 'wire_transfer']),
            'merchant_name': random.choice(['Unknown Merchant', 'Foreign Exchange', 'Crypto Exchange']),
            'merchant_category': random.choice(['gambling', 'crypto', 'wire_transfer', 'cash_advance']),
            'location': random.choice(['International', 'Unknown', 'Offshore']),
            'timestamp': datetime.now() - timedelta(hours=random.randint(0, 72)),  # Recent
            'status': 'completed',
            'risk_score': 0.8,
            'fraud_detected': True,
            'blocked': random.choice([True, False])
        }
        
        # Make some transactions at unusual hours
        if random.random() > 0.5:
            transaction['timestamp'] = transaction['timestamp'].replace(hour=random.randint(0, 5))
            
        transactions.append(transaction)
    
    # Shuffle transactions
    random.shuffle(transactions)
    
    # Insert into database
    for transaction in transactions:
        db.create_transaction(transaction)
        
    print(f"Generated {len(transactions)} training transactions")
    return transactions

def main():
    """Main training function"""
    print("Banking Security Platform - AI Model Training")
    print("-" * 50)
    
    # Initialize database
    db = DatabaseManager()
    if not db.connect():
        print("Failed to connect to database")
        return
        
    # Check if we have enough data
    cursor = db.conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM transactions")
    count = cursor.fetchone()[0]
    
    if count < 100:
        print(f"Not enough data ({count} transactions). Generating synthetic data...")
        transactions = generate_training_data(db)
    else:
        print(f"Found {count} transactions in database")
        # Get all transactions for training
        cursor.execute("SELECT * FROM transactions ORDER BY timestamp")
        transactions = [dict(row) for row in cursor.fetchall()]
    
    # Initialize and train model
    print("\nTraining fraud detection model...")
    model = FraudDetectionModel()
    
    try:
        model.train(transactions)
        print("Model trained successfully!")
        
        # Test the model on a few transactions
        print("\nTesting model predictions:")
        print("-" * 30)
        
        test_transactions = [
            {
                'amount': 50,
                'merchant_category': 'retail',
                'location': 'New York, NY',
                'timestamp': datetime.now(),
                'transaction_type': 'purchase'
            },
            {
                'amount': 5000,
                'merchant_category': 'gambling',
                'location': 'International',
                'timestamp': datetime.now().replace(hour=3),
                'transaction_type': 'wire_transfer'
            }
        ]
        
        for i, test_tx in enumerate(test_transactions):
            score, reasons = model.predict(test_tx)
            print(f"\nTest Transaction {i+1}:")
            print(f"  Amount: ${test_tx['amount']}")
            print(f"  Category: {test_tx['merchant_category']}")
            print(f"  Location: {test_tx['location']}")
            print(f"  Risk Score: {score:.3f}")
            print(f"  Reasons: {', '.join(reasons) if reasons else 'None'}")
            
    except Exception as e:
        print(f"Error training model: {e}")
        
    print("\nTraining complete!")

if __name__ == "__main__":
    main()