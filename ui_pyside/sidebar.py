from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QButtonGroup, QFrame, QLabel, QHBoxLayout
)
from PySide6.QtCore import Signal, QSize, Qt, QPropertyAnimation, QEasingCurve
import qtawesome as qta
from version import VERSION_STRING

class Sidebar(QFrame):
    page_changed = Signal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # Identify this widget for CSS styling
        self.setObjectName("SidebarContainer") 
        self.is_collapsed = True 
        self.expanded_width = 240
        self.collapsed_width = 64
        self.setup_ui()

    def setup_ui(self):
        self.setFixedWidth(self.collapsed_width if self.is_collapsed else self.expanded_width)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header Area
        self.header_frame = QFrame()
        self.header_frame.setFixedHeight(64) # Match TopBar height
        
        self.header_layout = QHBoxLayout(self.header_frame)
        self.header_layout.setContentsMargins(0, 0, 0, 0)
        self.header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.logo_icon = QLabel()
        self.logo_icon.setPixmap(qta.icon('fa5s.syringe', color='#2563EB').pixmap(24, 24))
        self.logo_icon.setVisible(not self.is_collapsed)
        
        self.app_title = QLabel("Vaccine Analyzer")
        self.app_title.setStyleSheet("font-weight: 800; font-size: 16px; color: #2563EB;")
        self.app_title.setVisible(not self.is_collapsed)
        
        self.toggle_btn = QPushButton()
        self.toggle_btn.setIcon(qta.icon('fa5s.bars', color='#64748B'))
        self.toggle_btn.setFixedSize(40, 40)
        self.toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_btn.setProperty("class", "ghost")
        self.toggle_btn.clicked.connect(self.toggle_sidebar)

        if not self.is_collapsed:
            self.header_layout.addWidget(self.logo_icon)
            self.header_layout.addWidget(self.app_title)
            self.header_layout.addStretch()
        self.header_layout.addWidget(self.toggle_btn)
        
        layout.addWidget(self.header_frame)

        # Navigation Buttons
        self.btn_group = QButtonGroup(self)
        self.btn_group.setExclusive(True)
        self.btn_group.idClicked.connect(self.page_changed.emit)

        self.buttons_layout = QVBoxLayout()
        self.buttons_layout.setSpacing(2)
        self.buttons_layout.setContentsMargins(0, 16, 0, 16)
        
        self.nav_btns = []
        self.add_button(0, "Tổng quan", "fa5s.chart-pie")
        self.add_button(1, "Phòng tiêm", "fa5s.clinic-medical")
        self.add_button(2, "Cấu hình", "fa5s.cog")
        self.add_button(3, "Hướng dẫn", "fa5s.book")
        self.add_button(4, "Debug Log", "fa5s.bug")

        layout.addLayout(self.buttons_layout)
        layout.addStretch()
        
        # Footer / Version
        self.footer_frame = QFrame()
        self.footer_layout = QVBoxLayout(self.footer_frame)
        self.footer_layout.setContentsMargins(0, 16, 0, 16)
        self.footer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.version_lbl = QLabel(VERSION_STRING)
        self.version_lbl.setStyleSheet("color: #94A3B8; font-size: 11px; font-weight: 600;")
        self.version_lbl.setVisible(not self.is_collapsed)
        
        self.footer_layout.addWidget(self.version_lbl)
        layout.addWidget(self.footer_frame)

    def add_button(self, id, text, icon_name):
        btn_text = "" if self.is_collapsed else f"  {text}"
        
        btn = QPushButton(btn_text)
        btn.setCheckable(True)
        # Note: Icon color is static here, but CSS handles the text/border. 
        # Ideally icons would be re-generated on theme change, but that's expensive.
        btn.setIcon(qta.icon(icon_name, color="#64748B"))
        btn.setIconSize(QSize(18, 18))
        btn.setProperty("class", "sidebar_btn")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFixedHeight(44) # Consistent height
        
        if self.is_collapsed:
            btn.setToolTip(text)
        
        if id == 0:
            btn.setChecked(True)

        self.buttons_layout.addWidget(btn)
        self.btn_group.addButton(btn, id)
        self.nav_btns.append((btn, text))

    def toggle_sidebar(self):
        target_width = self.collapsed_width if not self.is_collapsed else self.expanded_width
        self.is_collapsed = not self.is_collapsed
        
        self.anim = QPropertyAnimation(self, b"minimumWidth")
        self.anim.setDuration(250)
        self.anim.setStartValue(self.width())
        self.anim.setEndValue(target_width)
        self.anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.anim.start()
        
        self.logo_icon.setVisible(not self.is_collapsed)
        self.app_title.setVisible(not self.is_collapsed)
        self.version_lbl.setVisible(not self.is_collapsed)
        
        # Rebuild header layout to center hamburger or show full logo
        while self.header_layout.count():
            item = self.header_layout.takeAt(0)
            if item.widget(): item.widget().setParent(None)
            
        if not self.is_collapsed:
            self.header_layout.setContentsMargins(16, 0, 16, 0)
            self.header_layout.addWidget(self.logo_icon)
            self.header_layout.addWidget(self.app_title)
            self.header_layout.addStretch()
            self.header_layout.addWidget(self.toggle_btn)
        else:
            self.header_layout.setContentsMargins(0, 0, 0, 0)
            self.header_layout.addWidget(self.toggle_btn)
        
        for btn, text in self.nav_btns:
            if self.is_collapsed:
                btn.setText("")
                btn.setToolTip(text)
            else:
                btn.setText(f"  {text}")
                btn.setToolTip("")
        
        self.setFixedWidth(target_width)