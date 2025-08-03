from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFrame, QCheckBox)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from core.theme_manager import ThemeManager

class LoginDialog(QDialog):
    login_requested = Signal(str, str)  # username, password
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Banking Security Platform - Login")
        self.setFixedSize(400, 500)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Container frame
        container = QFrame()
        container.setObjectName("login-container")
        container.setStyleSheet(f"""
            QFrame#login-container {{
                background-color: {ThemeManager.COLORS['surface']};
                border: 1px solid {ThemeManager.COLORS['border']};
                border-radius: 12px;
            }}
        """)
        
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(20)
        container_layout.setContentsMargins(40, 40, 40, 40)
        
        # Logo section
        logo_frame = QFrame()
        logo_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {ThemeManager.COLORS['primary']};
                border-radius: 8px;
                padding: 20px;
            }}
        """)
        logo_layout = QVBoxLayout(logo_frame)
        
        logo = QLabel("BSP")
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 48px;
                font-weight: 900;
                letter-spacing: -2px;
            }
        """)
        logo_layout.addWidget(logo)
        
        container_layout.addWidget(logo_frame)
        
        # Title
        title = QLabel("Welcome Back")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"""
            QLabel {{
                color: {ThemeManager.COLORS['text-primary']};
                font-size: 24px;
                font-weight: 700;
                margin-bottom: 8px;
            }}
        """)
        container_layout.addWidget(title)
        
        subtitle = QLabel("Sign in to continue to Banking Security Platform")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet(f"""
            QLabel {{
                color: {ThemeManager.COLORS['text-secondary']};
                font-size: 14px;
                margin-bottom: 20px;
            }}
        """)
        container_layout.addWidget(subtitle)
        
        # Username field
        username_label = QLabel("Username")
        username_label.setStyleSheet(f"""
            QLabel {{
                color: {ThemeManager.COLORS['text-secondary']};
                font-size: 12px;
                font-weight: 600;
                margin-bottom: 4px;
            }}
        """)
        container_layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {ThemeManager.COLORS['background']};
                border: 1px solid {ThemeManager.COLORS['border']};
                border-radius: 6px;
                padding: 12px 16px;
                font-size: 14px;
                color: {ThemeManager.COLORS['text-primary']};
            }}
            QLineEdit:focus {{
                border-color: {ThemeManager.COLORS['primary']};
            }}
        """)
        container_layout.addWidget(self.username_input)
        
        # Password field
        password_label = QLabel("Password")
        password_label.setStyleSheet(f"""
            QLabel {{
                color: {ThemeManager.COLORS['text-secondary']};
                font-size: 12px;
                font-weight: 600;
                margin-bottom: 4px;
                margin-top: 12px;
            }}
        """)
        container_layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {ThemeManager.COLORS['background']};
                border: 1px solid {ThemeManager.COLORS['border']};
                border-radius: 6px;
                padding: 12px 16px;
                font-size: 14px;
                color: {ThemeManager.COLORS['text-primary']};
            }}
            QLineEdit:focus {{
                border-color: {ThemeManager.COLORS['primary']};
            }}
        """)
        container_layout.addWidget(self.password_input)
        
        # Remember me checkbox
        self.remember_checkbox = QCheckBox("Remember me")
        self.remember_checkbox.setStyleSheet(f"""
            QCheckBox {{
                color: {ThemeManager.COLORS['text-secondary']};
                font-size: 14px;
                margin-top: 12px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 1px solid {ThemeManager.COLORS['border']};
                background-color: {ThemeManager.COLORS['background']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {ThemeManager.COLORS['primary']};
                border-color: {ThemeManager.COLORS['primary']};
            }}
        """)
        container_layout.addWidget(self.remember_checkbox)
        
        # Login button
        self.login_button = QPushButton("Sign In")
        self.login_button.setCursor(Qt.PointingHandCursor)
        self.login_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {ThemeManager.COLORS['primary']};
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 14px;
                font-size: 16px;
                font-weight: 600;
                margin-top: 20px;
            }}
            QPushButton:hover {{
                background-color: {ThemeManager.COLORS['primary-hover']};
            }}
            QPushButton:pressed {{
                background-color: {ThemeManager.COLORS['primary-hover']};
                padding: 15px 14px 13px 14px;
            }}
        """)
        self.login_button.clicked.connect(self.handle_login)
        container_layout.addWidget(self.login_button)
        
        # Demo hint
        hint = QLabel("Demo: username 'admin', password 'admin123'")
        hint.setAlignment(Qt.AlignCenter)
        hint.setStyleSheet(f"""
            QLabel {{
                color: {ThemeManager.COLORS['text-disabled']};
                font-size: 12px;
                margin-top: 20px;
            }}
        """)
        container_layout.addWidget(hint)
        
        main_layout.addWidget(container)
        
        # Connect enter key
        self.username_input.returnPressed.connect(self.handle_login)
        self.password_input.returnPressed.connect(self.handle_login)
        
        # Focus username field
        self.username_input.setFocus()
        
    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            return
            
        self.login_button.setText("Signing in...")
        self.login_button.setEnabled(False)
        
        self.login_requested.emit(username, password)
        
    def reset_button(self):
        self.login_button.setText("Sign In")
        self.login_button.setEnabled(True)
        self.password_input.clear()
        self.password_input.setFocus()