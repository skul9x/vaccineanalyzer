from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLineEdit, QPushButton, QMessageBox, QComboBox, 
    QDateTimeEdit, QLabel, QFrame
)
from PySide6.QtCore import Qt, QDateTime, QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator
import qtawesome as qta

class AddPatientDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Thêm Bệnh Nhân Mới")
        self.resize(500, 400)
        self.data = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Header
        header_lbl = QLabel("Thông Tin Bệnh Nhân")
        header_lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #3B82F6;")
        layout.addWidget(header_lbl)

        # Form
        form_frame = QFrame()
        form_frame.setStyleSheet("background-color: #f8fafc; border-radius: 8px; border: 1px solid #e2e8f0;")
        form_layout = QFormLayout(form_frame)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.inp_name = QLineEdit()
        self.inp_name.setPlaceholderText("NGUYEN VAN A")
        self.inp_name.setStyleSheet("background-color: white; padding: 8px;")
        # Normalize name on finish
        self.inp_name.editingFinished.connect(lambda: self.normalize_input(self.inp_name))
        
        self.inp_dob = QDateTimeEdit()
        self.inp_dob.setDisplayFormat("dd/MM/yyyy HH:mm")
        self.inp_dob.setCalendarPopup(True)
        self.inp_dob.setDateTime(QDateTime.currentDateTime())
        self.inp_dob.setStyleSheet("background-color: white; padding: 8px;")

        self.inp_sex = QComboBox()
        self.inp_sex.addItems(["Nữ", "Nam"])
        self.inp_sex.setStyleSheet("background-color: white; padding: 8px;")

        self.inp_phone = QLineEdit()
        self.inp_phone.setPlaceholderText("09xxxxxxxx")
        self.inp_phone.setStyleSheet("background-color: white; padding: 8px;")
        
        # Phone validator: allow only digits
        rx = QRegularExpression("[0-9]*")
        validator = QRegularExpressionValidator(rx, self.inp_phone)
        self.inp_phone.setValidator(validator)

        self.inp_addr = QLineEdit()
        self.inp_addr.setPlaceholderText("Thôn/Xóm, Xã/Phường...")
        self.inp_addr.setStyleSheet("background-color: white; padding: 8px;")
        # Normalize address on finish
        self.inp_addr.editingFinished.connect(lambda: self.normalize_input(self.inp_addr))

        self.inp_nation = QLineEdit("Kinh")
        self.inp_nation.setStyleSheet("background-color: white; padding: 8px;")

        form_layout.addRow("Họ và Tên (*):", self.inp_name)
        form_layout.addRow("Ngày sinh:", self.inp_dob)
        form_layout.addRow("Giới tính:", self.inp_sex)
        form_layout.addRow("Điện thoại (*):", self.inp_phone)
        form_layout.addRow("Địa chỉ (*):", self.inp_addr)
        form_layout.addRow("Dân tộc:", self.inp_nation)

        layout.addWidget(form_frame)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        btn_save = QPushButton("Lưu Dữ Liệu")
        btn_save.setIcon(qta.icon('fa5s.save', color='white'))
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #10B981; color: white; font-weight: bold; 
                padding: 10px 20px; border-radius: 6px; border: none;
            }
            QPushButton:hover { background-color: #059669; }
        """)
        btn_save.clicked.connect(self.save_data)
        
        btn_cancel = QPushButton("Hủy Bỏ")
        btn_cancel.setIcon(qta.icon('fa5s.times', color='#475569'))
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #E2E8F0; color: #475569; font-weight: bold; 
                padding: 10px 20px; border-radius: 6px; border: none;
            }
            QPushButton:hover { background-color: #CBD5E1; }
        """)
        btn_cancel.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_cancel)
        
        layout.addLayout(btn_layout)

    def normalize_input(self, line_edit):
        """Standardizes text to Title Case (e.g., 'nguyen van a' -> 'Nguyen Van A')."""
        text = line_edit.text().strip()
        if text:
            # Capitalize first letter of each word
            normalized = " ".join([word.capitalize() for word in text.split()])
            line_edit.setText(normalized)

    def save_data(self):
        # Normalize both fields one last time before saving
        self.normalize_input(self.inp_name)
        self.normalize_input(self.inp_addr)
        
        name = self.inp_name.text().strip()
        phone = self.inp_phone.text().strip()
        addr = self.inp_addr.text().strip()

        if not name:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập Họ và Tên!")
            self.inp_name.setFocus()
            return
            
        if not phone:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập Số điện thoại!")
            self.inp_phone.setFocus()
            return

        if not addr:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập Địa chỉ!")
            self.inp_addr.setFocus()
            return
            
        q_datetime = self.inp_dob.dateTime()
        py_datetime = q_datetime.toPython()
        
        self.data = {
            'ten': name,
            'nam_sinh': py_datetime.year,
            'ngay_sinh_full': py_datetime,
            'is_nam': self.inp_sex.currentText() == "Nam",
            'sdt': phone,
            'dia_chi': addr
        }
        self.accept()