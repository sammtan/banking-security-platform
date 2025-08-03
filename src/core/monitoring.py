from PySide6.QtCore import QObject, QTimer, Signal, QThread
from datetime import datetime
import random
from typing import Dict, List
from core.transaction_generator import TransactionGenerator
from core.ai_model import FraudDetectionModel

class MonitoringEngine(QObject):
    """Real-time transaction monitoring engine"""
    
    # Signals
    transaction_received = Signal(dict)
    fraud_detected = Signal(dict)
    metrics_updated = Signal(dict)
    status_changed = Signal(str)  # 'active' or 'inactive'
    
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.is_monitoring = False
        self.monitoring_timer = QTimer()
        self.monitoring_timer.timeout.connect(self.process_transaction)
        
        # Fraud detection patterns from database
        self.fraud_patterns = []
        
        # AI Model
        self.ai_model = FraudDetectionModel()
        self.ai_model_loaded = self.ai_model.load_model()
        
        # Transaction history for AI model context
        self.recent_transactions = []
        
    def start_monitoring(self):
        """Start real-time monitoring"""
        if self.is_monitoring:
            return
            
        # Load fraud patterns
        self.fraud_patterns = self.db.get_fraud_patterns(enabled_only=True)
        
        self.is_monitoring = True
        self.status_changed.emit('active')
        
        # Start generating transactions every 1-3 seconds
        self.monitoring_timer.start(random.randint(1000, 3000))
        
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring_timer.stop()
        self.is_monitoring = False
        self.status_changed.emit('inactive')
        
    def process_transaction(self):
        """Process a new transaction"""
        if not self.is_monitoring:
            return
            
        # Generate a new transaction
        transaction = TransactionGenerator.generate_transaction()
        
        # Apply fraud detection
        risk_score, fraud_reasons = self.analyze_transaction(transaction)
        transaction['risk_score'] = risk_score
        transaction['fraud_detected'] = risk_score > 0.7
        transaction['blocked'] = transaction['fraud_detected'] and risk_score > 0.85
        
        # Save to database
        if self.db.add_transaction(transaction):
            self.transaction_received.emit(transaction)
            
            # Emit fraud alert if detected
            if transaction['fraud_detected']:
                alert_data = {
                    'transaction_id': transaction['transaction_id'],
                    'alert_type': 'fraud_detection',
                    'severity': 'high' if risk_score > 0.9 else 'medium',
                    'message': f"Suspicious transaction detected: {', '.join(fraud_reasons)}",
                    'details': {
                        'risk_score': risk_score,
                        'reasons': fraud_reasons,
                        'amount': transaction['amount'],
                        'merchant': transaction['merchant_name']
                    }
                }
                self.db.create_alert(alert_data)
                self.fraud_detected.emit(alert_data)
        
        # Update metrics
        metrics = self.db.get_metrics_summary()
        self.metrics_updated.emit(metrics)
        
        # Schedule next transaction
        if self.is_monitoring:
            self.monitoring_timer.setInterval(random.randint(1000, 3000))
            
    def analyze_transaction(self, transaction: Dict) -> tuple:
        """Analyze transaction for fraud using AI model and rule-based patterns"""
        risk_score = 0.0
        fraud_reasons = []
        
        # First, use AI model if available
        ai_score = 0.0
        ai_reasons = []
        if self.ai_model_loaded:
            try:
                # Use recent transaction history for context
                ai_score, ai_reasons = self.ai_model.predict(transaction, self.recent_transactions)
                fraud_reasons.extend(ai_reasons)
            except Exception as e:
                print(f"AI model prediction error: {e}")
                
        # Then apply rule-based patterns
        rule_score = 0.0
        for pattern in self.fraud_patterns:
            pattern_score = 0.0
            params = pattern['parameters']
            
            if pattern['pattern_type'] == 'amount_based':
                threshold = params.get('threshold', 10000)
                if transaction['amount'] > threshold:
                    pattern_score = min(transaction['amount'] / (threshold * 2), 1.0)
                    fraud_reasons.append(f"High amount: ${transaction['amount']:.2f}")
                    
            elif pattern['pattern_type'] == 'merchant_based':
                high_risk_categories = params.get('high_risk_categories', [])
                if transaction['merchant_category'] in high_risk_categories:
                    pattern_score = 0.8
                    fraud_reasons.append(f"High-risk merchant: {transaction['merchant_category']}")
                    
            elif pattern['pattern_type'] == 'temporal_based':
                suspicious_hours = params.get('suspicious_hours', [])
                hour = transaction['timestamp'].hour
                if hour in suspicious_hours:
                    pattern_score = 0.6
                    fraud_reasons.append(f"Unusual time: {hour:02d}:00")
                    
            elif pattern['pattern_type'] == 'location_based':
                if transaction['location'] not in ['Online', 'Mobile App'] and 'foreign' in transaction['location'].lower():
                    pattern_score = 0.7
                    fraud_reasons.append(f"Foreign location: {transaction['location']}")
            
            rule_score = max(rule_score, pattern_score)
        
        # Combine AI and rule-based scores (weighted average)
        if self.ai_model_loaded:
            risk_score = 0.7 * ai_score + 0.3 * rule_score  # AI has higher weight
        else:
            risk_score = rule_score
            
        # Add transaction to history for future predictions
        self.recent_transactions.append(transaction)
        if len(self.recent_transactions) > 100:  # Keep only recent 100 transactions
            self.recent_transactions.pop(0)
        
        # Remove duplicate reasons
        fraud_reasons = list(set(fraud_reasons))
        
        return round(risk_score, 3), fraud_reasons