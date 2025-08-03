"""
Banking Security Platform - Full Demo
This script runs the application and shows all key features
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    print("""
    ==============================================================
               Banking Security Platform - Demo               
    ==============================================================
    
    Features Demonstrated:
    * Lights-out UI theme with blue/red accents
    * Real SQLite database with 500+ test transactions
    * Live metrics dashboard
    * Fraud detection patterns
    * Risk assessment visualization
    * Programmatic UI testing capability
    
    Instructions:
    1. Click "Connect Database" to connect to the SQLite database
    2. Once connected, click "Start Monitoring" to begin real-time analysis
    3. Navigate through different sections using the sidebar
    4. The database already contains test data with fraud patterns
    
    Technical Stack:
    - PySide6 (Qt6) for native desktop UI
    - SQLite for local data storage
    - Inter font with fallbacks
    - Fully testable with pytest-qt
    
    Press Ctrl+C to exit
    """)
    
    # Import and run the main application
    from src.main import main
    main()

if __name__ == "__main__":
    main()