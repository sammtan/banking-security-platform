from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QProgressBar, QPushButton, QTabWidget,
                             QScrollArea, QGridLayout, QSpinBox, QSlider,
                             QFileDialog, QMessageBox)
from PySide6.QtCore import Qt, QTimer, QRectF, Signal
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QFont, QPainterPath
from core.theme_manager import ThemeManager
from core.database import DatabaseManager
from core.report_generator import ReportGenerator
from ui.widgets.rule_editor import RuleEditor
from datetime import datetime
import math
import json

class RiskGauge(QWidget):
    """Custom risk gauge widget"""
    def __init__(self):
        super().__init__()
        self.setMinimumSize(150, 150)
        self.value = 0.0
        
    def setValue(self, value):
        self.value = max(0.0, min(1.0, value))
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Get dimensions
        rect = self.rect()
        center = rect.center()
        radius = min(rect.width(), rect.height()) // 2 - 15
        
        # Draw background circle
        painter.setPen(QPen(QColor(ThemeManager.COLORS['surface-variant']), 2))
        painter.setBrush(QBrush(QColor(ThemeManager.COLORS['surface'])))
        painter.drawEllipse(center, radius, radius)
        
        # Draw background arc
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(QColor(ThemeManager.COLORS['border']), 6, Qt.SolidLine, Qt.RoundCap))
        painter.drawArc(center.x() - radius + 10, center.y() - radius + 10, 
                       (radius - 10) * 2, (radius - 10) * 2, 
                       -135 * 16, 270 * 16)
        
        # Draw value arc
        if self.value < 0.3:
            color = QColor(ThemeManager.COLORS['success'])
        elif self.value < 0.7:
            color = QColor(ThemeManager.COLORS['warning'])
        else:
            color = QColor(ThemeManager.COLORS['danger'])
            
        painter.setPen(QPen(color, 6, Qt.SolidLine, Qt.RoundCap))
        span_angle = int(270 * self.value * 16)
        painter.drawArc(center.x() - radius + 10, center.y() - radius + 10, 
                       (radius - 10) * 2, (radius - 10) * 2, 
                       -135 * 16, span_angle)
        
        # Draw percentage text
        painter.setPen(QColor(ThemeManager.COLORS['text-primary']))
        font = QFont("Inter", 24, QFont.Bold)
        painter.setFont(font)
        percentage_text = f"{int(self.value * 100)}%"
        painter.drawText(rect.adjusted(0, -10, 0, 0), Qt.AlignCenter, percentage_text)
        
        # Draw value below percentage
        painter.setPen(QColor(ThemeManager.COLORS['text-secondary']))
        font = QFont("Inter", 11)
        painter.setFont(font)
        value_text = f"{self.value:.3f}"
        value_rect = QRectF(rect.x(), center.y() + 12, rect.width(), 20)
        painter.drawText(value_rect, Qt.AlignCenter, value_text)

