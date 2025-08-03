from PySide6.QtWidgets import QSplashScreen, QProgressBar, QLabel, QVBoxLayout, QWidget
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QPainter, QBrush, QColor, QFont, QLinearGradient, QPainterPath
from core.theme_manager import ThemeManager

class SplashScreen(QSplashScreen):
    def __init__(self):
        # Create a custom pixmap for splash screen
        pixmap = QPixmap(600, 400)
        pixmap.fill(Qt.transparent)
        
        # Draw custom content on pixmap with rounded corners
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Create rounded rectangle path
        path = QPainterPath()
        path.addRoundedRect(0, 0, 600, 400, 20, 20)
        painter.setClipPath(path)
        
        # Fill background
        painter.fillRect(pixmap.rect(), QColor(ThemeManager.COLORS['background']))
        
        # Draw gradient accent
        gradient = QLinearGradient(0, 0, 600, 400)
        gradient.setColorAt(0, QColor(ThemeManager.COLORS['primary'] + '20'))
        gradient.setColorAt(1, QColor(ThemeManager.COLORS['danger'] + '10'))
        painter.fillRect(pixmap.rect(), gradient)
        
        # Draw title - full name
        title_font = QFont("Inter", 28, QFont.Bold)
        painter.setFont(title_font)
        painter.setPen(QColor(ThemeManager.COLORS['text-primary']))
        painter.drawText(pixmap.rect().adjusted(20, -50, -20, 0), 
                        Qt.AlignCenter | Qt.TextWordWrap, "Banking Security Platform")
        
        # Draw subtitle
        subtitle_font = QFont("Inter", 14, QFont.Normal)
        painter.setFont(subtitle_font)
        painter.setPen(QColor(ThemeManager.COLORS['text-secondary']))
        painter.drawText(pixmap.rect().adjusted(0, 20, 0, 0), 
                        Qt.AlignCenter, "Advanced Fraud Detection & Risk Assessment")
        
        # Draw version
        version_font = QFont("Inter", 10)
        painter.setFont(version_font)
        painter.setPen(QColor(ThemeManager.COLORS['text-disabled']))
        painter.drawText(pixmap.rect().adjusted(0, 0, -20, -20), 
                        Qt.AlignBottom | Qt.AlignRight, "v1.0.0")
        
        painter.end()
        
        super().__init__(pixmap)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Initialize progress
        self.progress = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(20)
        
    def update_progress(self):
        self.progress += 3
        if self.progress > 100:
            self.timer.stop()
            return
            
        # Update splash screen message
        color = QColor(ThemeManager.COLORS['text-secondary'])
        
        if self.progress < 20:
            self.showMessage("Initializing application...", 
                           Qt.AlignBottom | Qt.AlignCenter, color)
        elif self.progress < 40:
            self.showMessage("Loading security modules...", 
                           Qt.AlignBottom | Qt.AlignCenter, color)
        elif self.progress < 60:
            self.showMessage("Preparing database connections...", 
                           Qt.AlignBottom | Qt.AlignCenter, color)
        elif self.progress < 80:
            self.showMessage("Loading AI models...", 
                           Qt.AlignBottom | Qt.AlignCenter, color)
        else:
            self.showMessage("Starting application...", 
                           Qt.AlignBottom | Qt.AlignCenter, color)