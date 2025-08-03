import numpy as np
import joblib
import os
from datetime import datetime
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import pandas as pd
from typing import Dict, List, Tuple, Optional

class FraudDetectionModel:
    """AI/ML model for fraud detection using Isolation Forest"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = [
            'amount_normalized',
            'hour_of_day',
            'day_of_week',
            'is_weekend',
            'merchant_risk_score',
            'location_risk_score',
            'transaction_velocity',
            'amount_deviation'
        ]
        self.model_path = os.path.join(os.path.dirname(__file__), '..', '..', 'models')
        self.is_trained = False
        
    def extract_features(self, transaction: Dict, transaction_history: List[Dict] = None) -> np.ndarray:
        """Extract features from transaction data"""
        features = []
        
        # Amount normalized (log scale to handle outliers)
        amount = float(transaction.get('amount', 0))
        amount_normalized = np.log1p(amount)
        features.append(amount_normalized)
        
        # Time-based features
        timestamp = datetime.fromisoformat(str(transaction.get('timestamp', datetime.now())))
        hour_of_day = timestamp.hour
        day_of_week = timestamp.weekday()
        is_weekend = 1 if day_of_week >= 5 else 0
        
        features.extend([hour_of_day, day_of_week, is_weekend])
        
        # Merchant risk score (based on category)
        high_risk_merchants = ['gambling', 'crypto', 'wire_transfer', 'cash_advance']
        merchant_category = transaction.get('merchant_category', '').lower()
        merchant_risk_score = 1.0 if merchant_category in high_risk_merchants else 0.3
        features.append(merchant_risk_score)
        
        # Location risk score (simplified - would use geolocation API in production)
        location = transaction.get('location', '')
        location_risk_score = 0.8 if 'International' in location else 0.2
        features.append(location_risk_score)
        
        # Transaction velocity (number of transactions in last hour)
        transaction_velocity = 1  # Default
        if transaction_history:
            recent_count = sum(1 for t in transaction_history[-10:] 
                             if (timestamp - datetime.fromisoformat(str(t['timestamp']))).seconds < 3600)
            transaction_velocity = min(recent_count, 10) / 10.0
        features.append(transaction_velocity)
        
        # Amount deviation from average
        amount_deviation = 0.5  # Default
        if transaction_history and len(transaction_history) > 5:
            amounts = [float(t.get('amount', 0)) for t in transaction_history[-20:]]
            avg_amount = np.mean(amounts)
            std_amount = np.std(amounts)
            if std_amount > 0:
                amount_deviation = abs(amount - avg_amount) / std_amount
                amount_deviation = min(amount_deviation, 3.0) / 3.0  # Normalize to [0, 1]
        features.append(amount_deviation)
        
        return np.array(features).reshape(1, -1)
        
    def train(self, transactions: List[Dict]):
        """Train the model on historical transaction data"""
        if not transactions:
            raise ValueError("No training data provided")
            
        # Extract features for all transactions
        X = []
        for i, transaction in enumerate(transactions):
            # Get transaction history for velocity and deviation features
            history = transactions[:i] if i > 0 else []
            features = self.extract_features(transaction, history)
            X.append(features[0])
            
        X = np.array(X)
        
        # Fit scaler
        X_scaled = self.scaler.fit_transform(X)
        
        # Train Isolation Forest
        # contamination: expected proportion of outliers (fraud)
        self.model = IsolationForest(
            contamination=0.1,  # Assume 10% fraud rate
            random_state=42,
            n_estimators=100
        )
        self.model.fit(X_scaled)
        
        self.is_trained = True
        
        # Save model
        self.save_model()
        
    def predict(self, transaction: Dict, transaction_history: List[Dict] = None) -> Tuple[float, List[str]]:
        """Predict fraud probability for a transaction"""
        if not self.is_trained:
            # Use rule-based fallback if model not trained
            return self.rule_based_prediction(transaction)
            
        # Extract features
        features = self.extract_features(transaction, transaction_history)
        features_scaled = self.scaler.transform(features)
        
        # Get anomaly score (-1 for anomaly, 1 for normal)
        prediction = self.model.predict(features_scaled)[0]
        anomaly_score = self.model.score_samples(features_scaled)[0]
        
        # Convert to probability (0-1 range)
        # Lower scores indicate higher fraud probability
        fraud_probability = 1 / (1 + np.exp(anomaly_score))
        
        # Get fraud reasons
        reasons = self.get_fraud_reasons(transaction, features[0], fraud_probability)
        
        return fraud_probability, reasons
        
    def rule_based_prediction(self, transaction: Dict) -> Tuple[float, List[str]]:
        """Fallback rule-based prediction when model is not trained"""
        risk_score = 0.0
        reasons = []
        
        # Check amount
        amount = float(transaction.get('amount', 0))
        if amount > 5000:
            risk_score += 0.3
            reasons.append(f"High transaction amount: ${amount:,.2f}")
        elif amount > 10000:
            risk_score += 0.5
            reasons.append(f"Very high transaction amount: ${amount:,.2f}")
            
        # Check merchant category
        merchant_category = transaction.get('merchant_category', '').lower()
        if merchant_category in ['gambling', 'crypto', 'wire_transfer']:
            risk_score += 0.4
            reasons.append(f"High-risk merchant category: {merchant_category}")
            
        # Check time
        timestamp = datetime.fromisoformat(str(transaction.get('timestamp', datetime.now())))
        if timestamp.hour < 6 or timestamp.hour > 23:
            risk_score += 0.2
            reasons.append(f"Unusual transaction time: {timestamp.strftime('%H:%M')}")
            
        # Check location
        if 'International' in transaction.get('location', ''):
            risk_score += 0.3
            reasons.append("International transaction")
            
        # Ensure score is in [0, 1] range
        risk_score = min(risk_score, 1.0)
        
        return risk_score, reasons
        
    def get_fraud_reasons(self, transaction: Dict, features: np.ndarray, fraud_probability: float) -> List[str]:
        """Generate human-readable fraud reasons"""
        reasons = []
        
        # Amount-based reasons
        amount = float(transaction.get('amount', 0))
        if features[0] > 8:  # log(3000) ≈ 8
            reasons.append(f"High transaction amount: ${amount:,.2f}")
            
        # Time-based reasons
        hour = int(features[1])
        if hour < 6 or hour > 23:
            reasons.append(f"Unusual transaction time: {hour:02d}:00")
            
        # Merchant risk
        if features[4] > 0.7:
            reasons.append(f"High-risk merchant: {transaction.get('merchant_category', 'Unknown')}")
            
        # Location risk
        if features[5] > 0.7:
            reasons.append(f"Risky location: {transaction.get('location', 'Unknown')}")
            
        # Velocity
        if features[6] > 0.7:
            reasons.append("High transaction velocity")
            
        # Amount deviation
        if features[7] > 0.7:
            reasons.append("Amount significantly deviates from normal pattern")
            
        # Add ML confidence
        if fraud_probability > 0.8:
            reasons.append(f"AI model confidence: {fraud_probability:.1%}")
            
        return reasons
        
    def save_model(self):
        """Save trained model to disk"""
        os.makedirs(self.model_path, exist_ok=True)
        
        model_file = os.path.join(self.model_path, 'fraud_detection_model.pkl')
        scaler_file = os.path.join(self.model_path, 'fraud_detection_scaler.pkl')
        
        joblib.dump(self.model, model_file)
        joblib.dump(self.scaler, scaler_file)
        
    def load_model(self) -> bool:
        """Load model from disk if available"""
        model_file = os.path.join(self.model_path, 'fraud_detection_model.pkl')
        scaler_file = os.path.join(self.model_path, 'fraud_detection_scaler.pkl')
        
        if os.path.exists(model_file) and os.path.exists(scaler_file):
            try:
                self.model = joblib.load(model_file)
                self.scaler = joblib.load(scaler_file)
                self.is_trained = True
                return True
            except Exception as e:
                print(f"Error loading model: {e}")
                return False
        return False
        
    def update_model(self, new_transactions: List[Dict]):
        """Update model with new transaction data (incremental learning)"""
        # For Isolation Forest, we need to retrain on all data
        # In production, you might use online learning algorithms
        if self.is_trained and new_transactions:
            # This is a simplified approach - ideally, you'd keep a buffer of recent transactions
            self.train(new_transactions)