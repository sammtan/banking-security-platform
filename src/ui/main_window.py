from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QStackedWidget, QPushButton, QLabel, QFrame,
                             QGraphicsDropShadowEffect, QSizePolicy)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Signal, QSize
from PySide6.QtGui import QIcon, QColor
from ui.pages.dashboard import DashboardPage
from ui.pages.transactions import TransactionsPage
from ui.pages.fraud_detection import FraudDetectionPage
from ui.pages.risk_assessment import RiskAssessmentPage
from core.theme_manager import ThemeManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Banking Security Platform")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1000, 700)  # Smaller minimum for better responsiveness
        self.sidebar_expanded = True
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create sidebar
        self.sidebar = self.create_sidebar()
        main_layout.addWidget(self.sidebar)
        
        # Create content area
        self.content_stack = QStackedWidget()
        self.content_stack.setObjectName("contentArea")
        main_layout.addWidget(self.content_stack, 1)
        
        # Add pages
        self.dashboard_page = DashboardPage()
        self.transactions_page = TransactionsPage()
        self.fraud_page = FraudDetectionPage()
        self.risk_page = RiskAssessmentPage()
        
        self.content_stack.addWidget(self.dashboard_page)
        self.content_stack.addWidget(self.transactions_page)
        self.content_stack.addWidget(self.fraud_page)
        self.content_stack.addWidget(self.risk_page)
        
        # Set default page
        self.show_dashboard()
        
    def create_sidebar(self):
        self.sidebar_widget = QFrame()
        self.sidebar_widget.setObjectName("sidebar")
        self.sidebar_widget.setMinimumWidth(60)
        self.sidebar_widget.setMaximumWidth(280)
        self.sidebar_widget.setFixedWidth(280)
        
        layout = QVBoxLayout(self.sidebar_widget)
        layout.setSpacing(4)
        layout.setContentsMargins(12, 16, 12, 16)
        
        # Logo/Title
        logo_frame = QFrame()
        logo_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {ThemeManager.COLORS['primary']};
                border-radius: 6px;
                padding: 12px;
                margin-bottom: 8px;
            }}
        """)
        logo_layout = QVBoxLayout(logo_frame)
        
        self.title = QLabel("BSP")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 36px;
                font-weight: 900;
                letter-spacing: -1px;
            }
        """)
        logo_layout.addWidget(self.title)
        
        self.subtitle = QLabel("Banking Security Platform")
        self.subtitle.setAlignment(Qt.AlignCenter)
        self.subtitle.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 12px;
                font-weight: 400;
                opacity: 0.9;
            }
        """)
        logo_layout.addWidget(self.subtitle)
        
        layout.addWidget(logo_frame)
        
        # Navigation section
        self.nav_label = QLabel("Navigation")
        self.nav_label.setStyleSheet(f"""
            QLabel {{
                color: {ThemeManager.COLORS['text-secondary']};
                font-size: 11px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 1px;
                padding: 8px 12px 4px 12px;
            }}
        """)
        layout.addWidget(self.nav_label)
        
        # Navigation buttons
        self.dashboard_btn = self.create_nav_button("Dashboard", "home")
        self.dashboard_btn.clicked.connect(self.show_dashboard)
        layout.addWidget(self.dashboard_btn)
        
        self.transactions_btn = self.create_nav_button("Transactions", "list")
        self.transactions_btn.clicked.connect(self.show_transactions)
        layout.addWidget(self.transactions_btn)
        
        self.fraud_btn = self.create_nav_button("Fraud Detection", "shield")
        self.fraud_btn.clicked.connect(self.show_fraud_detection)
        layout.addWidget(self.fraud_btn)
        
        self.risk_btn = self.create_nav_button("Risk Assessment", "chart")
        self.risk_btn.clicked.connect(self.show_risk_assessment)
        layout.addWidget(self.risk_btn)
        
        # Add stretch
        layout.addStretch()
        
        # Status section
        status_frame = QFrame()
        status_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {ThemeManager.COLORS['surface-variant']};
                border-radius: 8px;
                padding: 16px;
            }}
        """)
        status_layout = QVBoxLayout(status_frame)
        
        status_label = QLabel("System Status")
        status_label.setStyleSheet(f"""
            QLabel {{
                color: {ThemeManager.COLORS['text-secondary']};
                font-size: 11px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-bottom: 8px;
            }}
        """)
        status_layout.addWidget(status_label)
        
        self.status_indicator = QLabel("● Connected")
        self.status_indicator.setStyleSheet(f"""
            QLabel {{
                color: {ThemeManager.COLORS['success']};
                font-size: 14px;
                font-weight: 500;
            }}
        """)
        status_layout.addWidget(self.status_indicator)
        
        layout.addWidget(status_frame)
        
        return self.sidebar_widget
        
    def create_nav_button(self, text, icon_name=None):
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setFlat(True)
        btn.setCursor(Qt.PointingHandCursor)
        return btn
        
    def show_dashboard(self):
        self.content_stack.setCurrentWidget(self.dashboard_page)
        self.update_nav_selection(self.dashboard_btn)
        
    def show_transactions(self):
        self.content_stack.setCurrentWidget(self.transactions_page)
        self.update_nav_selection(self.transactions_btn)
        
    def show_fraud_detection(self):
        self.content_stack.setCurrentWidget(self.fraud_page)
        self.update_nav_selection(self.fraud_btn)
        
    def show_risk_assessment(self):
        self.content_stack.setCurrentWidget(self.risk_page)
        self.update_nav_selection(self.risk_btn)
        
    def update_nav_selection(self, selected_btn):
        for btn in [self.dashboard_btn, self.transactions_btn, 
                   self.fraud_btn, self.risk_btn]:
            btn.setChecked(btn == selected_btn)
            
    def toggle_sidebar(self):
        """Toggle sidebar between expanded and collapsed states"""
        if self.sidebar_expanded:
            # Collapse
            self.sidebar_widget.setFixedWidth(60)
            self.subtitle.hide()
            self.nav_label.hide()
            self.title.setText("B")
            self.title.setStyleSheet("""
                QLabel {
                    color: #ffffff;
                    font-size: 24px;
                    font-weight: 900;
                }
            """)
            # Update buttons to show only icons
            self.dashboard_btn.setText("🏠")
            self.transactions_btn.setText("📊")
            self.fraud_btn.setText("🛡️")
            self.risk_btn.setText("📈")
        else:
            # Expand
            self.sidebar_widget.setFixedWidth(280)
            self.subtitle.show()
            self.nav_label.show()
            self.title.setText("BSP")
            self.title.setStyleSheet("""
                QLabel {
                    color: #ffffff;
                    font-size: 36px;
                    font-weight: 900;
                    letter-spacing: -1px;
                }
            """)
            # Update buttons to show text
            self.dashboard_btn.setText("Dashboard")
            self.transactions_btn.setText("Transactions")
            self.fraud_btn.setText("Fraud Detection")
            self.risk_btn.setText("Risk Assessment")
            
        self.sidebar_expanded = not self.sidebar_expanded
        
