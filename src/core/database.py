import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from PySide6.QtCore import QObject, Signal
import json
import hashlib

class DatabaseManager(QObject):
    # Signals for UI updates
    connection_established = Signal()
    connection_failed = Signal(str)
    data_updated = Signal(str)  # table_name
    
    def __init__(self):
        super().__init__()
        self.conn = None
        self.db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'banking_security.db')
        
    @staticmethod
    def dict_factory(cursor, row):
        """Convert sqlite3.Row to dict"""
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d
        
    def connect(self) -> bool:
        """Establish database connection and initialize schema"""
        try:
            # Create data directory if it doesn't exist
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            # Connect to database
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # Enable column access by name
            
            # Enable foreign keys
            self.conn.execute("PRAGMA foreign_keys = ON")
            
            # Initialize schema
            self.init_schema()
            
            self.connection_established.emit()
            return True
            
        except Exception as e:
            self.connection_failed.emit(str(e))
            return False
    
    def init_schema(self):
        """Create database tables if they don't exist"""
        cursor = self.conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'analyst',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        """)
        
        # Transactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id TEXT UNIQUE NOT NULL,
                account_number TEXT NOT NULL,
                amount DECIMAL(10, 2) NOT NULL,
                transaction_type TEXT NOT NULL,
                merchant_name TEXT,
                merchant_category TEXT,
                location TEXT,
                timestamp TIMESTAMP NOT NULL,
                status TEXT DEFAULT 'pending',
                risk_score REAL DEFAULT 0.0,
                fraud_detected BOOLEAN DEFAULT 0,
                blocked BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for better performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_transactions_timestamp 
            ON transactions(timestamp DESC)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_transactions_risk_score 
            ON transactions(risk_score DESC)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_transactions_fraud 
            ON transactions(fraud_detected)
        """)
        
        # Fraud patterns table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fraud_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_name TEXT NOT NULL,
                pattern_type TEXT NOT NULL,
                description TEXT,
                parameters TEXT,  -- JSON string
                enabled BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Alerts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id TEXT,
                alert_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                message TEXT NOT NULL,
                details TEXT,  -- JSON string
                acknowledged BOOLEAN DEFAULT 0,
                acknowledged_by INTEGER,
                acknowledged_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id),
                FOREIGN KEY (acknowledged_by) REFERENCES users(id)
            )
        """)
        
        # Risk assessment logs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS risk_assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id TEXT NOT NULL,
                model_version TEXT,
                risk_factors TEXT,  -- JSON string
                final_score REAL NOT NULL,
                decision TEXT NOT NULL,
                processing_time_ms INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id)
            )
        """)
        
        # System metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                metric_unit TEXT,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.conn.commit()
        
        # Insert default data if tables are empty
        self.insert_default_data()
    
    def insert_default_data(self):
        """Insert default data for testing"""
        cursor = self.conn.cursor()
        
        # Check if we have any users
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            # Create default admin user (password: admin123)
            password_hash = hashlib.sha256("admin123".encode()).hexdigest()
            cursor.execute("""
                INSERT INTO users (username, password_hash, role) 
                VALUES (?, ?, ?)
            """, ("admin", password_hash, "admin"))
        
        # Check if we have any fraud patterns
        cursor.execute("SELECT COUNT(*) FROM fraud_patterns")
        if cursor.fetchone()[0] == 0:
            patterns = [
                {
                    "name": "High Amount Transaction",
                    "type": "amount_based",
                    "description": "Flags transactions above threshold",
                    "parameters": {"threshold": 10000, "currency": "USD"}
                },
                {
                    "name": "Rapid Sequential Transactions",
                    "type": "velocity_based",
                    "description": "Multiple transactions in short time",
                    "parameters": {"max_transactions": 5, "time_window_minutes": 10}
                },
                {
                    "name": "Geographic Anomaly",
                    "type": "location_based",
                    "description": "Transactions from unusual locations",
                    "parameters": {"baseline_radius_km": 100}
                },
                {
                    "name": "Merchant Category Risk",
                    "type": "merchant_based",
                    "description": "High-risk merchant categories",
                    "parameters": {"high_risk_categories": ["gambling", "crypto", "wire_transfer"]}
                },
                {
                    "name": "Time-based Anomaly",
                    "type": "temporal_based",
                    "description": "Transactions at unusual hours",
                    "parameters": {"suspicious_hours": [0, 1, 2, 3, 4, 5]}
                }
            ]
            
            for pattern in patterns:
                cursor.execute("""
                    INSERT INTO fraud_patterns (pattern_name, pattern_type, description, parameters)
                    VALUES (?, ?, ?, ?)
                """, (pattern["name"], pattern["type"], pattern["description"], 
                     json.dumps(pattern["parameters"])))
        
        self.conn.commit()
    
    def get_metrics_summary(self) -> Dict:
        """Get summary of key metrics"""
        if not self.conn:
            return {}
            
        cursor = self.conn.cursor()
        
        # Total transactions
        cursor.execute("SELECT COUNT(*) FROM transactions")
        total_transactions = cursor.fetchone()[0]
        
        # Fraud detected
        cursor.execute("SELECT COUNT(*) FROM transactions WHERE fraud_detected = 1")
        fraud_count = cursor.fetchone()[0]
        
        # Blocked transactions
        cursor.execute("SELECT COUNT(*) FROM transactions WHERE blocked = 1")
        blocked_count = cursor.fetchone()[0]
        
        # Average risk score
        cursor.execute("SELECT AVG(risk_score) FROM transactions WHERE risk_score > 0")
        avg_risk = cursor.fetchone()[0] or 0.0
        
        return {
            "total_transactions": total_transactions,
            "fraud_detected": fraud_count,
            "blocked_transactions": blocked_count,
            "average_risk_score": round(avg_risk, 2)
        }
    
    def add_transaction(self, transaction_data: Dict) -> bool:
        """Add a new transaction to the database"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO transactions (
                    transaction_id, account_number, amount, transaction_type,
                    merchant_name, merchant_category, location, timestamp,
                    status, risk_score, fraud_detected, blocked
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                transaction_data.get('transaction_id'),
                transaction_data.get('account_number'),
                transaction_data.get('amount'),
                transaction_data.get('transaction_type'),
                transaction_data.get('merchant_name'),
                transaction_data.get('merchant_category'),
                transaction_data.get('location'),
                transaction_data.get('timestamp'),
                transaction_data.get('status', 'pending'),
                transaction_data.get('risk_score', 0.0),
                transaction_data.get('fraud_detected', False),
                transaction_data.get('blocked', False)
            ))
            self.conn.commit()
            self.data_updated.emit('transactions')
            return True
        except Exception as e:
            print(f"Error adding transaction: {e}")
            return False
    
    def get_recent_transactions(self, limit: int = 100) -> List[Dict]:
        """Get recent transactions"""
        if not self.conn:
            return []
            
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM transactions 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (limit,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_fraud_patterns(self, enabled_only: bool = True) -> List[Dict]:
        """Get fraud detection patterns"""
        if not self.conn:
            return []
            
        cursor = self.conn.cursor()
        query = "SELECT * FROM fraud_patterns"
        if enabled_only:
            query += " WHERE enabled = 1"
            
        cursor.execute(query)
        patterns = []
        for row in cursor.fetchall():
            pattern = dict(row)
            pattern['parameters'] = json.loads(pattern['parameters'])
            patterns.append(pattern)
            
        return patterns
    
    def create_alert(self, alert_data: Dict) -> bool:
        """Create a new alert"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO alerts (
                    transaction_id, alert_type, severity, message, details
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                alert_data.get('transaction_id'),
                alert_data.get('alert_type'),
                alert_data.get('severity'),
                alert_data.get('message'),
                json.dumps(alert_data.get('details', {}))
            ))
            self.conn.commit()
            self.data_updated.emit('alerts')
            return True
        except Exception as e:
            print(f"Error creating alert: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None