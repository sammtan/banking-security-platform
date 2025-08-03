# Banking Security Platform - Programming Guide

## Development Setup

### Prerequisites
```bash
# Python 3.8+ required
python --version

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Project Structure
```
banking-security-platform/
├── src/
│   ├── main.py                 # Entry point
│   ├── core/                   # Business logic
│   │   ├── database.py         # Database operations
│   │   ├── monitoring.py       # Real-time monitoring
│   │   ├── ai_model.py         # ML model
│   │   ├── report_generator.py # Report generation
│   │   └── theme_manager.py    # UI theming
│   └── ui/                     # User interface
│       ├── main_window.py      # Main window
│       ├── pages/              # Application pages
│       └── widgets/            # Reusable widgets
├── scripts/                    # Utility scripts
├── data/                       # Database storage
└── docs/                       # Documentation
```

## Core Components

### 1. Database Manager

The `DatabaseManager` class handles all database operations with connection pooling and thread safety.

```python
from core.database import DatabaseManager

# Initialize database
db = DatabaseManager()
db.connect()

# Create a transaction
transaction_data = {
    'transaction_id': 'TXN123456',
    'amount': 150.00,
    'merchant_name': 'Amazon',
    'merchant_category': 'retail',
    'location': 'New York, NY'
}
db.create_transaction(transaction_data)

# Query transactions
recent_transactions = db.get_recent_transactions(limit=100)

# Get metrics
metrics = db.get_metrics_summary()
```

### 2. Monitoring Engine

The `MonitoringEngine` provides real-time transaction monitoring with fraud detection.

```python
from core.monitoring import MonitoringEngine

# Initialize monitoring
monitor = MonitoringEngine(db_manager)

# Connect to signals
monitor.transaction_received.connect(on_transaction)
monitor.fraud_detected.connect(on_fraud_alert)

# Start monitoring
monitor.start_monitoring()

# Signal handlers
def on_transaction(transaction):
    print(f"New transaction: {transaction['transaction_id']}")
    
def on_fraud_alert(alert_data):
    print(f"Fraud detected: {alert_data['transaction_id']}")
```

### 3. AI Model Integration

The fraud detection model uses scikit-learn's Isolation Forest algorithm.

```python
from core.ai_model import FraudDetectionModel

# Initialize model
model = FraudDetectionModel()

# Train on historical data
transactions = db.get_all_transactions()
model.train(transactions)

# Make predictions
transaction = {
    'amount': 5000,
    'merchant_category': 'gambling',
    'location': 'Offshore',
    'timestamp': datetime.now()
}
risk_score, reasons = model.predict(transaction)
```

### 4. Report Generation

Generate reports in multiple formats:

```python
from core.report_generator import ReportGenerator

# Initialize generator
generator = ReportGenerator(db_manager)

# Generate transaction report
pdf_buffer = generator.generate_transaction_report(
    start_date='2024-01-01',
    end_date='2024-01-31',
    format='pdf'
)

# Save to file
with open('report.pdf', 'wb') as f:
    f.write(pdf_buffer.read())

# Generate fraud report
fraud_report = generator.generate_fraud_report(format='csv')
```

## UI Development

### 1. Creating a New Page

```python
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from core.theme_manager import ThemeManager

class CustomPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Add header
        header = QLabel("Custom Page")
        header.setObjectName("heading")
        layout.addWidget(header)
        
        # Add content
        # ...
```

### 2. Creating Custom Widgets

```python
from PySide6.QtWidgets import QFrame
from PySide6.QtCore import Signal

