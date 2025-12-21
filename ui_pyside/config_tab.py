import qtawesome as qta
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QFormLayout, 
    QLineEdit, QPushButton, QLabel, QComboBox, QHBoxLayout, QFrame
)
from PySide6.QtCore import Qt

class ConfigTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(24)
        layout.setContentsMargins(40, 40, 40, 40)
        
        header = QLabel("Cấu Hình Hệ Thống")
        header.setProperty("class", "header_title")
        layout.addWidget(header)

        # --- System Data ---
        data_frame = QFrame()
        data_frame.setProperty("class", "card")
        data_layout = QVBoxLayout(data_frame)
        data_layout.setContentsMargins(20, 20, 20, 20)
        
        lbl_data = QLabel("Dữ liệu Vắc-xin")
        lbl_data.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        self.update_vaccine_btn = QPushButton("Cập nhật Dữ liệu Online")
        self.update_vaccine_btn.setIcon(qta.icon('fa5s.cloud-download-alt'))
        self.update_vaccine_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update_vaccine_btn.setFixedWidth(250)
        
        data_layout.addWidget(lbl_data)
        data_layout.addWidget(self.update_vaccine_btn)

        # --- Account ---
        acc_frame = QFrame()
        acc_frame.setProperty("class", "card")
        acc_layout = QVBoxLayout(acc_frame)
        acc_layout.setContentsMargins(20, 20, 20, 20)
        
        lbl_acc = QLabel("Tài khoản Cổng Tiêm Chủng")
        lbl_acc.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Tên đăng nhập")
        self.username_input.setFixedHeight(36)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Mật khẩu")
        self.password_input.setFixedHeight(36)
        
        form_layout.addRow("Tên đăng nhập:", self.username_input)
        form_layout.addRow("Mật khẩu:", self.password_input)
        
        acc_layout.addWidget(lbl_acc)
        acc_layout.addLayout(form_layout)
        
        # --- Theme ---
        theme_frame = QFrame()
        theme_frame.setProperty("class", "card")
        theme_layout = QHBoxLayout(theme_frame)
        theme_layout.setContentsMargins(20, 20, 20, 20)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark", "Ocean"])
        self.theme_combo.setFixedWidth(150)
        
        theme_layout.addWidget(QLabel("Giao diện ứng dụng:"))
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()

        # --- Save ---
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Lưu Cài Đặt")
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.setFixedSize(160, 45)
        self.save_btn.setIcon(qta.icon('fa5s.save', color='white'))
        self.save_btn.setProperty("class", "primary")
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.save_btn)
        
        layout.addWidget(data_frame)
        layout.addWidget(acc_frame)
        layout.addWidget(theme_frame)
        layout.addLayout(btn_layout)
        layout.addStretch()