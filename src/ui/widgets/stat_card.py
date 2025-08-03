from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont

class StatCard(QFrame):
    def __init__(self, title, value, change, color):
        super().__init__()
        self.color = color
        self.setup_ui(title, value, change)
        
    def setup_ui(self, title, value, change):
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #313244;
                border-radius: 12px;
                border: 2px solid {self.color}40;
                padding: 20px;
            }}
            QFrame:hover {{
                border-color: {self.color};
                background-color: #45475a;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: #a6adc8;
                font-size: 14px;
                font-weight: 500;
            }}
        """)
        layout.addWidget(title_label)
        
        # Value
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet(f"""
            QLabel {{
                color: {self.color};
                font-size: 36px;
                font-weight: bold;
            }}
        """)
        layout.addWidget(self.value_label)
        
        # Change indicator
        change_label = QLabel(change)
        change_color = "#a6e3a1" if change.startswith("+") else "#f38ba8"
        change_label.setStyleSheet(f"""
            QLabel {{
                color: {change_color};
                font-size: 14px;
                font-weight: 600;
            }}
        """)
        layout.addWidget(change_label)
        
    def set_value(self, value):
        self.value_label.setText(value)
        
        # Animate the card
        self.animate_update()
        
    def animate_update(self):
        # Create a subtle scale animation
        animation = QPropertyAnimation(self, b"scale")
        animation.setDuration(200)
        animation.setStartValue(1.0)
        animation.setKeyValueAt(0.5, 1.05)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.OutBounce)
        animation.start()