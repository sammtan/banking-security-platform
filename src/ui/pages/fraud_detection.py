from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QScrollArea, QPushButton, QProgressBar,
                             QMessageBox, QGridLayout, QFileDialog)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QFont
from core.theme_manager import ThemeManager
from core.database import DatabaseManager
from core.report_generator import ReportGenerator
from datetime import datetime
import json

class FraudDetectionPage(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.db.connect()
        self.setup_ui()
        
        # Connect to database updates
        self.db.data_updated.connect(self.refresh_data)
        
        # Auto-refresh
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(3000)
        
        # Load initial data
        self.refresh_data()
        
    def setup_ui(self):
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Header
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        header = QLabel("Fraud Detection Center")
        header.setObjectName("heading")
        header_layout.addWidget(header)
        header_layout.addStretch()
        
        # Export button
        export_btn = QPushButton("Export Fraud Report")
        export_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ThemeManager.COLORS['surface-variant']};
                padding: 8px 16px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {ThemeManager.COLORS['border']};
            }}
        """)
        export_btn.clicked.connect(self.export_fraud_report)
        header_layout.addWidget(export_btn)
        
        layout.addLayout(header_layout)
        
        # Two-panel layout
        panels_layout = QHBoxLayout()
        panels_layout.setSpacing(12)
        
        # Left panel - Recent Fraud Alerts (bigger)
        left_panel = QFrame()
        left_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {ThemeManager.COLORS['surface']};
                border-radius: 8px;
                padding: 16px;
            }}
        """)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(12)
        
        # Left panel header
        alerts_header = QLabel("Recent Fraud Alerts")
        alerts_header.setStyleSheet(f"""
            QLabel {{
                font-size: 16px;
                font-weight: 600;
                color: {ThemeManager.COLORS['text-primary']};
                margin-bottom: 8px;
            }}
        """)
        left_layout.addWidget(alerts_header)
        
        # Alerts scroll area
        alerts_scroll = QScrollArea()
        alerts_scroll.setWidgetResizable(True)
        alerts_scroll.setFrameShape(QFrame.NoFrame)
        alerts_scroll.setStyleSheet(f"""
            QScrollArea {{
                background-color: transparent;
                border: none;
            }}
            QScrollBar:vertical {{
                background-color: {ThemeManager.COLORS['surface-variant']};
                width: 8px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {ThemeManager.COLORS['border']};
                border-radius: 4px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {ThemeManager.COLORS['primary']};
            }}
        """)
        
        # Alerts container
        self.alerts_container = QWidget()
        self.alerts_layout = QGridLayout(self.alerts_container)
        self.alerts_layout.setSpacing(12)
        self.alerts_layout.setContentsMargins(0, 0, 8, 0)
        
        alerts_scroll.setWidget(self.alerts_container)
        left_layout.addWidget(alerts_scroll)
        
        panels_layout.addWidget(left_panel, 2)  # 2:1 ratio
        
        # Right panel - Active Detection Patterns (smaller)
        right_panel = QFrame()
        right_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {ThemeManager.COLORS['surface']};
                border-radius: 8px;
                padding: 16px;
            }}
        """)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(12)
        
        # Right panel header
        patterns_header = QLabel("Active Detection Patterns")
        patterns_header.setStyleSheet(f"""
            QLabel {{
                font-size: 16px;
                font-weight: 600;
                color: {ThemeManager.COLORS['text-primary']};
                margin-bottom: 8px;
            }}
        """)
        right_layout.addWidget(patterns_header)
        
        # Patterns container (no scroll)
        self.patterns_layout = QVBoxLayout()
        self.patterns_layout.setSpacing(8)
        right_layout.addLayout(self.patterns_layout)
        right_layout.addStretch()
        
        panels_layout.addWidget(right_panel, 1)  # 2:1 ratio
        
        layout.addLayout(panels_layout)
        
    def refresh_data(self):
        """Refresh both alerts and patterns"""
        self.refresh_alerts()
        self.refresh_patterns()
        
    def refresh_alerts(self):
        """Refresh fraud alerts with tiles/cards"""
        if not self.db.conn:
            return
            
        # Get recent fraud alerts
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT t.*, 
                   MAX(CASE WHEN a.alert_type = 'fraud_detection' THEN a.severity END) as alert_severity,
                   MAX(CASE WHEN a.alert_type = 'fraud_detection' THEN a.message END) as alert_message
            FROM transactions t
            LEFT JOIN alerts a ON t.transaction_id = a.transaction_id
            WHERE t.fraud_detected = 1 OR a.alert_type = 'fraud_detection'
            GROUP BY t.id
            ORDER BY t.timestamp DESC
            LIMIT 12
        """)
        
        alerts = [dict(row) for row in cursor.fetchall()]
        
        # Clear existing alerts
        while self.alerts_layout.count():
            item = self.alerts_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        # Add alert tiles in grid (3 columns)
        row = 0
        col = 0
        
        for alert in alerts:
            tile = self.create_alert_tile(alert)
            self.alerts_layout.addWidget(tile, row, col)
            
            col += 1
            if col >= 3:
                col = 0
                row += 1
                
        if not alerts:
            no_alerts = QLabel("No fraud alerts detected")
            no_alerts.setStyleSheet(f"""
                QLabel {{
                    color: {ThemeManager.COLORS['text-disabled']};
                    font-style: italic;
                    padding: 40px;
                    font-size: 14px;
                }}
            """)
            no_alerts.setAlignment(Qt.AlignCenter)
            self.alerts_layout.addWidget(no_alerts, 0, 0, 1, 3)
            
    def create_alert_tile(self, alert):
        """Create a tile/card for fraud alert"""
        # Determine severity and color
        risk_score = alert.get('risk_score', 0)
        if risk_score >= 0.8:
            severity = 'critical'
            color = ThemeManager.COLORS['danger']
            icon = "🚨"
        elif risk_score >= 0.6:
            severity = 'high'
            color = ThemeManager.COLORS['warning']
            icon = "⚠️"
        else:
            severity = 'medium'
            color = ThemeManager.COLORS['primary']
            icon = "ℹ️"
            
        tile = QFrame()
        tile.setStyleSheet(f"""
            QFrame {{
                background-color: {ThemeManager.COLORS['surface-variant']};
                border-radius: 8px;
                padding: 16px;
                border: 1px solid {color}40;
            }}
            QFrame:hover {{
                background-color: {color}10;
                border-color: {color};
            }}
        """)
        tile.setCursor(Qt.PointingHandCursor)
        
        layout = QVBoxLayout(tile)
        layout.setSpacing(8)
        
        # Header with icon and amount
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 24px;")
        header_layout.addWidget(icon_label)
        
        # Amount
        amount_label = QLabel(f"${alert['amount']:,.2f}")
        amount_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 20px;
                font-weight: 700;
            }}
        """)
        header_layout.addWidget(amount_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Transaction type and merchant
        info_label = QLabel(f"{alert['transaction_type'].title()} • {alert['merchant_name']}")
        info_label.setStyleSheet(f"""
            QLabel {{
                color: {ThemeManager.COLORS['text-primary']};
                font-size: 13px;
                font-weight: 500;
            }}
        """)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Location and time
        time_str = datetime.fromisoformat(str(alert['timestamp'])).strftime("%H:%M")
        location_label = QLabel(f"📍 {alert['location']} • {time_str}")
        location_label.setStyleSheet(f"""
            QLabel {{
                color: {ThemeManager.COLORS['text-secondary']};
                font-size: 11px;
            }}
        """)
        layout.addWidget(location_label)
        
        # Risk score bar
        risk_bar = QProgressBar()
        risk_bar.setRange(0, 100)
        risk_bar.setValue(int(risk_score * 100))
        risk_bar.setTextVisible(False)
        risk_bar.setFixedHeight(4)
        risk_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {ThemeManager.COLORS['surface']};
                border-radius: 2px;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 2px;
            }}
        """)
        layout.addWidget(risk_bar)
        
        # Status
        status = "Blocked" if alert['blocked'] else "Flagged"
        status_label = QLabel(status)
        status_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 11px;
                font-weight: 600;
                text-transform: uppercase;
            }}
        """)
        layout.addWidget(status_label)
        
        # Add click handler
        tile.mousePressEvent = lambda e: self.show_alert_details(alert)
        
        return tile
        
    def refresh_patterns(self):
        """Refresh active detection patterns"""
        patterns = self.db.get_fraud_patterns(enabled_only=True)
        
        # Clear existing
        while self.patterns_layout.count():
            item = self.patterns_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        # Group patterns by type
        pattern_groups = {}
        for pattern in patterns:
            ptype = pattern['pattern_type']
            if ptype not in pattern_groups:
                pattern_groups[ptype] = []
            pattern_groups[ptype].append(pattern)
            
        # Add pattern groups
        for ptype, patterns_list in pattern_groups.items():
            group_widget = self.create_pattern_group(ptype, patterns_list)
            self.patterns_layout.addWidget(group_widget)
            
    def create_pattern_group(self, pattern_type, patterns):
        """Create a compact pattern group widget"""
        group = QFrame()
        group.setStyleSheet(f"""
            QFrame {{
                background-color: {ThemeManager.COLORS['surface-variant']};
                border-radius: 6px;
                padding: 12px;
            }}
        """)
        
        layout = QVBoxLayout(group)
        layout.setSpacing(6)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Group header
        header_layout = QHBoxLayout()
        
        type_label = QLabel(pattern_type.replace('_', ' ').title())
        type_label.setStyleSheet(f"""
            QLabel {{
                color: {ThemeManager.COLORS['text-primary']};
                font-weight: 600;
                font-size: 13px;
            }}
        """)
        header_layout.addWidget(type_label)
        
        count_label = QLabel(str(len(patterns)))
        count_label.setStyleSheet(f"""
            QLabel {{
                background-color: {ThemeManager.COLORS['primary']};
                color: white;
                padding: 2px 6px;
                border-radius: 10px;
                font-size: 11px;
                font-weight: 600;
            }}
        """)
        header_layout.addWidget(count_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Pattern items
        for pattern in patterns:
            item_layout = QHBoxLayout()
            item_layout.setSpacing(4)
            
            # Status indicator
            status_dot = QLabel("●")
            status_dot.setStyleSheet(f"""
                QLabel {{
                    color: {ThemeManager.COLORS['success']};
                    font-size: 8px;
                }}
            """)
            item_layout.addWidget(status_dot)
            
            # Pattern name
            name_label = QLabel(pattern['pattern_name'])
            name_label.setStyleSheet(f"""
                QLabel {{
                    color: {ThemeManager.COLORS['text-secondary']};
                    font-size: 11px;
                }}
            """)
            item_layout.addWidget(name_label)
            item_layout.addStretch()
            
            layout.addLayout(item_layout)
            
        return group
        
    def show_alert_details(self, alert):
        """Show detailed fraud alert information"""
        details_text = f"""
