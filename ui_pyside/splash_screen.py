"""
Splash Screen for VaccineAnalyzer
A beautiful, animated splash screen with modern design
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QGraphicsOpacityEffect, QApplication
)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, Property, QPoint
from PySide6.QtGui import QFont, QPainter, QLinearGradient, QColor, QPen, QBrush, QPainterPath
from version import APP_VERSION

class SplashScreen(QWidget):
    """
    Modern animated splash screen with:
    - Gradient background
    - Pulsing logo animation
    - Smooth progress bar
    - Fade-in/out effects
    """
    
    VERSION = APP_VERSION  # Use centralized version
    
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.SplashScreen)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(520, 380)
        
        # Center on screen
        screen = QApplication.primaryScreen()
        if screen:
            screen_geo = screen.availableGeometry()
            x = (screen_geo.width() - self.width()) // 2
            y = (screen_geo.height() - self.height()) // 2
            self.move(x, y)
        
        # Animation properties
        self._pulse_scale = 1.0
        self._progress_value = 0
        
        self.setup_ui()
        self.setup_animations()
    
    def get_pulse_scale(self):
        return self._pulse_scale
    
    def set_pulse_scale(self, value):
        self._pulse_scale = value
        self.update()
    
    pulse_scale = Property(float, get_pulse_scale, set_pulse_scale)
    
    def setup_ui(self):
        """Setup the splash screen UI"""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 50, 40, 40)
        layout.setSpacing(15)
        
        # Spacer for logo area (we draw it in paintEvent)
        layout.addSpacing(120)
        
        # App Title
        self.title_label = QLabel("VaccineAnalyzer")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        self.title_label.setStyleSheet("color: white; background: transparent;")
        layout.addWidget(self.title_label)
        
        # Subtitle
        self.subtitle_label = QLabel("Clinical Dashboard")
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label.setFont(QFont("Segoe UI", 12))
        self.subtitle_label.setStyleSheet("color: rgba(255, 255, 255, 0.7); background: transparent;")
        layout.addWidget(self.subtitle_label)
        
        layout.addSpacing(20)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: rgba(255, 255, 255, 0.2);
                border: none;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #60A5FA, stop:0.5 #A78BFA, stop:1 #F472B6);
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Đang khởi động...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFont(QFont("Segoe UI", 10))
        self.status_label.setStyleSheet("color: rgba(255, 255, 255, 0.6); background: transparent;")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        # Version & Copyright
        version_layout = QHBoxLayout()
        
        self.version_label = QLabel(f"Version {self.VERSION}")
        self.version_label.setFont(QFont("Segoe UI", 9))
        self.version_label.setStyleSheet("color: rgba(255, 255, 255, 0.5); background: transparent;")
        
        self.copyright_label = QLabel("© 2025 Nguyễn Duy Trường")
        self.copyright_label.setFont(QFont("Segoe UI", 9))
        self.copyright_label.setStyleSheet("color: rgba(255, 255, 255, 0.5); background: transparent;")
        
        version_layout.addWidget(self.version_label)
        version_layout.addStretch()
        version_layout.addWidget(self.copyright_label)
        
        layout.addLayout(version_layout)
    
    def setup_animations(self):
        """Setup pulse animation for the logo"""
        # Pulse animation
        self.pulse_anim = QPropertyAnimation(self, b"pulse_scale")
        self.pulse_anim.setDuration(1500)
        self.pulse_anim.setStartValue(0.95)
        self.pulse_anim.setEndValue(1.05)
        self.pulse_anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        self.pulse_anim.setLoopCount(-1)  # Infinite loop
        
        # Progress animation timer
        self.progress_timer = QTimer(self)
        self.progress_timer.timeout.connect(self._update_progress)
        
    def start_animation(self):
        """Start all animations"""
        self.pulse_anim.start()
        self.progress_timer.start(30)
    
    def stop_animation(self):
        """Stop all animations"""
        self.pulse_anim.stop()
        self.progress_timer.stop()
    
    def _update_progress(self):
        """Smoothly update progress bar"""
        if self._progress_value < self.progress_bar.value():
            return
        
        current = self.progress_bar.value()
        target = self._progress_value
        
        if current < target:
            # Smooth increment
            step = max(1, (target - current) // 5)
            self.progress_bar.setValue(min(current + step, target))
    
    def set_progress(self, value, status_text=None):
        """Set progress value and optionally update status text"""
        self._progress_value = value
        if status_text:
            self.status_label.setText(status_text)
    
    def paintEvent(self, event):
        """Custom paint for gradient background and logo"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw rounded rectangle background with gradient
        rect = self.rect()
        path = QPainterPath()
        path.addRoundedRect(rect.x(), rect.y(), rect.width(), rect.height(), 20, 20)
        
        # Beautiful gradient background (Dark Purple to Blue)
        gradient = QLinearGradient(0, 0, rect.width(), rect.height())
        gradient.setColorAt(0, QColor("#1E1B4B"))      # Deep indigo
        gradient.setColorAt(0.3, QColor("#312E81"))    # Indigo
        gradient.setColorAt(0.7, QColor("#1E3A5F"))    # Dark blue
        gradient.setColorAt(1, QColor("#0F172A"))      # Slate
        
        painter.fillPath(path, QBrush(gradient))
        
        # Draw subtle border
        painter.setPen(QPen(QColor(255, 255, 255, 30), 1))
        painter.drawPath(path)
        
        # Draw animated logo (syringe/vaccine icon)
        self._draw_logo(painter)
        
        painter.end()
    
    def _draw_logo(self, painter):
        """Draw an animated vaccine/medical icon"""
        center_x = self.width() // 2
        center_y = 85
        
        # Apply pulse scale
        painter.save()
        painter.translate(center_x, center_y)
        painter.scale(self._pulse_scale, self._pulse_scale)
        painter.translate(-center_x, -center_y)
        
        # Outer glow circle
        glow_gradient = QLinearGradient(center_x - 45, center_y - 45, center_x + 45, center_y + 45)
        glow_gradient.setColorAt(0, QColor("#60A5FA"))  # Blue
        glow_gradient.setColorAt(0.5, QColor("#A78BFA"))  # Purple
        glow_gradient.setColorAt(1, QColor("#F472B6"))  # Pink
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(glow_gradient))
        painter.drawEllipse(center_x - 45, center_y - 45, 90, 90)
        
        # Inner circle (darker)
        painter.setBrush(QBrush(QColor("#1E1B4B")))
        painter.drawEllipse(center_x - 38, center_y - 38, 76, 76)
        
        # Draw shield/medical cross icon
        painter.setPen(QPen(QColor("#60A5FA"), 3))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        # Shield outline
        shield_path = QPainterPath()
        shield_path.moveTo(center_x, center_y - 28)
        shield_path.lineTo(center_x + 22, center_y - 18)
        shield_path.lineTo(center_x + 22, center_y + 5)
        shield_path.quadTo(center_x + 22, center_y + 25, center_x, center_y + 32)
        shield_path.quadTo(center_x - 22, center_y + 25, center_x - 22, center_y + 5)
        shield_path.lineTo(center_x - 22, center_y - 18)
        shield_path.closeSubpath()
        
        # Fill shield with gradient
        shield_gradient = QLinearGradient(center_x, center_y - 28, center_x, center_y + 32)
        shield_gradient.setColorAt(0, QColor(96, 165, 250, 120))
        shield_gradient.setColorAt(1, QColor(167, 139, 250, 80))
        painter.setBrush(QBrush(shield_gradient))
        painter.drawPath(shield_path)
        
        # Medical cross inside shield
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor("#FFFFFF")))
        
        # Vertical bar
        painter.drawRoundedRect(center_x - 4, center_y - 15, 8, 26, 2, 2)
        # Horizontal bar
        painter.drawRoundedRect(center_x - 11, center_y - 5, 22, 8, 2, 2)
        
        painter.restore()


