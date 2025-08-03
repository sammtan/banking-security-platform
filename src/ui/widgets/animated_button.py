from PySide6.QtWidgets import QPushButton, QGraphicsDropShadowEffect
from PySide6.QtCore import QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor

class AnimatedButton(QPushButton):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        
        # Add shadow effect
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(15)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(3)
        self.shadow.setColor(QColor(0, 0, 0, 60))
        self.setGraphicsEffect(self.shadow)
        
        # Animation for hover effect
        self._animation = QPropertyAnimation(self, b"color")
        self._animation.setDuration(200)
        self._animation.setEasingCurve(QEasingCurve.InOutQuad)
        
    def enterEvent(self, event):
        self.shadow.setBlurRadius(20)
        self.shadow.setYOffset(5)
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self.shadow.setBlurRadius(15)
        self.shadow.setYOffset(3)
        super().leaveEvent(event)
        
    def mousePressEvent(self, event):
        self.shadow.setBlurRadius(10)
        self.shadow.setYOffset(1)
        super().mousePressEvent(event)
        
    def mouseReleaseEvent(self, event):
        self.shadow.setBlurRadius(20)
        self.shadow.setYOffset(5)
        super().mouseReleaseEvent(event)