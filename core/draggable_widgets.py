from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QMouseEvent

class DraggableWidget(QWidget):
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.setup_widget(title)
        
    def setup_widget(self, title):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("""
            background: rgba(0, 0, 0, 180);
            border: 2px solid #ff66aa;
            border-radius: 8px;
            padding: 5px;
        """)
        self.drag_start_position = None
        
        if title:
            label = QLabel(title, self)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("color: white; font-weight: bold;")
            label.move(10, 10)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.raise_()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.drag_start_position and event.buttons() & Qt.MouseButton.LeftButton:
            new_pos = event.globalPosition().toPoint() - self.drag_start_position
            if self.parent():
                # Begrenzung auf Eltern-Widget
                new_pos.setX(max(0, min(new_pos.x(), self.parent().width() - self.width())))
                new_pos.setY(max(0, min(new_pos.y(), self.parent().height() - self.height())))
            self.move(new_pos)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self.drag_start_position:
            self.drag_start_position = None
            if hasattr(self.parent(), 'save_widget_positions'):
                self.parent().save_widget_positions()