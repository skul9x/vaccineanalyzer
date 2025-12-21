from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve

class ToastNotification(QWidget):
    def __init__(self, parent, message, icon_name="fa5s.info-circle", color="#333333", text_color="#ffffff"):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.SubWindow)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        
        self.lbl = QLabel(message)
        self.lbl.setStyleSheet(f"color: {text_color}; font-weight: bold; font-size: 14px;")
        layout.addWidget(self.lbl)
        
        self.setStyleSheet(f"""
            background-color: {color};
            border-radius: 20px;
        """)
        
        self.adjustSize()
        
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        
        self.anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim.setDuration(300)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.fade_out)

    def show_toast(self, duration=3000):
        if not self.parent(): return
        parent_rect = self.parent().rect()
        x = (parent_rect.width() - self.width()) // 2
        y = parent_rect.height() - self.height() - 50
        self.move(x, y)
        
        self.show()
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.start()
        self.timer.start(duration)

    def fade_out(self):
        self.anim.setStartValue(1.0)
        self.anim.setEndValue(0.0)
        self.anim.finished.connect(self.close)
        self.anim.start()

    @staticmethod
    def show_message(parent, message, duration=3000, type="info"):
        color_map = {
            "info": "#333333",
            "success": "#10B981",
            "error": "#EF4444",
            "warning": "#F59E0B"
        }
        bg_color = color_map.get(type, "#333333")
        toast = ToastNotification(parent, message, color=bg_color)
        toast.show_toast(duration)