"""
Chart widget for data visualization
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QPainterPath
from core.theme_manager import ThemeManager
from collections import deque
import math

class LineChart(QWidget):
    """Real-time line chart widget"""
    
    def __init__(self, title="", max_points=50):
        super().__init__()
        self.title = title
        self.max_points = max_points
        self.data_points = deque(maxlen=max_points)
        self.setMinimumHeight(200)
        
    def add_data_point(self, value):
        """Add a new data point to the chart"""
        self.data_points.append(value)
        self.update()
        
    def set_data(self, data):
        """Set all data points at once"""
        self.data_points.clear()
        for value in data[-self.max_points:]:
            self.data_points.append(value)
        self.update()
        
    def paintEvent(self, event):
        """Paint the chart"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Background
        painter.fillRect(self.rect(), QColor(ThemeManager.COLORS['surface']))
        
        # Draw border
        painter.setPen(QPen(QColor(ThemeManager.COLORS['border']), 1))
        painter.drawRect(self.rect().adjusted(0, 0, -1, -1))
        
        if not self.data_points:
            # No data message
            painter.setPen(QColor(ThemeManager.COLORS['text-disabled']))
            painter.setFont(QFont("Inter", 10))
            painter.drawText(self.rect(), Qt.AlignCenter, "No data available")
            return
            
        # Chart area
        margin = 20
        chart_rect = self.rect().adjusted(margin, margin + 20, -margin, -margin - 10)
        
        # Title
        if self.title:
            painter.setPen(QColor(ThemeManager.COLORS['text-primary']))
            painter.setFont(QFont("Inter", 11, QFont.Bold))
            painter.drawText(self.rect().adjusted(margin, 5, -margin, 0), 
                           Qt.AlignLeft | Qt.AlignTop, self.title)
        
        # Calculate scale
        min_val = min(self.data_points) if self.data_points else 0
        max_val = max(self.data_points) if self.data_points else 1
        val_range = max_val - min_val
        if val_range == 0:
            val_range = 1
            
        # Draw grid lines
        painter.setPen(QPen(QColor(ThemeManager.COLORS['border']), 1, Qt.DotLine))
        grid_lines = 5
        for i in range(grid_lines + 1):
            y = chart_rect.top() + (chart_rect.height() * i / grid_lines)
            painter.drawLine(chart_rect.left(), y, chart_rect.right(), y)
            
            # Y-axis labels
            value = max_val - (val_range * i / grid_lines)
            label = f"{value:.1f}"
            painter.setPen(QColor(ThemeManager.COLORS['text-secondary']))
            painter.setFont(QFont("Inter", 8))
            label_rect = painter.boundingRect(0, 0, 100, 20, Qt.AlignLeft, label)
            painter.drawText(chart_rect.left() - label_rect.width() - 5, 
                           y - label_rect.height()/2, 
                           label_rect.width(), label_rect.height(), 
                           Qt.AlignRight, label)
            painter.setPen(QPen(QColor(ThemeManager.COLORS['border']), 1, Qt.DotLine))
        
        # Draw line chart
        if len(self.data_points) > 1:
            # Create path
            path = QPainterPath()
            x_step = chart_rect.width() / (self.max_points - 1)
            
            for i, value in enumerate(self.data_points):
                x = chart_rect.left() + (i * x_step)
                y = chart_rect.bottom() - ((value - min_val) / val_range * chart_rect.height())
                
                if i == 0:
                    path.moveTo(x, y)
                else:
                    path.lineTo(x, y)
            
            # Draw the line
            painter.setPen(QPen(QColor(ThemeManager.COLORS['primary']), 2))
            painter.drawPath(path)
            
            # Draw points
            painter.setBrush(QBrush(QColor(ThemeManager.COLORS['primary'])))
            for i, value in enumerate(self.data_points):
                x = chart_rect.left() + (i * x_step)
                y = chart_rect.bottom() - ((value - min_val) / val_range * chart_rect.height())
                painter.drawEllipse(x - 3, y - 3, 6, 6)