class CustomWidget(QFrame):
    # Define signals
    value_changed = Signal(float)
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {ThemeManager.COLORS['surface']};
                border-radius: 8px;
                padding: 16px;
            }}
        """)
```

### 3. Using Signals and Slots

```python
# Emit signal
self.value_changed.emit(new_value)

# Connect to slot
widget.value_changed.connect(self.on_value_changed)

# Slot implementation
def on_value_changed(self, value):
    print(f"Value changed to: {value}")
```

## Best Practices

### 1. Error Handling

```python
try:
    result = db.execute_query(query)
except DatabaseError as e:
    logger.error(f"Database error: {e}")
    QMessageBox.critical(self, "Error", str(e))
except Exception as e:
    logger.exception("Unexpected error")
    QMessageBox.critical(self, "Error", "An unexpected error occurred")
```

### 2. Thread Safety

```python
from PySide6.QtCore import QThread, Signal

class WorkerThread(QThread):
    progress = Signal(int)
    finished = Signal(dict)
    
    def run(self):
        try:
            # Long-running operation
            for i in range(100):
                self.progress.emit(i)
                time.sleep(0.1)
                
            self.finished.emit({'status': 'success'})
        except Exception as e:
            self.finished.emit({'status': 'error', 'message': str(e)})
```

### 3. Memory Management

```python
# Use context managers
with db.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute(query)
    
# Clean up large objects
del large_data
gc.collect()

# Use generators for large datasets
def get_transactions_batch(limit=1000):
    offset = 0
    while True:
        batch = db.get_transactions(limit=limit, offset=offset)
        if not batch:
            break
        yield batch
        offset += limit
```

### 4. Performance Optimization

```python
# Cache expensive operations
@lru_cache(maxsize=128)
def get_merchant_risk_score(merchant_category):
    return calculate_risk_score(merchant_category)

# Use bulk operations
transactions = []
for data in batch_data:
    transactions.append(process_transaction(data))
    
db.bulk_insert_transactions(transactions)

# Optimize queries
# Bad:
for account in accounts:
    transactions = db.get_transactions_for_account(account)
    
# Good:
transactions = db.get_transactions_for_accounts(accounts)
```

## Testing

### 1. Unit Tests

```python
import pytest
from core.ai_model import FraudDetectionModel

def test_fraud_detection():
    model = FraudDetectionModel()
    
    # Normal transaction
    normal_tx = {
        'amount': 50,
        'merchant_category': 'retail',
        'location': 'Local'
    }
    score, _ = model.predict(normal_tx)
    assert score < 0.3
    
    # Suspicious transaction
    suspicious_tx = {
        'amount': 10000,
        'merchant_category': 'gambling',
        'location': 'International'
    }
    score, _ = model.predict(suspicious_tx)
    assert score > 0.7
```

### 2. Integration Tests

```python
def test_transaction_pipeline():
    db = DatabaseManager()
    db.connect()
    
    monitor = MonitoringEngine(db)
    
    # Inject test transaction
    test_tx = create_test_transaction()
    monitor.process_transaction(test_tx)
    
    # Verify processing
    stored_tx = db.get_transaction(test_tx['transaction_id'])
    assert stored_tx is not None
    assert stored_tx['risk_score'] > 0
```

### 3. UI Tests

```python
from pytest_qt import qtbot

def test_transaction_export(qtbot):
    page = TransactionsPage()
    qtbot.addWidget(page)
    
    # Trigger export
    page.export_transactions('csv', export_all=True)
    
    # Verify export completed
    assert page.export_completed
```

## Debugging

### 1. Enable Debug Logging

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.debug("Debug message")
```

### 2. Qt Debug Tools

```python
# Enable Qt logging
import os
os.environ['QT_LOGGING_RULES'] = '*.debug=true'

# Debug widget hierarchy
def print_widget_tree(widget, indent=0):
    print(" " * indent + str(widget))
    for child in widget.children():
        print_widget_tree(child, indent + 2)
```

### 3. Performance Profiling

```python
import cProfile
import pstats

# Profile function
profiler = cProfile.Profile()
profiler.enable()

# Code to profile
process_large_dataset()

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)
```

## Deployment

### 1. Building Executable

```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller --name "Banking Security Platform" \
            --windowed \
            --icon=icon.ico \
            --add-data "data;data" \
            --add-data "src;src" \
            src/main.py
```

### 2. Creating Installer

```nsis
; NSIS installer script
!define APP_NAME "Banking Security Platform"
!define APP_VERSION "1.0.0"

OutFile "BankingSecurityPlatform-${APP_VERSION}-Setup.exe"
InstallDir "$PROGRAMFILES\${APP_NAME}"

Section "Install"
    SetOutPath $INSTDIR
    File /r "dist\Banking Security Platform\*.*"
    
    CreateShortcut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\${APP_NAME}.exe"
SectionEnd
```

## Extending the Platform

### 1. Adding New Fraud Rules

```python
class CustomFraudRule:
    def __init__(self, name, parameters):
        self.name = name
        self.parameters = parameters
        
    def evaluate(self, transaction):
        # Implement rule logic
        if transaction['amount'] > self.parameters['threshold']:
            return True, "Amount exceeds threshold"
        return False, None
        
# Register rule
rule_engine.register_rule(CustomFraudRule(
    name="High Amount Check",
    parameters={'threshold': 10000}
))
```

### 2. Adding New ML Models

```python
from sklearn.ensemble import RandomForestClassifier

class RandomForestFraudModel:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100)
        
    def train(self, X, y):
        self.model.fit(X, y)
        
    def predict(self, features):
        probability = self.model.predict_proba([features])[0][1]
        return probability
```

### 3. Custom Export Formats

```python
class CustomExporter:
    def export(self, data, format='json'):
        if format == 'json':
            return json.dumps(data, indent=2)
        elif format == 'xml':
            return self.to_xml(data)
            
    def to_xml(self, data):
        # XML conversion logic
        pass
```

## Troubleshooting

### Common Issues

1. **Database Locked Error**
   ```python
   # Solution: Use connection pooling
   db.conn.execute("PRAGMA journal_mode=WAL")
   ```

2. **UI Freezing**
   ```python
   # Solution: Use worker threads
   worker = WorkerThread()
   worker.start()
   ```

3. **Memory Leaks**
   ```python
   # Solution: Properly disconnect signals
   widget.destroyed.connect(lambda: signal.disconnect())
   ```

## Resources

- [PySide6 Documentation](https://doc.qt.io/qtforpython/)
- [scikit-learn Documentation](https://scikit-learn.org/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [ReportLab Documentation](https://www.reportlab.com/docs/)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Submit a pull request

## License

This project is part of a portfolio demonstration and is provided as-is for educational purposes.