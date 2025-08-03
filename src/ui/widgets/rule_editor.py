from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QPushButton, QSpinBox, QDoubleSpinBox,
                             QLineEdit, QComboBox, QListWidget, QListWidgetItem,
                             QMessageBox)
from PySide6.QtCore import Qt, Signal
from core.theme_manager import ThemeManager
import json

class RuleEditor(QWidget):
    """Widget for editing fraud detection rules"""
    
    rule_updated = Signal(dict)
    
    def __init__(self, pattern_data, db_manager):
        super().__init__()
        self.pattern = pattern_data
        self.db = db_manager
        self.original_params = pattern_data['parameters'].copy()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Rule name
        name_label = QLabel(self.pattern['pattern_name'])
        name_label.setStyleSheet(f"""
            QLabel {{
                color: {ThemeManager.COLORS['text-primary']};
                font-weight: 600;
                font-size: 16px;
                padding: 2px 0px;
            }}
        """)
        layout.addWidget(name_label)
        
        # Rule type
        type_label = QLabel(f"Type: {self.pattern['pattern_type'].replace('_', ' ').title()}")
        type_label.setStyleSheet(f"""
            QLabel {{
                color: {ThemeManager.COLORS['text-secondary']};
                font-size: 12px;
                padding: 2px 0px;
            }}
        """)
        layout.addWidget(type_label)
        
        # Description
        desc_label = QLabel(self.pattern['description'])
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet(f"""
            QLabel {{
                color: {ThemeManager.COLORS['text-secondary']};
                font-size: 12px;
                margin-bottom: 8px;
                padding: 4px 0px;
                line-height: 1.4;
            }}
        """)
        layout.addWidget(desc_label)
        
        # Parameters editor
        params_frame = QFrame()
        params_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {ThemeManager.COLORS['surface-variant']};
                border-radius: 4px;
                padding: 12px;
            }}
        """)
        params_layout = QVBoxLayout(params_frame)
        
        params_label = QLabel("Parameters:")
        params_label.setStyleSheet(f"""
            QLabel {{
                color: {ThemeManager.COLORS['text-primary']};
                font-weight: 500;
                font-size: 13px;
                margin-bottom: 8px;
            }}
        """)
        params_layout.addWidget(params_label)
        
        # Create parameter editors based on pattern type
        self.param_widgets = {}
        
        if self.pattern['pattern_type'] == 'amount_based':
            self.create_amount_editor(params_layout)
        elif self.pattern['pattern_type'] == 'velocity_based':
            self.create_velocity_editor(params_layout)
        elif self.pattern['pattern_type'] == 'merchant_based':
            self.create_merchant_editor(params_layout)
        elif self.pattern['pattern_type'] == 'temporal_based':
            self.create_temporal_editor(params_layout)
        elif self.pattern['pattern_type'] == 'location_based':
            self.create_location_editor(params_layout)
            
        layout.addWidget(params_frame)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.apply_btn = QPushButton("Apply Changes")
        self.apply_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ThemeManager.COLORS['success']};
                color: white;
                padding: 6px 16px;
                font-weight: 500;
            }}
        """)
        self.apply_btn.clicked.connect(self.apply_changes)
        button_layout.addWidget(self.apply_btn)
        
        self.reset_btn = QPushButton("Reset to Default")
        self.reset_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ThemeManager.COLORS['warning']};
                color: white;
                padding: 6px 16px;
                font-weight: 500;
            }}
        """)
        self.reset_btn.clicked.connect(self.reset_to_default)
        button_layout.addWidget(self.reset_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
    def create_amount_editor(self, layout):
        """Create editor for amount-based rules"""
        # Threshold editor
        threshold_layout = QHBoxLayout()
        threshold_label = QLabel("Threshold ($):")
        threshold_label.setMinimumWidth(100)
        threshold_layout.addWidget(threshold_label)
        
        self.threshold_input = QSpinBox()
        self.threshold_input.setMinimum(0)
        self.threshold_input.setMaximum(1000000)
        self.threshold_input.setSingleStep(1000)
        self.threshold_input.setValue(self.pattern['parameters'].get('threshold', 10000))
        threshold_layout.addWidget(self.threshold_input)
        
        self.param_widgets['threshold'] = self.threshold_input
        layout.addLayout(threshold_layout)
        
    def create_velocity_editor(self, layout):
        """Create editor for velocity-based rules"""
        # Max transactions
        max_trans_layout = QHBoxLayout()
        max_trans_label = QLabel("Max transactions:")
        max_trans_label.setMinimumWidth(120)
        max_trans_layout.addWidget(max_trans_label)
        
        self.max_trans_input = QSpinBox()
        self.max_trans_input.setMinimum(1)
        self.max_trans_input.setMaximum(100)
        self.max_trans_input.setValue(self.pattern['parameters'].get('max_transactions', 5))
        max_trans_layout.addWidget(self.max_trans_input)
        
        self.param_widgets['max_transactions'] = self.max_trans_input
        layout.addLayout(max_trans_layout)
        
        # Time window
        time_layout = QHBoxLayout()
        time_label = QLabel("Time window (min):")
        time_label.setMinimumWidth(120)
        time_layout.addWidget(time_label)
        
        self.time_window_input = QSpinBox()
        self.time_window_input.setMinimum(1)
        self.time_window_input.setMaximum(1440)
        self.time_window_input.setValue(self.pattern['parameters'].get('time_window_minutes', 10))
        time_layout.addWidget(self.time_window_input)
        
        self.param_widgets['time_window_minutes'] = self.time_window_input
        layout.addLayout(time_layout)
        
    def create_merchant_editor(self, layout):
        """Create editor for merchant-based rules"""
        list_label = QLabel("High-risk categories:")
        layout.addWidget(list_label)
        
        self.category_list = QListWidget()
        self.category_list.setMaximumHeight(100)
        categories = self.pattern['parameters'].get('high_risk_categories', [])
        for cat in categories:
            self.category_list.addItem(cat)
            
        self.param_widgets['high_risk_categories'] = self.category_list
        layout.addWidget(self.category_list)
        
        # Add/Remove buttons
        cat_button_layout = QHBoxLayout()
        
        self.add_cat_input = QLineEdit()
        self.add_cat_input.setPlaceholderText("Add category...")
        cat_button_layout.addWidget(self.add_cat_input)
        
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self.add_category)
        cat_button_layout.addWidget(add_btn)
        
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self.remove_category)
        cat_button_layout.addWidget(remove_btn)
        
        layout.addLayout(cat_button_layout)
        
    def create_temporal_editor(self, layout):
        """Create editor for time-based rules"""
        list_label = QLabel("Suspicious hours (24h format):")
        layout.addWidget(list_label)
        
        self.hours_list = QListWidget()
        self.hours_list.setMaximumHeight(100)
        hours = self.pattern['parameters'].get('suspicious_hours', [])
        for hour in sorted(hours):
            self.hours_list.addItem(f"{hour:02d}:00")
            
        self.param_widgets['suspicious_hours'] = self.hours_list
        layout.addWidget(self.hours_list)
        
        # Add/Remove hours
        hour_button_layout = QHBoxLayout()
        
        self.hour_input = QSpinBox()
        self.hour_input.setMinimum(0)
        self.hour_input.setMaximum(23)
        hour_button_layout.addWidget(self.hour_input)
        
        add_hour_btn = QPushButton("Add Hour")
        add_hour_btn.clicked.connect(self.add_hour)
        hour_button_layout.addWidget(add_hour_btn)
        
        remove_hour_btn = QPushButton("Remove Hour")
        remove_hour_btn.clicked.connect(self.remove_hour)
        hour_button_layout.addWidget(remove_hour_btn)
        
        layout.addLayout(hour_button_layout)
        
    def create_location_editor(self, layout):
        """Create editor for location-based rules"""
        radius_layout = QHBoxLayout()
        radius_label = QLabel("Baseline radius (km):")
        radius_label.setMinimumWidth(120)
        radius_layout.addWidget(radius_label)
        
        self.radius_input = QSpinBox()
        self.radius_input.setMinimum(1)
        self.radius_input.setMaximum(10000)
        self.radius_input.setValue(self.pattern['parameters'].get('baseline_radius_km', 100))
        radius_layout.addWidget(self.radius_input)
        
        self.param_widgets['baseline_radius_km'] = self.radius_input
        layout.addLayout(radius_layout)
        
    def add_category(self):
        """Add a merchant category"""
        category = self.add_cat_input.text().strip()
        if category and self.category_list.findItems(category, Qt.MatchExactly) == []:
            self.category_list.addItem(category)
            self.add_cat_input.clear()
            
    def remove_category(self):
        """Remove selected merchant category"""
        current = self.category_list.currentItem()
        if current:
            self.category_list.takeItem(self.category_list.row(current))
            
    def add_hour(self):
        """Add a suspicious hour"""
        hour = self.hour_input.value()
        hour_text = f"{hour:02d}:00"
        if self.hours_list.findItems(hour_text, Qt.MatchExactly) == []:
            self.hours_list.addItem(hour_text)
            # Sort hours
            items = []
            for i in range(self.hours_list.count()):
                items.append(self.hours_list.item(i).text())
            self.hours_list.clear()
            for item in sorted(items):
                self.hours_list.addItem(item)
                
    def remove_hour(self):
        """Remove selected hour"""
        current = self.hours_list.currentItem()
        if current:
            self.hours_list.takeItem(self.hours_list.row(current))
            
    def get_parameters(self):
        """Get current parameter values"""
        params = {}
        
        if 'threshold' in self.param_widgets:
            params['threshold'] = self.param_widgets['threshold'].value()
            
        if 'max_transactions' in self.param_widgets:
            params['max_transactions'] = self.param_widgets['max_transactions'].value()
            
        if 'time_window_minutes' in self.param_widgets:
            params['time_window_minutes'] = self.param_widgets['time_window_minutes'].value()
            
        if 'baseline_radius_km' in self.param_widgets:
            params['baseline_radius_km'] = self.param_widgets['baseline_radius_km'].value()
            
        if 'high_risk_categories' in self.param_widgets:
            categories = []
            for i in range(self.param_widgets['high_risk_categories'].count()):
                categories.append(self.param_widgets['high_risk_categories'].item(i).text())
            params['high_risk_categories'] = categories
            
        if 'suspicious_hours' in self.param_widgets:
            hours = []
            for i in range(self.param_widgets['suspicious_hours'].count()):
                hour_text = self.param_widgets['suspicious_hours'].item(i).text()
                hours.append(int(hour_text.split(':')[0]))
            params['suspicious_hours'] = sorted(hours)
            
        # Keep any other parameters that weren't edited
        for key, value in self.pattern['parameters'].items():
            if key not in params:
                params[key] = value
                
        return params
        
    def apply_changes(self):
        """Apply parameter changes to database"""
        new_params = self.get_parameters()
        
        # Update database
        cursor = self.db.conn.cursor()
        cursor.execute("""
            UPDATE fraud_patterns 
            SET parameters = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (json.dumps(new_params), self.pattern['id']))
        self.db.conn.commit()
        
        # Update local pattern
        self.pattern['parameters'] = new_params
        
        # Emit signal
        self.rule_updated.emit(self.pattern)
        
        QMessageBox.information(self, "Success", "Rule parameters updated successfully!")
        
    def reset_to_default(self):
        """Reset parameters to default values"""
        reply = QMessageBox.question(self, "Reset to Default", 
                                   "Are you sure you want to reset this rule to default values?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Default values based on pattern type
            defaults = {
                'amount_based': {'threshold': 10000, 'currency': 'USD'},
                'velocity_based': {'max_transactions': 5, 'time_window_minutes': 10},
                'location_based': {'baseline_radius_km': 100},
                'merchant_based': {'high_risk_categories': ['gambling', 'crypto', 'wire_transfer']},
                'temporal_based': {'suspicious_hours': [0, 1, 2, 3, 4, 5]}
            }
            
            default_params = defaults.get(self.pattern['pattern_type'], {})
            
            # Update UI
            if 'threshold' in self.param_widgets and 'threshold' in default_params:
                self.param_widgets['threshold'].setValue(default_params['threshold'])
                
            if 'max_transactions' in self.param_widgets and 'max_transactions' in default_params:
                self.param_widgets['max_transactions'].setValue(default_params['max_transactions'])
                
            if 'time_window_minutes' in self.param_widgets and 'time_window_minutes' in default_params:
                self.param_widgets['time_window_minutes'].setValue(default_params['time_window_minutes'])
                
            if 'baseline_radius_km' in self.param_widgets and 'baseline_radius_km' in default_params:
                self.param_widgets['baseline_radius_km'].setValue(default_params['baseline_radius_km'])
                
            if 'high_risk_categories' in self.param_widgets and 'high_risk_categories' in default_params:
                self.param_widgets['high_risk_categories'].clear()
                for cat in default_params['high_risk_categories']:
                    self.param_widgets['high_risk_categories'].addItem(cat)
                    
            if 'suspicious_hours' in self.param_widgets and 'suspicious_hours' in default_params:
                self.param_widgets['suspicious_hours'].clear()
                for hour in sorted(default_params['suspicious_hours']):
                    self.param_widgets['suspicious_hours'].addItem(f"{hour:02d}:00")
                    
            # Apply the changes
            self.apply_changes()