class BarChart(QWidget):
    """Bar chart widget for categorical data"""
    
    def __init__(self, title=""):
        super().__init__()
        self.title = title
        self.data = {}
        self.setMinimumHeight(200)
        
    def set_data(self, data):
        """Set chart data as dict {category: value}"""
        self.data = data
        self.update()
        
    def paintEvent(self, event):
        """Paint the bar chart"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Background
        painter.fillRect(self.rect(), QColor(ThemeManager.COLORS['surface']))
        
        # Draw border
        painter.setPen(QPen(QColor(ThemeManager.COLORS['border']), 1))
        painter.drawRect(self.rect().adjusted(0, 0, -1, -1))
        
        if not self.data:
            # No data message
            painter.setPen(QColor(ThemeManager.COLORS['text-disabled']))
            painter.setFont(QFont("Inter", 10))
            painter.drawText(self.rect(), Qt.AlignCenter, "No data available")
            return
            
        # Chart area
        margin = 20
        chart_rect = self.rect().adjusted(margin, margin + 20, -margin, -margin - 30)
        
        # Title
        if self.title:
            painter.setPen(QColor(ThemeManager.COLORS['text-primary']))
            painter.setFont(QFont("Inter", 11, QFont.Bold))
            painter.drawText(self.rect().adjusted(margin, 5, -margin, 0), 
                           Qt.AlignLeft | Qt.AlignTop, self.title)
        
        # Calculate scale
        max_val = max(self.data.values()) if self.data else 1
        
        # Draw bars
        bar_width = chart_rect.width() / len(self.data) * 0.7
        spacing = chart_rect.width() / len(self.data) * 0.3
        
        colors = [
            ThemeManager.COLORS['primary'],
            ThemeManager.COLORS['success'],
            ThemeManager.COLORS['warning'],
            ThemeManager.COLORS['danger'],
            ThemeManager.COLORS['surface-variant']
        ]
        
        for i, (category, value) in enumerate(self.data.items()):
            # Bar position
            x = chart_rect.left() + i * (bar_width + spacing) + spacing/2
            bar_height = (value / max_val) * chart_rect.height()
            y = chart_rect.bottom() - bar_height
            
            # Draw bar
            color = QColor(colors[i % len(colors)])
            painter.fillRect(x, y, bar_width, bar_height, color)
            
            # Value label on top of bar
            painter.setPen(QColor(ThemeManager.COLORS['text-primary']))
            painter.setFont(QFont("Inter", 9, QFont.Bold))
            painter.drawText(x, y - 5, bar_width, 20, Qt.AlignCenter, str(int(value)))
            
            # Category label
            painter.setPen(QColor(ThemeManager.COLORS['text-secondary']))
            painter.setFont(QFont("Inter", 8))
            label_rect = painter.boundingRect(0, 0, 100, 40, Qt.AlignCenter | Qt.TextWordWrap, category)
            painter.drawText(x, chart_rect.bottom() + 5, bar_width, 25, 
                           Qt.AlignCenter | Qt.TextWordWrap, category)

class PieChart(QWidget):
    """Pie chart widget for proportional data"""
    
    def __init__(self, title=""):
        super().__init__()
        self.title = title
        self.data = {}
        self.setMinimumHeight(200)
        self.setMinimumWidth(200)
        
    def set_data(self, data):
        """Set chart data as dict {category: value}"""
        self.data = data
        self.update()
        
    def paintEvent(self, event):
        """Paint the pie chart"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Background
        painter.fillRect(self.rect(), QColor(ThemeManager.COLORS['surface']))
        
        if not self.data:
            # No data message
            painter.setPen(QColor(ThemeManager.COLORS['text-disabled']))
            painter.setFont(QFont("Inter", 10))
            painter.drawText(self.rect(), Qt.AlignCenter, "No data available")
            return
            
        # Title
        if self.title:
            painter.setPen(QColor(ThemeManager.COLORS['text-primary']))
            painter.setFont(QFont("Inter", 11, QFont.Bold))
            painter.drawText(self.rect().adjusted(10, 5, -10, 0), 
                           Qt.AlignCenter | Qt.AlignTop, self.title)
        
        # Calculate center and radius
        center = self.rect().center()
        radius = min(self.width(), self.height()) // 2 - 40
        
        # Calculate total
        total = sum(self.data.values())
        if total == 0:
            return
            
        # Colors
        colors = [
            QColor(ThemeManager.COLORS['success']),
            QColor(ThemeManager.COLORS['warning']),
            QColor(ThemeManager.COLORS['danger']),
            QColor(ThemeManager.COLORS['primary']),
            QColor(ThemeManager.COLORS['surface-variant'])
        ]
        
        # Draw pie slices
        start_angle = 90 * 16  # Start at top
        
        for i, (category, value) in enumerate(self.data.items()):
            # Calculate angle
            angle = int(360 * 16 * value / total)
            
            # Draw slice
            color = colors[i % len(colors)]
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(QColor(ThemeManager.COLORS['background']), 2))
            painter.drawPie(center.x() - radius, center.y() - radius, 
                          radius * 2, radius * 2, start_angle, angle)
            
            # Calculate label position
            label_angle = (start_angle + angle / 2) / 16
            label_radius = radius * 0.7
            label_x = center.x() + label_radius * math.cos(math.radians(label_angle))
            label_y = center.y() - label_radius * math.sin(math.radians(label_angle))
            
            # Draw percentage
            percentage = f"{value/total*100:.1f}%"
            painter.setPen(QPen(Qt.white, 1))
            painter.setFont(QFont("Inter", 9, QFont.Bold))
            painter.drawText(label_x - 20, label_y - 10, 40, 20, 
                           Qt.AlignCenter, percentage)
            
            start_angle += angle
        
        # Draw legend
        legend_y = self.rect().bottom() - 30
        legend_x = 20
        
        painter.setFont(QFont("Inter", 8))
        for i, (category, value) in enumerate(self.data.items()):
            color = colors[i % len(colors)]
            
            # Color box
            painter.fillRect(legend_x, legend_y, 12, 12, color)
            
            # Label
            painter.setPen(QColor(ThemeManager.COLORS['text-secondary']))
            painter.drawText(legend_x + 16, legend_y, 100, 12, 
                           Qt.AlignLeft | Qt.AlignVCenter, category)
            
            legend_x += 120