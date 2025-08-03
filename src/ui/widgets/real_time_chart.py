from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QPainterPath
from collections import deque

class RealTimeChart(QWidget):
    def __init__(self, title, max_points=50):
        super().__init__()
        self.title = title
        self.max_points = max_points
        self.data_points = deque(maxlen=max_points)
        self.setMinimumHeight(300)
        
    def add_data_point(self, value):
        self.data_points.append(value)
        self.update()  # Trigger repaint
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Background
        painter.fillRect(self.rect(), QColor("#313244"))
        
        # Draw border
        painter.setPen(QPen(QColor("#45475a"), 2))
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 10, 10)
        
        # Title
        painter.setPen(QColor("#f5e0dc"))
        title_font = QFont("Segoe UI", 16, QFont.Bold)
        painter.setFont(title_font)
        painter.drawText(20, 30, self.title)
        
        if not self.data_points:
            return
            
        # Calculate chart area
        chart_rect = self.rect().adjusted(20, 60, -20, -20)
        
        # Draw grid lines
        painter.setPen(QPen(QColor("#45475a"), 1, Qt.DashLine))
        for i in range(5):
            y = chart_rect.top() + (i * chart_rect.height() / 4)
            painter.drawLine(chart_rect.left(), y, chart_rect.right(), y)
            
        # Prepare data for drawing
        if self.data_points:
            max_value = max(self.data_points) if self.data_points else 1
            min_value = min(self.data_points) if self.data_points else 0
            value_range = max_value - min_value if max_value != min_value else 1
            
            # Create gradient path
            path = QPainterPath()
            gradient_path = QPainterPath()
            
            # Calculate points
            points = []
            for i, value in enumerate(self.data_points):
                x = chart_rect.left() + (i * chart_rect.width() / (self.max_points - 1))
                normalized_value = (value - min_value) / value_range
                y = chart_rect.bottom() - (normalized_value * chart_rect.height())
                points.append((x, y))
                
            if points:
                # Start gradient path
                gradient_path.moveTo(points[0][0], chart_rect.bottom())
                
                # Draw smooth curve
                path.moveTo(points[0][0], points[0][1])
                gradient_path.lineTo(points[0][0], points[0][1])
                
                for i in range(1, len(points)):
                    # Create smooth curve using cubic bezier
                    if i < len(points) - 1:
                        ctrl1_x = points[i-1][0] + (points[i][0] - points[i-1][0]) / 2
                        ctrl1_y = points[i-1][1]
                        ctrl2_x = points[i][0] - (points[i+1][0] - points[i][0]) / 2
                        ctrl2_y = points[i][1]
                        
                        path.cubicTo(ctrl1_x, ctrl1_y, ctrl2_x, ctrl2_y, 
                                   points[i][0], points[i][1])
                        gradient_path.cubicTo(ctrl1_x, ctrl1_y, ctrl2_x, ctrl2_y,
                                            points[i][0], points[i][1])
                    else:
                        path.lineTo(points[i][0], points[i][1])
                        gradient_path.lineTo(points[i][0], points[i][1])
                
                # Complete gradient path
                gradient_path.lineTo(points[-1][0], chart_rect.bottom())
                gradient_path.closeSubpath()
                
                # Draw gradient fill
                gradient = painter.brush()
                gradient_color = QColor("#89b4fa")
                gradient_color.setAlpha(50)
                painter.fillPath(gradient_path, gradient_color)
                
                # Draw line
                painter.setPen(QPen(QColor("#89b4fa"), 3))
                painter.drawPath(path)
                
                # Draw points
                painter.setPen(QPen(QColor("#89b4fa"), 2))
                painter.setBrush(QColor("#1e1e2e"))
                for x, y in points[-5:]:  # Only show last 5 points
                    painter.drawEllipse(int(x-4), int(y-4), 8, 8)
                    
                # Draw current value
                if points:
                    current_value = self.data_points[-1]
                    painter.setPen(QColor("#cdd6f4"))
                    value_font = QFont("Segoe UI", 12)
                    painter.setFont(value_font)
                    painter.drawText(chart_rect.right() - 100, 30, 
                                   f"Current: {current_value:.1f}")