Fraud Alert Details:

Transaction ID: {alert['transaction_id']}
Amount: ${alert['amount']:,.2f}
Type: {alert['transaction_type'].title()}
Merchant: {alert['merchant_name']}
Category: {alert.get('merchant_category', 'N/A').replace('_', ' ').title()}
Location: {alert['location']}
Time: {alert['timestamp']}

Risk Assessment:
Risk Score: {alert['risk_score']:.3f}
Status: {'Blocked' if alert['blocked'] else 'Flagged'}
Fraud Detected: {'Yes' if alert['fraud_detected'] else 'No'}

Actions:
• Review transaction history
• Update fraud rules
• Whitelist merchant
• Contact customer
        """.strip()
        
        QMessageBox.information(self, "Fraud Alert Details", details_text)
        
    def export_fraud_report(self):
        """Export fraud detection report"""
        if not self.db.conn:
            QMessageBox.warning(self, "Export Error", "Database not connected")
            return
            
        # Get file path from user
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Fraud Detection Report",
            f"fraud_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
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
            report_buffer = generator.generate_fraud_report(format=format)
            
            # Save to file
            with open(file_path, 'wb' if format == 'pdf' else 'w') as f:
                f.write(report_buffer.read() if format == 'pdf' else report_buffer.getvalue())
                
            QMessageBox.information(self, "Export Complete", f"Fraud report exported to:\n{file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export report:\n{str(e)}")