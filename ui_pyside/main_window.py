from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QFrame, QLabel, QPushButton, QStatusBar, QApplication
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QScreen
import qtawesome as qta

from ui_pyside.sidebar import Sidebar
from ui_pyside.analysis_tab import AnalysisTab
from ui_pyside.config_tab import ConfigTab
from ui_pyside.help_tab import HelpTab
from ui_pyside.debug_tab import DebugTab
from ui_pyside.vaccination_room_tab import VaccinationRoomTab
from ui_pyside.animated_stacked_widget import AnimatedStackedWidget
from version import APP_TITLE

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        
        # Optimize for multiple screen resolutions
        self._setup_responsive_size()
        self.setWindowState(Qt.WindowState.WindowMaximized)
    
    def _setup_responsive_size(self):
        """Setup responsive window size based on screen resolution"""
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            screen_width = screen_geometry.width()
            screen_height = screen_geometry.height()
            
            # Set minimum size based on screen resolution
            if screen_width >= 1920:  # Full HD or higher
                min_width, min_height = 1200, 800
            elif screen_width >= 1366:  # HD
                min_width, min_height = 1024, 700
            else:  # Lower resolutions
                min_width, min_height = 900, 600
            
            self.setMinimumSize(min_width, min_height)
            
            # Set default size to 85% of available screen
            default_width = int(screen_width * 0.85)
            default_height = int(screen_height * 0.85)
            self.resize(default_width, default_height)
        
        container = QWidget()
        self.setCentralWidget(container)
        
        self.main_layout = QHBoxLayout(container)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # 1. Sidebar (Left)
        self.sidebar = Sidebar()
        
        # 2. Main Content Area (Right)
        self.content_area_frame = QFrame()
        self.content_area_frame.setProperty("class", "content_area")
        
        self.content_layout = QVBoxLayout(self.content_area_frame)
        self.content_layout.setSpacing(0)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        
        # 2.1 Top Bar
        self.topbar = QFrame()
        self.topbar.setProperty("class", "topbar")
        self.topbar.setFixedHeight(64)
        
        topbar_layout = QHBoxLayout(self.topbar)
        topbar_layout.setContentsMargins(24, 0, 24, 0)
        
        self.page_title = QLabel("Tổng Quan")
        self.page_title.setProperty("class", "header_title")
        
        self.theme_toggle_btn = QPushButton()
        self.theme_toggle_btn.setIcon(qta.icon('fa5s.adjust', color='#64748B'))
        self.theme_toggle_btn.setFlat(True)
        self.theme_toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.theme_toggle_btn.setToolTip("Đổi giao diện (Sáng/Tối)")
        self.theme_toggle_btn.setFixedSize(40, 40)
        
        self.relogin_btn = QPushButton(" Đăng nhập lại")
        self.relogin_btn.setIcon(qta.icon('fa5s.sign-in-alt', color='#3B82F6'))
        self.relogin_btn.setFlat(True)
        self.relogin_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.relogin_btn.setProperty("class", "ghost")
        self.relogin_btn.setToolTip("Xóa cookies và đăng nhập lại")
        
        topbar_layout.addWidget(self.page_title)
        topbar_layout.addStretch()
        topbar_layout.addWidget(self.theme_toggle_btn)
        topbar_layout.addWidget(self.relogin_btn)
        
        # 2.2 Viewport
        self.stacked_widget = AnimatedStackedWidget()
        
        self.analysis_tab = AnalysisTab()
        self.vaccination_tab = VaccinationRoomTab(None, None)
        self.config_tab = ConfigTab()
        self.help_tab = HelpTab()
        self.debug_tab = DebugTab()
        
        self.stacked_widget.addWidget(self.analysis_tab)
        self.stacked_widget.addWidget(self.vaccination_tab)
        self.stacked_widget.addWidget(self.config_tab)
        self.stacked_widget.addWidget(self.help_tab)
        self.stacked_widget.addWidget(self.debug_tab)
        
        self.content_layout.addWidget(self.topbar)
        self.content_layout.addWidget(self.stacked_widget)
        
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.content_area_frame)
        
        self.sidebar.page_changed.connect(self.on_page_changed)
        
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.hide() 

    def on_page_changed(self, index):
        self.stacked_widget.setCurrentIndex(index)
        titles = ["Phân tích & Dashboard", "Quản Lý Phòng Tiêm (HIS)", "Cấu hình hệ thống", "Hướng dẫn sử dụng", "Debug Log"]
        if 0 <= index < len(titles):
            self.page_title.setText(titles[index])