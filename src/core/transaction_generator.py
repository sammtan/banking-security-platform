import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, List

class TransactionGenerator:
    """Generate realistic banking transaction data for testing"""
    
    MERCHANTS = {
        "grocery": ["Walmart", "Target", "Kroger", "Whole Foods", "Safeway"],
        "gas": ["Shell", "Chevron", "Exxon", "BP", "Mobil"],
        "restaurant": ["McDonald's", "Starbucks", "Subway", "Chipotle", "Pizza Hut"],
        "online": ["Amazon", "eBay", "Netflix", "Spotify", "Apple Store"],
        "utilities": ["Electric Company", "Water Services", "Internet Provider", "Gas Company"],
        "entertainment": ["AMC Theaters", "Dave & Busters", "TopGolf", "Bowling Alley"],
        "travel": ["United Airlines", "Marriott Hotel", "Uber", "Lyft", "Hertz"],
        "healthcare": ["CVS Pharmacy", "Walgreens", "City Hospital", "Dental Clinic"],
        "gambling": ["Online Casino", "Sports Betting", "Lottery", "Poker Site"],
        "crypto": ["Coinbase", "Binance", "Crypto Exchange", "Bitcoin ATM"],
        "wire_transfer": ["International Wire", "Domestic Wire", "Money Transfer"]
    }
    
    LOCATIONS = [
        "New York, NY", "Los Angeles, CA", "Chicago, IL", "Houston, TX",
        "Phoenix, AZ", "Philadelphia, PA", "San Antonio, TX", "San Diego, CA",
        "Dallas, TX", "San Jose, CA", "Austin, TX", "Jacksonville, FL",
        "Online", "ATM Location", "Mobile App"
    ]
    
    TRANSACTION_TYPES = ["debit", "credit", "transfer", "withdrawal", "deposit"]
    
    @staticmethod
    def generate_transaction(account_number: str = None, timestamp: datetime = None) -> Dict:
        """Generate a single transaction"""
        
        # Random merchant category
        category = random.choice(list(TransactionGenerator.MERCHANTS.keys()))
        merchant = random.choice(TransactionGenerator.MERCHANTS[category])
        
        # Transaction amount based on category
        amount_ranges = {
            "grocery": (20, 300),
            "gas": (30, 80),
            "restaurant": (10, 100),
            "online": (15, 500),
            "utilities": (50, 300),
            "entertainment": (20, 200),
            "travel": (100, 2000),
            "healthcare": (20, 500),
            "gambling": (50, 5000),
            "crypto": (100, 10000),
            "wire_transfer": (500, 50000)
        }
        
        min_amount, max_amount = amount_ranges.get(category, (10, 1000))
        amount = round(random.uniform(min_amount, max_amount), 2)
        
        # Generate risk score based on various factors
        risk_factors = {
            "amount": min(amount / 10000, 0.3),  # Higher amounts = higher risk
            "category": {
                "gambling": 0.4,
                "crypto": 0.35,
                "wire_transfer": 0.45,
                "travel": 0.15,
                "online": 0.1
            }.get(category, 0.05),
            "time": 0.2 if timestamp and (timestamp.hour < 6 or timestamp.hour > 23) else 0,
            "random": random.uniform(0, 0.2)
        }
        
        risk_score = min(sum(risk_factors.values()), 1.0)
        
        # Determine if fraud based on risk score
        fraud_detected = risk_score > 0.7 and random.random() > 0.5
        blocked = fraud_detected and random.random() > 0.3
        
        transaction = {
            "transaction_id": f"TXN{uuid.uuid4().hex[:12].upper()}",
            "account_number": account_number or f"****{random.randint(1000, 9999)}",
            "amount": amount,
            "transaction_type": random.choice(TransactionGenerator.TRANSACTION_TYPES),
            "merchant_name": merchant,
            "merchant_category": category,
            "location": random.choice(TransactionGenerator.LOCATIONS),
            "timestamp": timestamp or datetime.now(),
            "status": "blocked" if blocked else "completed",
            "risk_score": round(risk_score, 3),
            "fraud_detected": fraud_detected,
            "blocked": blocked
        }
        
        return transaction
    
    @staticmethod
    def generate_batch(count: int = 100, start_date: datetime = None) -> List[Dict]:
        """Generate a batch of transactions"""
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
            
        transactions = []
        
        # Generate some account numbers
        accounts = [f"****{random.randint(1000, 9999)}" for _ in range(10)]
        
        for i in range(count):
            # Random timestamp within the date range
            time_offset = timedelta(
                days=random.randint(0, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            timestamp = start_date + time_offset
            
            # Pick a random account
            account = random.choice(accounts)
            
            transaction = TransactionGenerator.generate_transaction(account, timestamp)
            transactions.append(transaction)
            
        # Sort by timestamp
        transactions.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return transactions
    
    @staticmethod
    def generate_suspicious_pattern() -> List[Dict]:
        """Generate transactions that follow suspicious patterns"""
        patterns = []
        account = f"****{random.randint(1000, 9999)}"
        base_time = datetime.now()
        
        # Pattern 1: Rapid sequential transactions
        for i in range(5):
            transaction = TransactionGenerator.generate_transaction(account, base_time)
            transaction['risk_score'] = min(0.8 + (i * 0.05), 1.0)
            transaction['fraud_detected'] = True
            patterns.append(transaction)
            base_time += timedelta(minutes=random.randint(1, 5))
            
        return patterns