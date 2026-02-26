# Banking Security Platform

A comprehensive desktop application for real-time banking fraud detection and risk assessment, built with Python and PySide6.

## Features

### ✅ Implemented
- **Real-time Transaction Monitoring** - Track and analyze banking transactions as they occur
- **AI-Powered Fraud Detection** - Machine learning model (Isolation Forest) with rule-based fallback
- **Risk Assessment Dashboard** - Comprehensive risk scoring and factor analysis
- **Export & Reporting** - Generate PDF, CSV, and Excel reports
- **Modern Dark Theme UI** - Professional lights-out design with blue/red accents
- **Responsive Layout** - Adaptive UI for different screen sizes
- **SQLite Database** - Local data persistence
- **Live Data Updates** - Real-time refresh without UI lag
- **Customizable Rules** - Editable fraud detection parameters
- **Pagination System** - Efficient handling of large datasets

## Technology Stack

- **GUI Framework**: PySide6 (Qt6)
- **Database**: SQLite
- **ML Framework**: scikit-learn (Isolation Forest)
- **Reporting**: ReportLab (PDF), pandas, XlsxWriter (Excel)
- **Font**: Inter (embedded)
- **Testing**: pytest-qt

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

```bash
python src/main.py
```

### First-time Setup
1. Click "Connect Database" to initialize the SQLite database
2. Click "Start Monitoring" to begin real-time transaction monitoring
3. The system will generate synthetic transactions for demonstration

### Demo Mode
```bash
python scripts/run_demo.py  # Generates sample transactions
```

### Train AI Model
```bash
python scripts/train_model.py  # Train fraud detection model
```

## Testing

### Running the Application
To test the application functionality:
```bash
python src/main.py
```

### Training the AI Model
```bash
python scripts/train_model.py
```

## Project Structure

```
banking-security-platform/
├── src/
│   ├── main.py                  # Application entry point
│   ├── core/
│   │   ├── database.py          # SQLite database manager
│   │   ├── monitoring.py        # Real-time monitoring engine
│   │   ├── ai_model.py          # Fraud detection ML model
│   │   ├── report_generator.py  # Report generation
│   │   └── theme_manager.py     # UI theme configuration
│   └── ui/
│       ├── main_window.py       # Main application window
│       ├── pages/               # UI page components
│       │   ├── dashboard.py     # System overview
│       │   ├── transactions.py  # Transaction monitoring
│       │   ├── fraud_detection.py # Fraud alerts
│       │   └── risk_assessment.py # Risk analysis
│       └── widgets/             # Reusable components
├── scripts/
│   ├── run_demo.py             # Demo data generator
│   └── train_model.py          # ML model training
├── data/
│   └── banking.db              # SQLite database
├── docs/                       # Documentation
│   ├── SYSTEM_DESIGN.md        # Architecture documentation
│   └── PROGRAMMING_GUIDE.md    # Development guide
└── requirements.txt

```

## Key Features Explained

### 1. Transaction Monitoring
- Real-time transaction feed with 5-second auto-refresh
- Advanced filtering by risk level, status, and search terms
- Pagination with configurable page sizes (10-200 rows)
- Export to PDF, CSV, or Excel formats

### 2. Fraud Detection System
- **Rule-Based Detection**: 5 configurable pattern types
  - Amount-based (high-value transactions)
  - Velocity-based (rapid sequences)
  - Temporal-based (suspicious hours)
  - Location-based (keyword-based location risk scoring)
  - Merchant-based (high-risk categories)
- **AI Model**: Isolation Forest for anomaly detection
- **Visual Alerts**: Tile-based fraud alerts with severity indicators

### 3. Risk Assessment
- Real-time risk gauge visualization
- Top risk factors analysis
- Distribution statistics (High/Medium/Low)
- Editable fraud detection rules

### 4. Export & Reporting
- **Transaction Reports**: Complete transaction history
- **Fraud Reports**: Detailed fraud analysis with statistics
- **Risk Reports**: Risk distribution and merchant analysis
- **Formats**: PDF (with charts), CSV, Excel (with formatting)

## Performance Specifications

- **ML Inference**: Sub-millisecond per transaction (inference-only benchmark; full pipeline throughput is lower due to database writes and UI updates)
- **Database**: Optimized SQLite with proper indexing
- **UI Updates**: Non-blocking with incremental refresh
- **Memory Usage**: Efficient pagination prevents memory overflow
- **Response Time**: <100ms for most operations

## Security Features

- Local database (no network exposure)
- Prepared statements (SQL injection prevention)
- Rule-based + AI hybrid detection
- Automatic flagging and blocking status assignment
- Comprehensive audit trail

## AI Model Sanity Checks

> **Note:** All data below is **synthetic** (randomly generated for demonstration). These results are not derived from a real-world dataset, cross-validation, or hold-out test set and should not be interpreted as production accuracy measurements.

### ML Inference Benchmark (2025-08-03)

The following figures measure **scikit-learn `.predict()` inference time only** — pure matrix math without database writes, Qt signal emission, or UI re-rendering. Actual end-to-end throughput is far lower (the monitoring engine uses a 1–3 second timer between transactions).

| Batch size | Inference TPS |
|-----------|--------------|
| 1         | ~31,300       |
| 10        | ~267,153      |
| 100       | ~390,167      |

### Basic Sanity Checks on Synthetic Data

These three synthetic scenarios verify that the model produces sensible directional outputs. They are not a substitute for evaluation on a representative dataset.

**Test Scenarios:**
1. **Normal Transaction** ($50, grocery, local) → Risk: 0.000 (Low) ✓
2. **High Risk** ($10,000, gambling, offshore, 3AM) → Risk: 0.900 (High) ✓
3. **Medium Risk** ($2,000, online, international) → Risk: 0.300 (Medium) ✓

**Edge Case Handling:**
- Zero amount transactions: Handled
- Extreme amounts ($1M): Detected as medium risk
- Unknown locations: Processed successfully

**Overall Sanity Check Result: PASS**

The model correctly classifies these three obvious synthetic cases, confirming the pipeline is wired up correctly. No precision/recall/F1 metrics from a representative dataset have been measured.

## Portfolio Demonstration

This project showcases:
- **Full-Stack Development**: Frontend (PySide6) + Backend (Python) + Database (SQLite)
- **AI/ML Integration**: Practical implementation of anomaly detection
- **Clean Architecture**: Separation of concerns, modular design
- **Professional UI/UX**: Banking-grade interface design
- **Data Visualization**: Real-time charts and metrics
- **Report Generation**: Multi-format export capabilities
- **Demo & Validation Scripts**: `scripts/train_model.py` for model training and basic synthetic-data sanity checks

---

**Developed for Portfolio** | Targeting: Financial Technology Companies