class CompactRuleEditor(QWidget):
    """Compact rule editor for grid layout"""
    rule_updated = Signal(dict)
    
    def __init__(self, pattern_data, db_manager):
        super().__init__()
        self.pattern = pattern_data
        self.db = db_manager
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        
        # Header with name and type
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)
        
        name_label = QLabel(self.pattern['pattern_name'])
        name_label.setStyleSheet(f"""
            QLabel {{
                color: {ThemeManager.COLORS['text-primary']};
                font-weight: 600;
                font-size: 13px;
            }}
        """)
        header_layout.addWidget(name_label)
        header_layout.addStretch()
        
        type_label = QLabel(self.pattern['pattern_type'].replace('_', ' ').title())
        type_label.setStyleSheet(f"""
            QLabel {{
                color: {ThemeManager.COLORS['primary']};
                font-size: 11px;
                padding: 2px 8px;
                background-color: {ThemeManager.COLORS['primary'] + '20'};
                border-radius: 3px;
            }}
        """)
        header_layout.addWidget(type_label)
        
        layout.addLayout(header_layout)
        
        # Main parameter control
        if self.pattern['pattern_type'] == 'amount_based':
            self.create_amount_control(layout)
        elif self.pattern['pattern_type'] == 'velocity_based':
            self.create_velocity_control(layout)
        elif self.pattern['pattern_type'] == 'temporal_based':
            self.create_temporal_control(layout)
        elif self.pattern['pattern_type'] == 'location_based':
            self.create_location_control(layout)
        elif self.pattern['pattern_type'] == 'merchant_based':
            self.create_merchant_control(layout)
            
    def create_amount_control(self, layout):
        control_layout = QHBoxLayout()
        control_layout.setSpacing(8)
        
        label = QLabel("Threshold:")
        label.setStyleSheet(f"color: {ThemeManager.COLORS['text-secondary']}; font-size: 12px;")
        control_layout.addWidget(label)
        
        self.threshold_spin = QSpinBox()
        self.threshold_spin.setMinimum(0)
        self.threshold_spin.setMaximum(100000)
        self.threshold_spin.setSingleStep(1000)
        self.threshold_spin.setValue(self.pattern['parameters'].get('threshold', 10000))
        self.threshold_spin.setPrefix("$")
        self.threshold_spin.valueChanged.connect(self.update_rule)
        control_layout.addWidget(self.threshold_spin)
        
        layout.addLayout(control_layout)
        
    def create_velocity_control(self, layout):
        control_layout = QHBoxLayout()
        control_layout.setSpacing(8)
        
        label = QLabel("Max trans:")
        label.setStyleSheet(f"color: {ThemeManager.COLORS['text-secondary']}; font-size: 12px;")
        control_layout.addWidget(label)
        
        self.max_trans_spin = QSpinBox()
        self.max_trans_spin.setMinimum(1)
        self.max_trans_spin.setMaximum(50)
        self.max_trans_spin.setValue(self.pattern['parameters'].get('max_transactions', 5))
        self.max_trans_spin.valueChanged.connect(self.update_rule)
        control_layout.addWidget(self.max_trans_spin)
        
        label2 = QLabel("in")
        label2.setStyleSheet(f"color: {ThemeManager.COLORS['text-secondary']}; font-size: 12px;")
        control_layout.addWidget(label2)
        
        self.time_spin = QSpinBox()
        self.time_spin.setMinimum(1)
        self.time_spin.setMaximum(60)
        self.time_spin.setValue(self.pattern['parameters'].get('time_window_minutes', 10))
        self.time_spin.setSuffix(" min")
        self.time_spin.valueChanged.connect(self.update_rule)
        control_layout.addWidget(self.time_spin)
        
        layout.addLayout(control_layout)
        
    def create_temporal_control(self, layout):
        hours = self.pattern['parameters'].get('suspicious_hours', [0, 1, 2, 3, 4, 5])
        label = QLabel(f"Suspicious hours: {len(hours)} selected")
        label.setStyleSheet(f"color: {ThemeManager.COLORS['text-secondary']}; font-size: 12px;")
        layout.addWidget(label)
        
    def create_location_control(self, layout):
        control_layout = QHBoxLayout()
        control_layout.setSpacing(8)
        
        label = QLabel("Radius:")
        label.setStyleSheet(f"color: {ThemeManager.COLORS['text-secondary']}; font-size: 12px;")
        control_layout.addWidget(label)
        
        self.radius_spin = QSpinBox()
        self.radius_spin.setMinimum(1)
        self.radius_spin.setMaximum(1000)
        self.radius_spin.setValue(self.pattern['parameters'].get('baseline_radius_km', 100))
        self.radius_spin.setSuffix(" km")
        self.radius_spin.valueChanged.connect(self.update_rule)
        control_layout.addWidget(self.radius_spin)
        
        layout.addLayout(control_layout)
        
    def create_merchant_control(self, layout):
        categories = self.pattern['parameters'].get('high_risk_categories', [])
        label = QLabel(f"Risk categories: {len(categories)} active")
        label.setStyleSheet(f"color: {ThemeManager.COLORS['text-secondary']}; font-size: 12px;")
        layout.addWidget(label)
        
    def update_rule(self):
        """Update rule parameters"""
        new_params = self.pattern['parameters'].copy()
        
        if hasattr(self, 'threshold_spin'):
            new_params['threshold'] = self.threshold_spin.value()
        if hasattr(self, 'max_trans_spin'):
            new_params['max_transactions'] = self.max_trans_spin.value()
        if hasattr(self, 'time_spin'):
            new_params['time_window_minutes'] = self.time_spin.value()
        if hasattr(self, 'radius_spin'):
            new_params['baseline_radius_km'] = self.radius_spin.value()
            
        # Update database
        cursor = self.db.conn.cursor()
        cursor.execute("""
            UPDATE fraud_patterns 
            SET parameters = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (json.dumps(new_params), self.pattern['id']))
        self.db.conn.commit()
        
        self.pattern['parameters'] = new_params
        self.rule_updated.emit(self.pattern)

class RiskAssessmentPage(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.db.connect()
        self.setup_ui()
        
        # Auto-refresh
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(5000)
        
        # Load initial data
        self.refresh_data()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Header
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        header = QLabel("Risk Assessment & Rule Management")
        header.setObjectName("heading")
        header_layout.addWidget(header)
        header_layout.addStretch()
        
        # Export button
        export_btn = QPushButton("Export Risk Report")
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
        export_btn.clicked.connect(self.export_risk_report)
        header_layout.addWidget(export_btn)
        
        layout.addLayout(header_layout)
        
        # Top section - Risk Overview and Rules in a grid
        top_grid = QGridLayout()
        top_grid.setSpacing(12)
        
        # Risk gauge panel (top-left)
        gauge_panel = QFrame()
        gauge_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {ThemeManager.COLORS['surface']};
                border-radius: 8px;
                padding: 16px;
            }}
        """)
        gauge_layout = QHBoxLayout(gauge_panel)
        gauge_layout.setSpacing(16)
        
        # Risk gauge (smaller)
        self.risk_gauge = RiskGauge()
        self.risk_gauge.setMaximumSize(150, 150)
        gauge_layout.addWidget(self.risk_gauge)
        
        # Risk info
        risk_info_layout = QVBoxLayout()
        risk_info_layout.setSpacing(4)
        
        self.risk_level_label = QLabel("Calculating...")
        self.risk_level_label.setStyleSheet(f"""
            QLabel {{
                font-size: 20px;
                font-weight: 700;
                color: {ThemeManager.COLORS['text-primary']};
            }}
        """)
        risk_info_layout.addWidget(self.risk_level_label)
        
        self.risk_desc_label = QLabel("Analyzing patterns...")
        self.risk_desc_label.setWordWrap(True)
        self.risk_desc_label.setStyleSheet(f"""
            QLabel {{
                color: {ThemeManager.COLORS['text-secondary']};
                font-size: 12px;
            }}
        """)
        risk_info_layout.addWidget(self.risk_desc_label)
        risk_info_layout.addStretch()
        
        gauge_layout.addLayout(risk_info_layout)
        gauge_layout.addStretch()
        
        top_grid.addWidget(gauge_panel, 0, 0)
        
        # Risk factors panel (top-right)
        factors_panel = QFrame()
        factors_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {ThemeManager.COLORS['surface']};
                border-radius: 8px;
                padding: 16px;
            }}
        """)
        factors_layout = QVBoxLayout(factors_panel)
        factors_layout.setSpacing(8)
        
        factors_label = QLabel("Top Risk Factors")
        factors_label.setStyleSheet(f"""
            QLabel {{
                font-weight: 600;
                font-size: 14px;
                color: {ThemeManager.COLORS['text-primary']};
                margin-bottom: 4px;
            }}
        """)
        factors_layout.addWidget(factors_label)
        
        # Risk factor items container
        self.factors_layout = QVBoxLayout()
        self.factors_layout.setSpacing(6)
        factors_layout.addLayout(self.factors_layout)
        
        top_grid.addWidget(factors_panel, 0, 1)
        
        # Stats row
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(12)
        
        self.high_risk_card = self.create_compact_stat_card("High Risk", "0", ThemeManager.COLORS['danger'], "⚠")
        stats_layout.addWidget(self.high_risk_card)
        
        self.medium_risk_card = self.create_compact_stat_card("Medium Risk", "0", ThemeManager.COLORS['warning'], "◉")
        stats_layout.addWidget(self.medium_risk_card)
        
        self.low_risk_card = self.create_compact_stat_card("Low Risk", "0", ThemeManager.COLORS['success'], "✓")
        stats_layout.addWidget(self.low_risk_card)
        
        self.blocked_card = self.create_compact_stat_card("Blocked", "0", ThemeManager.COLORS['primary'], "✕")
        stats_layout.addWidget(self.blocked_card)
        
        top_grid.addLayout(stats_layout, 1, 0, 1, 2)
        layout.addLayout(top_grid)
        
        # Rule Management Section - Compact grid layout
        rules_label = QLabel("Fraud Detection Rules")
        rules_label.setObjectName("subheading")
        rules_label.setStyleSheet("margin-top: 12px; margin-bottom: 8px;")
        layout.addWidget(rules_label)
        
        # Rules grid
        self.rules_grid = QGridLayout()
        self.rules_grid.setSpacing(12)
        
        # Load all rule editors in grid
        self.load_rule_editors()
        
        layout.addLayout(self.rules_grid)
        layout.addStretch()
        
    def create_compact_stat_card(self, title, value, color, icon):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {ThemeManager.COLORS['surface']};
                border-radius: 6px;
                padding: 12px;
            }}
        """)
        
        layout = QHBoxLayout(card)
        layout.setSpacing(12)
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 24px;
            }}
        """)
        layout.addWidget(icon_label)
        
        # Text
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        value_label = QLabel(value)
        value_label.setObjectName(f"stat_value_{title}")
        value_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 20px;
                font-weight: 700;
            }}
        """)
        text_layout.addWidget(value_label)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {ThemeManager.COLORS['text-secondary']};
                font-size: 11px;
                font-weight: 500;
            }}
        """)
        text_layout.addWidget(title_label)
        
        layout.addLayout(text_layout)
        layout.addStretch()
        
        return card
        
    def refresh_data(self):
        """Refresh risk assessment data"""
        if not self.db.conn:
            return
            
        # Get risk statistics
        cursor = self.db.conn.cursor()
        
        # Average risk score
        cursor.execute("SELECT AVG(risk_score) FROM transactions WHERE risk_score > 0")
        avg_risk = cursor.fetchone()[0] or 0.0
        self.risk_gauge.setValue(avg_risk)
        
        # Update risk level
        if avg_risk < 0.3:
            self.risk_level_label.setText("Low Risk")
            self.risk_level_label.setStyleSheet(f"""
                QLabel {{
                    color: {ThemeManager.COLORS['success']};
                    font-size: 24px;
                    font-weight: 700;
                    margin-top: 20px;
                }}
            """)
            self.risk_desc_label.setText("Transaction patterns appear normal with minimal suspicious activity.")
        elif avg_risk < 0.7:
            self.risk_level_label.setText("Medium Risk")
            self.risk_level_label.setStyleSheet(f"""
                QLabel {{
                    color: {ThemeManager.COLORS['warning']};
                    font-size: 24px;
                    font-weight: 700;
                    margin-top: 20px;
                }}
            """)
            self.risk_desc_label.setText("Some suspicious patterns detected. Enhanced monitoring recommended.")
        else:
            self.risk_level_label.setText("High Risk")
            self.risk_level_label.setStyleSheet(f"""
                QLabel {{
                    color: {ThemeManager.COLORS['danger']};
                    font-size: 24px;
                    font-weight: 700;
                    margin-top: 20px;
                }}
            """)
            self.risk_desc_label.setText("Significant suspicious activity. Action required.")
            
        # Get risk factor breakdown
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN risk_score >= 0.7 THEN 1 ELSE 0 END) as high_risk,
                SUM(CASE WHEN risk_score >= 0.3 AND risk_score < 0.7 THEN 1 ELSE 0 END) as medium_risk,
                SUM(CASE WHEN risk_score < 0.3 THEN 1 ELSE 0 END) as low_risk,
                SUM(CASE WHEN blocked = 1 THEN 1 ELSE 0 END) as blocked
            FROM transactions
        """)
        
        stats = cursor.fetchone()
        
        # Update stat cards
        self.update_stat_value("High Risk", str(stats[0] or 0))
        self.update_stat_value("Medium Risk", str(stats[1] or 0))
        self.update_stat_value("Low Risk", str(stats[2] or 0))
        self.update_stat_value("Blocked", str(stats[3] or 0))
        
        # Update risk factors
        self.update_risk_factors()
        
    def update_stat_value(self, title, value):
        """Update a stat card value"""
        for i in range(4):
            card = [self.high_risk_card, self.medium_risk_card, 
                   self.low_risk_card, self.blocked_card][i]
            label = card.findChild(QLabel, f"stat_value_{title}")
            if label:
                label.setText(value)
                
    def update_risk_factors(self):
        """Update risk factors display"""
        # Clear existing
        while self.factors_layout.count():
            item = self.factors_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        # Get recent high-risk patterns
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT merchant_category, COUNT(*) as count, AVG(risk_score) as avg_risk
            FROM transactions
            WHERE risk_score > 0.5
            GROUP BY merchant_category
            ORDER BY avg_risk DESC
            LIMIT 5
        """)
        
        categories = cursor.fetchall()
        
        for cat in categories:
            factor_item = self.create_risk_factor(
                f"{cat[0].replace('_', ' ').title()}",
                f"{cat[1]} transactions",
                cat[2]
            )
            self.factors_layout.addWidget(factor_item)
            
    def create_risk_factor(self, name, description, risk_value):
        """Create a risk factor item"""
        item = QFrame()
        item.setStyleSheet(f"""
            QFrame {{
                background-color: {ThemeManager.COLORS['surface-variant']};
                border-radius: 4px;
                padding: 8px 12px;
            }}
        """)
        
        layout = QHBoxLayout(item)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Risk indicator bar
        indicator = QFrame()
        color = (ThemeManager.COLORS['success'] if risk_value < 0.3 else
                ThemeManager.COLORS['warning'] if risk_value < 0.7 else
                ThemeManager.COLORS['danger'])
        indicator.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 2px;
                min-width: 4px;
                max-width: 4px;
            }}
        """)
        layout.addWidget(indicator)
        
        # Text
        text_label = QLabel(f"{name} - {description}")
        text_label.setStyleSheet(f"""
            QLabel {{
                color: {ThemeManager.COLORS['text-primary']};
                font-size: 12px;
            }}
        """)
        layout.addWidget(text_label)
        layout.addStretch()
        
        # Risk value
        risk_label = QLabel(f"{risk_value:.2f}")
        risk_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-weight: 600;
                font-size: 13px;
            }}
        """)
        layout.addWidget(risk_label)
        
        return item
        
    def load_rule_editors(self):
        """Load fraud detection rules into the grid layout"""
        # Clear existing rules
        while self.rules_grid.count():
            item = self.rules_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Get fraud patterns
        patterns = self.db.get_fraud_patterns(enabled_only=True)
        
        # Add rules in a 2-column grid
        row = 0
        col = 0
        
        for pattern in patterns:
            # Create compact rule frame
            rule_frame = QFrame()
            rule_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {ThemeManager.COLORS['surface']};
                    border-radius: 8px;
                    padding: 12px;
                }}
            """)
            
            frame_layout = QVBoxLayout(rule_frame)
            frame_layout.setContentsMargins(0, 0, 0, 0)
            frame_layout.setSpacing(8)
            
            # Create compact editor
            editor = CompactRuleEditor(pattern, self.db)
            editor.rule_updated.connect(self.on_rule_updated)
            frame_layout.addWidget(editor)
            
            self.rules_grid.addWidget(rule_frame, row, col)
            
            # Move to next position
            col += 1
            if col > 1:
                col = 0
                row += 1
            
    def on_rule_updated(self, pattern):
        """Handle rule update"""
        # Refresh risk factors
        self.update_risk_factors()
        # The monitoring engine will pick up the new rules automatically
        
    def export_risk_report(self):
        """Export risk assessment report"""
        if not self.db.conn:
            QMessageBox.warning(self, "Export Error", "Database not connected")
            return
            
        # Get file path from user
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Risk Assessment Report",
            f"risk_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            "PDF Files (*.pdf)"
        )
        
        if not file_path:
            return
            
        try:
            # Create report generator
            generator = ReportGenerator(self.db)
            
            # Generate report
            report_buffer = generator.generate_risk_assessment_report(format='pdf')
            
            # Save to file
            with open(file_path, 'wb') as f:
                f.write(report_buffer.read())
                
            QMessageBox.information(self, "Export Complete", f"Risk assessment report exported to:\n{file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export report:\n{str(e)}")