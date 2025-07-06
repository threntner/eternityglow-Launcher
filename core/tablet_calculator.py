from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, 
                            QPushButton, QMessageBox)
from PyQt6.QtGui import (QPainter, QPen, QColor, QKeySequence,
                        QFont, QMouseEvent)
from PyQt6.QtCore import Qt, QTimer
import math

class TabletAreaCalculator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.recording = False
        self.points = []
        self.area_rect = None
        self.tablet_width_mm = 216  # Standard-Wacom Medium Größe
        self.tablet_height_mm = 135
        self.timer = QTimer(self)
        
        # UI Initialisierung
        self.setup_ui()
        self.timer.timeout.connect(self.check_recording)
        
    def setup_ui(self):
        """Initialisiert die Benutzeroberfläche"""
        self.setMinimumSize(800, 500)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("Tablet Area Calculator")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.measure_button = QPushButton("Press space to measure (or click here)")
        self.measure_button.setShortcut(QKeySequence(Qt.Key.Key_Space))
        self.measure_button.clicked.connect(self.toggle_recording)
        
        self.info_label = QLabel("1. Hold space key\n"
                               "2. Move pen over desired area\n"
                               "3. Release space for results")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setFont(QFont("Arial", 12))
        
        layout.addWidget(title)
        layout.addWidget(self.info_label)
        layout.addWidget(self.measure_button)
        layout.addStretch()
        
        self.setStyleSheet("""
            QWidget {
                background: rgba(40, 40, 50, 220);
            }
            QLabel {
                color: white;
                padding: 10px;
            }
            QPushButton {
                background: rgba(255, 102, 170, 180);
                color: white;
                border: none;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 5px;
                min-width: 300px;
            }
            QPushButton:hover {
                background: rgba(255, 120, 180, 220);
            }
        """)

    def toggle_recording(self):
        if self.recording:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):
        self.recording = True
        self.points = []
        self.area_rect = None
        self.measure_button.setText("Measuring... (Release space to stop)")
        self.info_label.setText("Now move your pen over the desired area...")
        self.setMouseTracking(True)
        self.timer.start(100)
        self.update()

    def stop_recording(self):
        if self.recording:
            self.recording = False
            self.setMouseTracking(False)
            self.timer.stop()
            self.measure_button.setText("Press space to measure again")
            if len(self.points) > 10:
                self.calculate_area()
            else:
                self.info_label.setText("Too little data! Please cover a larger area")
            self.update()

    def check_recording(self):
        if self.recording:
            pos = self.mapFromGlobal(self.cursor().pos())
            if self.rect().contains(pos):
                self.points.append(pos)
                self.update()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.recording:
            self.points.append(event.pos())
            self.update()
        super().mouseMoveEvent(event)

    def calculate_area(self):
        if not self.points:
            return
            
        min_x = min(p.x() for p in self.points)
        max_x = max(p.x() for p in self.points)
        min_y = min(p.y() for p in self.points)
        max_y = max(p.y() for p in self.points)
        
        pixel_to_mm_x = self.tablet_width_mm / self.width()
        pixel_to_mm_y = self.tablet_height_mm / self.height()
        
        width_mm = (max_x - min_x) * pixel_to_mm_x
        height_mm = (max_y - min_y) * pixel_to_mm_y
        center_x_mm = (min_x + (max_x - min_x)/2) * pixel_to_mm_x
        center_y_mm = (min_y + (max_y - min_y)/2) * pixel_to_mm_y
        
        self.area_rect = (min_x, min_y, max_x - min_x, max_y - min_y)
        
        result_text = (
            f"<b>Recommended Area Settings:</b><br><br>"
            f"▸ <b>Width:</b> {width_mm:.0f} mm<br>"
            f"▸ <b>Height:</b> {height_mm:.0f} mm<br>"
            f"▸ <b>Center X:</b> {center_x_mm:.0f} mm<br>"
            f"▸ <b>Center Y:</b> {center_y_mm:.0f} mm<br><br>"
            "<i>You can use these values in your tablet driver settings</i>"
        )
        
        self.info_label.setText(result_text)
        self.info_label.setFont(QFont("Arial", 11))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        if len(self.points) > 1:
            pen = QPen(QColor(255, 102, 170), 3)
            painter.setPen(pen)
            for i in range(len(self.points)-1):
                painter.drawLine(self.points[i], self.points[i+1])
        
        if self.area_rect:
            x, y, w, h = self.area_rect
            pen = QPen(QColor(100, 255, 100), 2, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.drawRect(x, y, w, h)
            
            painter.setPen(QColor(255, 255, 255))
            painter.drawText(x + w//2 - 30, y + h + 20, 
                           f"{self.tablet_width_mm * (w/self.width()):.0f}mm × {self.tablet_height_mm * (h/self.height()):.0f}mm")