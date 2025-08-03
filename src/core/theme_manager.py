from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor, QFontDatabase, QFont
from PySide6.QtCore import QFile, QTextStream
import os

class ThemeManager:
    # Lights-out color scheme
    COLORS = {
        # Base colors
        'background': '#000000',          # Pure black
        'surface': '#0a0a0a',            # Near black
        'surface-variant': '#121212',     # Slightly lighter
        'border': '#1a1a1a',             # Very dark gray
        
        # Text colors
        'text-primary': '#ffffff',        # Pure white
        'text-secondary': '#b3b3b3',      # Light gray
        'text-disabled': '#666666',       # Dark gray
        
        # Accent colors
        'primary': '#0080ff',            # Bright blue
        'primary-hover': '#0066cc',      # Darker blue
        'primary-light': '#4da6ff',      # Light blue
        
        'danger': '#ff3333',             # Bright red
        'danger-hover': '#cc0000',       # Darker red
        'danger-light': '#ff6666',       # Light red
        
        'success': '#00cc66',            # Green
        'warning': '#ffaa00',            # Orange
        
        # Special UI elements
        'chart-line': '#0080ff',         # Blue for charts
        'chart-fill': '#0080ff20',       # Transparent blue
        'shadow': '#00000080',           # Black with transparency
    }
    
    @classmethod
    def load_fonts(cls):
        """Load embedded fonts"""
        # Note: In production, we would download and embed Inter font
        # For now, we'll use system fonts with fallbacks
        return "Inter, -apple-system, 'Segoe UI', 'Roboto', sans-serif"
    
    @classmethod
    def apply_dark_theme(cls, app: QApplication):
        # Load fonts
        font_family = cls.load_fonts()
        
        # Set default font
        default_font = QFont(font_family.split(',')[0].strip(), 10)
        app.setFont(default_font)
        
        dark_style = f"""
        * {{
            font-family: {font_family};
            font-size: 13px;
            font-weight: 400;
        }}
        
        QWidget {{
            background-color: {cls.COLORS['background']};
            color: {cls.COLORS['text-primary']};
        }}
        
        QMainWindow {{
            background-color: {cls.COLORS['background']};
        }}
        
        /* Minimal frame styling */
        QFrame {{
            background-color: transparent;
            border: none;
        }}
        
        QFrame#sidebar {{
            background-color: {cls.COLORS['surface']};
            border-right: 1px solid {cls.COLORS['border']};
        }}
        
        /* Buttons */
        QPushButton {{
            background-color: {cls.COLORS['primary']};
            color: {cls.COLORS['text-primary']};
            border: none;
            border-radius: 4px;
            padding: 6px 14px;
            font-weight: 500;
            min-height: 32px;
        }}
        
        QPushButton:hover {{
            background-color: {cls.COLORS['primary-hover']};
        }}
        
        QPushButton:pressed {{
            background-color: {cls.COLORS['primary-hover']};
        }}
        
        QPushButton:disabled {{
            background-color: {cls.COLORS['surface-variant']};
            color: {cls.COLORS['text-disabled']};
        }}
        
        /* Navigation buttons */
        QPushButton[flat="true"] {{
            background-color: transparent;
            color: {cls.COLORS['text-secondary']};
            text-align: left;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: 400;
            border: none;
        }}
        
        QPushButton[flat="true"]:hover {{
            background-color: {cls.COLORS['surface-variant']};
            color: {cls.COLORS['text-primary']};
        }}
        
        QPushButton[flat="true"]:checked {{
            background-color: {cls.COLORS['primary']};
            color: {cls.COLORS['text-primary']};
            font-weight: 500;
        }}
        
        /* Input fields */
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {cls.COLORS['surface']};
            border: 1px solid {cls.COLORS['border']};
            border-radius: 4px;
            padding: 6px;
            color: {cls.COLORS['text-primary']};
            selection-background-color: {cls.COLORS['primary']};
            selection-color: {cls.COLORS['text-primary']};
        }}
        
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border-color: {cls.COLORS['primary']};
            outline: none;
        }}
        
        /* Labels */
        QLabel {{
            color: {cls.COLORS['text-primary']};
            background-color: transparent;
        }}
        
        QLabel#heading {{
            font-size: 28px;
            font-weight: 700;
            color: {cls.COLORS['text-primary']};
        }}
        
        QLabel#subheading {{
            font-size: 18px;
            font-weight: 600;
            color: {cls.COLORS['text-primary']};
        }}
        
        QLabel#caption {{
            font-size: 11px;
            font-weight: 400;
            color: {cls.COLORS['text-secondary']};
        }}
        
        /* Group boxes - minimal style */
        QGroupBox {{
            border: none;
            margin-top: 8px;
            padding-top: 8px;
            font-weight: 500;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 8px;
            padding: 0 4px;
            color: {cls.COLORS['text-primary']};
        }}
        
        /* Tab widget */
        QTabWidget::pane {{
            background-color: transparent;
            border: none;
        }}
        
        QTabBar::tab {{
            background-color: transparent;
            color: {cls.COLORS['text-secondary']};
            padding: 6px 12px;
            margin-right: 4px;
            border-bottom: 2px solid transparent;
        }}
        
        QTabBar::tab:selected {{
            color: {cls.COLORS['primary']};
            border-bottom-color: {cls.COLORS['primary']};
            font-weight: 500;
        }}
        
        QTabBar::tab:hover:!selected {{
            color: {cls.COLORS['text-primary']};
        }}
        
        /* Tables */
        QTableWidget {{
            background-color: {cls.COLORS['surface']};
            alternate-background-color: {cls.COLORS['surface-variant']};
            gridline-color: {cls.COLORS['border']};
            border: none;
            border-radius: 4px;
        }}
        
        QTableWidget::item {{
            padding: 4px;
            color: {cls.COLORS['text-primary']};
        }}
        
        QTableWidget::item:selected {{
            background-color: {cls.COLORS['primary']};
            color: {cls.COLORS['text-primary']};
        }}
        
        QHeaderView::section {{
            background-color: {cls.COLORS['background']};
            color: {cls.COLORS['text-secondary']};
            font-weight: 500;
            padding: 6px;
            border: none;
            border-bottom: 1px solid {cls.COLORS['border']};
        }}
        
        /* Scrollbars - minimal */
        QScrollBar:vertical {{
            background-color: transparent;
            width: 8px;
            border: none;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {cls.COLORS['border']};
            border-radius: 4px;
            min-height: 30px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {cls.COLORS['text-disabled']};
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        
        /* Progress bars */
        QProgressBar {{
            background-color: {cls.COLORS['surface-variant']};
            border-radius: 4px;
            text-align: center;
            height: 16px;
            color: {cls.COLORS['text-primary']};
            border: none;
        }}
        
        QProgressBar::chunk {{
            background-color: {cls.COLORS['primary']};
            border-radius: 4px;
        }}
        
        /* Menus */
        QMenu {{
            background-color: {cls.COLORS['surface-variant']};
            border: 1px solid {cls.COLORS['border']};
            border-radius: 4px;
            padding: 4px;
        }}
        
        QMenu::item {{
            padding: 6px 20px;
            border-radius: 2px;
            color: {cls.COLORS['text-primary']};
        }}
        
        QMenu::item:selected {{
            background-color: {cls.COLORS['primary']};
            color: {cls.COLORS['text-primary']};
        }}
        
        /* Message box */
        QMessageBox {{
            background-color: {cls.COLORS['surface']};
        }}
        
        QMessageBox QPushButton {{
            min-width: 70px;
        }}
        
        /* Custom elements for banking */
        QWidget#fraudAlert {{
            background-color: {cls.COLORS['danger']};
            border-radius: 4px;
            padding: 8px;
        }}
        
        QWidget#successNotification {{
            background-color: {cls.COLORS['success']};
            border-radius: 4px;
            padding: 8px;
        }}
        
        QWidget#warningNotification {{
            background-color: {cls.COLORS['warning']};
            border-radius: 4px;
            padding: 8px;
        }}
        
        /* Stat cards - no border */
        QFrame.stat-card {{
            background-color: {cls.COLORS['surface']};
            border: none;
            border-radius: 6px;
            padding: 16px;
        }}
        
        QFrame.stat-card:hover {{
            background-color: {cls.COLORS['surface-variant']};
        }}
        
        /* Metric display - minimal */
        QFrame#metric-display {{
            background-color: {cls.COLORS['surface']};
            border: none;
            border-radius: 6px;
            padding: 16px;
        }}
        
        QFrame#metric-display:hover {{
            background-color: {cls.COLORS['surface-variant']};
        }}
        
        /* Remove outlines from scroll areas */
        QScrollArea {{
            border: none;
            background-color: transparent;
        }}
        
        QScrollArea > QWidget > QWidget {{
            background-color: transparent;
        }}
        
        /* Charts */
        QChartView {{
            background-color: {cls.COLORS['surface']};
            border: none;
            border-radius: 4px;
        }}
        """
        
        app.setStyleSheet(dark_style)
        
        # Set application palette for native widgets
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(cls.COLORS['background']))
        palette.setColor(QPalette.WindowText, QColor(cls.COLORS['text-primary']))
        palette.setColor(QPalette.Base, QColor(cls.COLORS['surface']))
        palette.setColor(QPalette.AlternateBase, QColor(cls.COLORS['surface-variant']))
        palette.setColor(QPalette.ToolTipBase, QColor(cls.COLORS['surface-variant']))
        palette.setColor(QPalette.ToolTipText, QColor(cls.COLORS['text-primary']))
        palette.setColor(QPalette.Text, QColor(cls.COLORS['text-primary']))
        palette.setColor(QPalette.Button, QColor(cls.COLORS['surface-variant']))
        palette.setColor(QPalette.ButtonText, QColor(cls.COLORS['text-primary']))
        palette.setColor(QPalette.BrightText, QColor(cls.COLORS['text-primary']))
        palette.setColor(QPalette.Link, QColor(cls.COLORS['primary']))
        palette.setColor(QPalette.Highlight, QColor(cls.COLORS['primary']))
        palette.setColor(QPalette.HighlightedText, QColor(cls.COLORS['text-primary']))
        
        app.setPalette(palette)