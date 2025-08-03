from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QGridLayout, QProgressBar, QPushButton,
                             QScrollArea, QMessageBox, QFileDialog)
from PySide6.QtCore import Qt, QTimer, Signal, QThread
from PySide6.QtGui import QPainter, QBrush, QColor, QPen
from ui.widgets.stat_card import StatCard
from ui.widgets.metric_display import MetricDisplay
from ui.widgets.chart_widget import LineChart, BarChart, PieChart
from core.theme_manager import ThemeManager
from core.database import DatabaseManager
from core.monitoring import MonitoringEngine
from core.report_generator import ReportGenerator
from datetime import datetime

class DashboardPage(QWidget):
    fraud_detected = Signal(dict)
    
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.monitoring = MonitoringEngine(self.db)
        self.setup_ui()
        
        # Connect database signals
        self.db.connection_established.connect(self.on_database_connected)
        self.db.connection_failed.connect(self.on_database_error)
        self.db.data_updated.connect(self.refresh_metrics)
        
        # Connect monitoring signals
        self.monitoring.transaction_received.connect(self.on_transaction_received)
        self.monitoring.fraud_detected.connect(self.on_fraud_detected)
        self.monitoring.metrics_updated.connect(self.on_metrics_updated)
        self.monitoring.status_changed.connect(self.on_monitoring_status_changed)
        
    def setup_ui(self):
        # Main scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        # Content widget
        content = QWidget()
        scroll.setWidget(content)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
        
        # Content layout
        layout = QVBoxLayout(content)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Header section
        header_frame = QFrame()
        header_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {ThemeManager.COLORS['surface']};
                border-radius: 6px;
                padding: 16px;
            }}
        """)
        header_layout = QVBoxLayout(header_frame)
        
        # Page title
        title = QLabel("Security Dashboard")
        title.setObjectName("heading")
        header_layout.addWidget(title)
        
        # Page description
        description = QLabel("Real-time monitoring and analytics for banking security")
        description.setObjectName("caption")
        description.setStyleSheet(f"color: {ThemeManager.COLORS['text-secondary']};")
        header_layout.addWidget(description)
        
        layout.addWidget(header_frame)
        
        # Quick actions
        actions_frame = QFrame()
        actions_frame.setStyleSheet(f"""
            QFrame {{
                background-color: transparent;
            }}
        """)
        actions_layout = QHBoxLayout(actions_frame)
        actions_layout.setSpacing(12)
        
        # Connect Database button
        self.connect_db_btn = QPushButton("Connect Database")
        self.connect_db_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ThemeManager.COLORS['primary']};
                padding: 12px 24px;
                font-weight: 600;
            }}
        """)
        self.connect_db_btn.clicked.connect(self.connect_database)
        actions_layout.addWidget(self.connect_db_btn)
        
        # Start Monitoring button
        self.monitor_btn = QPushButton("Start Monitoring")
        self.monitor_btn.setEnabled(False)
        self.monitor_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ThemeManager.COLORS['success']};
                padding: 12px 24px;
                font-weight: 600;
            }}
            QPushButton:disabled {{
                background-color: {ThemeManager.COLORS['surface-variant']};
                color: {ThemeManager.COLORS['text-disabled']};
            }}
        """)
        self.monitor_btn.clicked.connect(self.toggle_monitoring)
        actions_layout.addWidget(self.monitor_btn)
        
        # Export Report button
        self.export_btn = QPushButton("Export Report")
        self.export_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ThemeManager.COLORS['surface-variant']};
                padding: 12px 24px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {ThemeManager.COLORS['border']};
            }}
        """)
        self.export_btn.clicked.connect(self.export_report)
        actions_layout.addWidget(self.export_btn)
        
        actions_layout.addStretch()
        layout.addWidget(actions_frame)
        
        # Metrics section
        metrics_label = QLabel("System Metrics")
        metrics_label.setObjectName("subheading")
        metrics_label.setStyleSheet("margin-top: 16px;")
        layout.addWidget(metrics_label)
        
        # Metrics grid
        metrics_grid = QGridLayout()
        metrics_grid.setSpacing(16)
        
        # Create metric cards
        self.total_transactions = MetricDisplay(
            "Total Transactions",
            "0",
            "No data",
            ThemeManager.COLORS['primary']
        )
        metrics_grid.addWidget(self.total_transactions, 0, 0)
        
        self.fraud_count = MetricDisplay(
            "Fraud Detected",
            "0",
            "No data",
            ThemeManager.COLORS['danger']
        )
        metrics_grid.addWidget(self.fraud_count, 0, 1)
        
        self.risk_score = MetricDisplay(
            "Risk Score",
            "N/A",
            "Not calculated",
            ThemeManager.COLORS['warning']
        )
        metrics_grid.addWidget(self.risk_score, 0, 2)
        
        self.blocked_count = MetricDisplay(
            "Blocked",
            "0",
            "No data",
            ThemeManager.COLORS['success']
        )
        metrics_grid.addWidget(self.blocked_count, 0, 3)
        
        layout.addLayout(metrics_grid)
        
        # Status section
        status_label = QLabel("System Status")
        status_label.setObjectName("subheading")
        status_label.setStyleSheet("margin-top: 24px;")
        layout.addWidget(status_label)
        
        # Status cards
        status_frame = QFrame()
        status_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {ThemeManager.COLORS['surface']};
                border-radius: 6px;
                padding: 16px;
            }}
        """)
        status_layout = QVBoxLayout(status_frame)
        
        # Database status
        self.db_status = self.create_status_item(
            "Database Connection",
            "Not connected",
            ThemeManager.COLORS['text-disabled']
        )
        status_layout.addWidget(self.db_status)
        
        # AI Model status
        self.ai_status = self.create_status_item(
            "AI Model",
            "Checking...",
            ThemeManager.COLORS['text-disabled']
        )
        status_layout.addWidget(self.ai_status)
        
        # Check AI model status
        self.check_ai_model_status()
        
        # Monitoring status
        self.monitor_status = self.create_status_item(
            "Real-time Monitoring",
            "Inactive",
            ThemeManager.COLORS['text-disabled']
        )
        status_layout.addWidget(self.monitor_status)
        
        layout.addWidget(status_frame)
        
        # Charts section
        charts_label = QLabel("Analytics")
        charts_label.setObjectName("subheading")
        charts_label.setStyleSheet("margin-top: 24px;")
        layout.addWidget(charts_label)
        
        # Charts grid
        charts_grid = QGridLayout()
        charts_grid.setSpacing(16)
        
        # Transaction volume chart
        self.volume_chart = LineChart("Transaction Volume (Last 50)")
        self.volume_chart.setMinimumHeight(200)
        charts_grid.addWidget(self.volume_chart, 0, 0)
        
        # Risk distribution chart
        self.risk_chart = PieChart("Risk Distribution")
        self.risk_chart.setMinimumHeight(200)
        charts_grid.addWidget(self.risk_chart, 0, 1)
        
        # Transaction types chart
        self.types_chart = BarChart("Transaction Types")
        self.types_chart.setMinimumHeight(200)
        charts_grid.addWidget(self.types_chart, 1, 0, 1, 2)
        
        layout.addLayout(charts_grid)
        
        # Add stretch at the end
        layout.addStretch()
        
    def create_status_item(self, label, status, color):
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {ThemeManager.COLORS['surface-variant']};
                border-radius: 4px;
                padding: 12px 16px;
                margin-bottom: 8px;
            }}
        """)
        
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        
        label_widget = QLabel(label)
        label_widget.setStyleSheet(f"""
            QLabel {{
                color: {ThemeManager.COLORS['text-primary']};
                font-weight: 500;
            }}
        """)
        layout.addWidget(label_widget)
        
        layout.addStretch()
        
        status_widget = QLabel(f"● {status}")
        status_widget.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-weight: 400;
            }}
        """)
        layout.addWidget(status_widget)
        
        return frame
        
    def connect_database(self):
        """Connect to the SQLite database"""
        self.connect_db_btn.setText("Connecting...")
        self.connect_db_btn.setEnabled(False)
        
        # Connect to database
        if self.db.connect():
            # Connection will be handled by signal
            pass
        else:
            self.connect_db_btn.setText("Connect Database")
            self.connect_db_btn.setEnabled(True)
        
    def on_database_connected(self):
        """Handle successful database connection"""
        self.connect_db_btn.setText("Database Connected")
        self.connect_db_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ThemeManager.COLORS['success']};
                padding: 12px 24px;
                font-weight: 600;
            }}
        """)
        self.monitor_btn.setEnabled(True)
        
        # Update status
        self.update_status_item(self.db_status, "Connected", ThemeManager.COLORS['success'])
        
        # Refresh metrics from database
        self.refresh_metrics()
        
    def on_database_error(self, error_msg):
        """Handle database connection error"""
        QMessageBox.critical(self, "Database Error", f"Failed to connect to database:\n{error_msg}")
        self.connect_db_btn.setText("Connect Database")
        self.connect_db_btn.setEnabled(True)
        
    def refresh_metrics(self, table_name=None):
        """Refresh metrics from database"""
        if not self.db.conn:
            return
            
        metrics = self.db.get_metrics_summary()
        
        # Update metric displays
        self.total_transactions.update_value(
            str(metrics.get('total_transactions', 0)),
            "Total processed"
        )
        
        self.fraud_count.update_value(
            str(metrics.get('fraud_detected', 0)),
            f"{metrics.get('fraud_detected', 0) / max(metrics.get('total_transactions', 1), 1) * 100:.1f}% of total"
        )
        
        avg_risk = metrics.get('average_risk_score', 0)
        self.risk_score.update_value(
            f"{avg_risk:.2f}",
            "Low risk" if avg_risk < 0.3 else "Medium risk" if avg_risk < 0.7 else "High risk"
        )
        
        self.blocked_count.update_value(
            str(metrics.get('blocked_transactions', 0)),
            "Transactions blocked"
        )
        
        # Update charts
        self.update_charts()
        
    def update_status_item(self, status_frame, new_status, color):
        """Update a status item's text and color"""
        # Find the status label in the frame
        for child in status_frame.children():
            if isinstance(child, QLabel) and "●" in child.text():
                child.setText(f"● {new_status}")
                child.setStyleSheet(f"""
                    QLabel {{
                        color: {color};
                        font-weight: 400;
                    }}
                """)
                break
                
    def toggle_monitoring(self):
        """Toggle real-time monitoring"""
        if self.monitoring.is_monitoring:
            self.monitoring.stop_monitoring()
            self.monitor_btn.setText("Start Monitoring")
            self.monitor_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {ThemeManager.COLORS['success']};
                    padding: 12px 24px;
                    font-weight: 600;
                }}
            """)
        else:
            self.monitoring.start_monitoring()
            self.monitor_btn.setText("Stop Monitoring")
            self.monitor_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {ThemeManager.COLORS['danger']};
                    padding: 12px 24px;
                    font-weight: 600;
                }}
            """)
            
    def on_transaction_received(self, transaction):
        """Handle new transaction"""
        # Transaction will be shown in the transactions page
        pass
        
    def on_fraud_detected(self, alert_data):
        """Handle fraud detection alert"""
        self.fraud_detected.emit(alert_data)
        
    def on_metrics_updated(self, metrics):
        """Handle metrics update from monitoring"""
        # Update metric displays
        self.total_transactions.update_value(
            str(metrics.get('total_transactions', 0)),
            "Total processed"
        )
        
        fraud_count = metrics.get('fraud_detected', 0)
        total = max(metrics.get('total_transactions', 1), 1)
        self.fraud_count.update_value(
            str(fraud_count),
            f"{fraud_count / total * 100:.1f}% fraud rate"
        )
        
        avg_risk = metrics.get('average_risk_score', 0)
        self.risk_score.update_value(
            f"{avg_risk:.2f}",
            "Low risk" if avg_risk < 0.3 else "Medium risk" if avg_risk < 0.7 else "High risk"
        )
        
        self.blocked_count.update_value(
            str(metrics.get('blocked_transactions', 0)),
            "Automatically blocked"
        )
        
    def on_monitoring_status_changed(self, status):
        """Handle monitoring status change"""
        if status == 'active':
            self.update_status_item(self.monitor_status, "Active", ThemeManager.COLORS['success'])
        else:
            self.update_status_item(self.monitor_status, "Inactive", ThemeManager.COLORS['text-disabled'])
            
    def check_ai_model_status(self):
        """Check if AI model is loaded"""
        if hasattr(self.monitoring, 'ai_model_loaded') and self.monitoring.ai_model_loaded:
            self.update_status_item(self.ai_status, "Model Loaded", ThemeManager.COLORS['success'])
        else:
            self.update_status_item(self.ai_status, "Using Rules Only", ThemeManager.COLORS['warning'])
            
    def update_charts(self):
        """Update dashboard charts with latest data"""
        if not self.db.conn:
            return
            
        cursor = self.db.conn.cursor()
        
        # Get transaction volume data (last 50 transactions)
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM (
                SELECT timestamp, 
                       datetime(timestamp, 'unixepoch') as dt,
                       strftime('%H', datetime(timestamp, 'unixepoch')) as hour
                FROM transactions
                ORDER BY timestamp DESC
                LIMIT 500
            )
            GROUP BY hour
            ORDER BY hour
        """)
        
        volume_data = []
        for row in cursor.fetchall():
            volume_data.append(row[0])
            
        if volume_data:
            self.volume_chart.set_data(volume_data)
            
        # Get risk distribution
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN risk_score < 0.3 THEN 'Low Risk'
                    WHEN risk_score < 0.7 THEN 'Medium Risk'
                    ELSE 'High Risk'
                END as risk_level,
                COUNT(*) as count
            FROM transactions
            GROUP BY risk_level
        """)
        
        risk_data = {}
        for row in cursor.fetchall():
            risk_data[row[0]] = row[1]
            
        if risk_data:
            self.risk_chart.set_data(risk_data)
            
        # Get transaction types
        cursor.execute("""
            SELECT transaction_type, COUNT(*) as count
            FROM transactions
            GROUP BY transaction_type
            ORDER BY count DESC
            LIMIT 5
        """)
        
        types_data = {}
        for row in cursor.fetchall():
            types_data[row[0].title()] = row[1]
            
        if types_data:
            self.types_chart.set_data(types_data)
            
    def export_report(self):
        """Export dashboard summary report"""
        if not self.db.conn:
            QMessageBox.warning(self, "Export Error", "Please connect to database first")
            return
            
        # Get file path from user
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Dashboard Report",
            f"dashboard_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            "PDF Files (*.pdf);;CSV Files (*.csv)"
        )
        
        if not file_path:
            return
            
        try:
            # Create report generator
            generator = ReportGenerator(self.db)
            
            # Determine format
            format = 'pdf' if file_path.endswith('.pdf') else 'csv'
            
            # Generate report
            report_buffer = generator.generate_transaction_report(format=format)
            
            # Save to file
            with open(file_path, 'wb' if format == 'pdf' else 'w') as f:
                f.write(report_buffer.read() if format == 'pdf' else report_buffer.getvalue())
                
            QMessageBox.information(self, "Export Complete", f"Report exported to:\n{file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export report:\n{str(e)}")