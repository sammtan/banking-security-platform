from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer
from PySide6.QtGui import QFont
from core.theme_manager import ThemeManager

class MetricDisplay(QFrame):
    def __init__(self, title, value, subtitle, accent_color):
        super().__init__()
        self.accent_color = accent_color
        self.setObjectName("metric-display")
        
        self.setup_ui(title, value, subtitle)
        
    def setup_ui(self, title, value, subtitle):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {ThemeManager.COLORS['text-secondary']};
                font-size: 12px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
        """)
        layout.addWidget(title_label)
        
        # Value
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet(f"""
            QLabel {{
                color: {self.accent_color};
                font-size: 36px;
                font-weight: 700;
                letter-spacing: -1px;
            }}
        """)
        layout.addWidget(self.value_label)
        
        # Subtitle
        self.subtitle_label = QLabel(subtitle)
        self.subtitle_label.setStyleSheet(f"""
            QLabel {{
                color: {ThemeManager.COLORS['text-disabled']};
                font-size: 12px;
                font-weight: 400;
            }}
        """)
        layout.addWidget(self.subtitle_label)
        
    def update_value(self, value, subtitle=None):
        self.value_label.setText(str(value))
        if subtitle:
            self.subtitle_label.setText(subtitle)
            
        # Add visual feedback
        self.flash_update()
        
    def flash_update(self):
        # Create a subtle background flash effect when value updates
        self.setStyleSheet(f"""
            QFrame#metric-display {{
                background-color: {self.accent_color}20;
                border-radius: 6px;
                padding: 16px;
            }}
        """)
        QTimer.singleShot(200, lambda: self.setStyleSheet(""))