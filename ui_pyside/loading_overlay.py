from PySide6.QtWidgets import QWidget, QVBoxLayout, QProgressBar, QLabel
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QColor, QPalette

class LoadingOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Update attribute usage for PySide6
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, False)
        
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(0, 0, 0, 120))
        self.setPalette(palette)
        self.setAutoFillBackground(True)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.progress = QProgressBar()
        self.progress.setFixedWidth(200)
        self.progress.setRange(0, 0)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet("""
            QProgressBar {
                background-color: #444;
                border-radius: 4px;
                height: 6px;
            }
            QProgressBar::chunk {
                background-color: #007AFF;
                border-radius: 4px;
            }
        """)
        
        self.label = QLabel("Đang xử lý...")
        self.label.setStyleSheet("color: white; font-weight: bold; font-size: 14px; margin-top: 10px;")
        
        layout.addWidget(self.progress)
        layout.addWidget(self.label)
        
        self.hide()
        if parent:
            parent.installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj == self.parent() and event.type() == QEvent.Type.Resize:
            self.resize(obj.size())
        return super().eventFilter(obj, event)

    def show_loading(self, show=True, message="Đang xử lý..."):
        if show:
            self.label.setText(message)
            self.resize(self.parent().size())
            self.show()
            self.raise_()
        else:
            self.hide()