class SplashScreenManager:
    """Manager class to handle splash screen lifecycle"""
    
    def __init__(self, main_window_class, controller_class):
        self.main_window_class = main_window_class
        self.controller_class = controller_class
        self.splash = None
        self.main_window = None
        self.controller = None
    
    def start(self):
        """Show splash and start loading"""
        self.splash = SplashScreen()
        self.splash.show()
        self.splash.start_animation()
        
        # Simulate loading stages
        QTimer.singleShot(100, lambda: self._load_stage(1))
    
    def _load_stage(self, stage):
        """Handle different loading stages"""
        if stage == 1:
            self.splash.set_progress(20, "Đang tải giao diện...")
            QTimer.singleShot(300, lambda: self._load_stage(2))
        
        elif stage == 2:
            self.splash.set_progress(40, "Đang khởi tạo components...")
            # Actually create main window
            self.main_window = self.main_window_class()
            QTimer.singleShot(200, lambda: self._load_stage(3))
        
        elif stage == 3:
            self.splash.set_progress(60, "Đang kết nối services...")
            # Create controller
            self.controller = self.controller_class(self.main_window)
            QTimer.singleShot(300, lambda: self._load_stage(4))
        
        elif stage == 4:
            self.splash.set_progress(80, "Đang hoàn tất...")
            QTimer.singleShot(200, lambda: self._load_stage(5))
        
        elif stage == 5:
            self.splash.set_progress(100, "Sẵn sàng!")
            QTimer.singleShot(400, self._finish)
    
    def _finish(self):
        """Finish loading and show main window"""
        self.splash.stop_animation()
        self.splash.close()
        self.main_window.show()
