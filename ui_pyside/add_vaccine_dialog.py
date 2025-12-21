import qtawesome as qta
from datetime import date
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QComboBox, QDateEdit, QPushButton, QMessageBox, QFrame
)
from PySide6.QtCore import Qt, QDate

from live_worker.vaccine_data import get_vaccine_list
from services.data_formatter import DataFormattingService

class AddVaccineDialog(QDialog):
    def __init__(self, parent=None, patient_info=None):
        super().__init__(parent)
        self.setWindowTitle("Thêm Mũi Tiêm (Thủ công)")
        self.resize(450, 300)
        self.selected_vaccine_id = None
        self.full_vaccine_list = []
        self.patient_info = patient_info or {}
        
        self.load_vaccine_data()
        self.setup_ui()

    def load_vaccine_data(self):
        try:
            raw_data = get_vaccine_list()
            filtered_list = [
                v for v in raw_data 
                if v.get("COVID") == 0 and v.get("IS_ACTIVE", 0) == 0
            ]
            filtered_list.sort(key=lambda v: v.get("TEN_VACXIN", "z"))
            
            for v in filtered_list:
                name = v.get("TEN_VACXIN", f"ID_{v['VACXIN_ID']}")
                vac_id = v["VACXIN_ID"]
                self.full_vaccine_list.append((name, vac_id))
        except Exception as e:
            print(f"Error loading vaccine list: {e}")
            self.full_vaccine_list = [("Lỗi tải danh sách", -1)]

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # --- Patient Info Header ---
        if self.patient_info:
            info_frame = QFrame()
            info_frame.setStyleSheet("background-color: #EFF6FF; border-radius: 6px; border: 1px solid #BFDBFE;")
            info_layout = QVBoxLayout(info_frame)
            info_layout.setContentsMargins(15, 10, 15, 10)
            
            name = self.patient_info.get('name', 'Không rõ')
            dob = self.patient_info.get('birth', '')
            
            lbl_name = QLabel(f"Bệnh nhân: {name}")
            lbl_name.setStyleSheet("font-weight: bold; color: #1E3A8A; font-size: 14px;")
            
            lbl_dob = QLabel(f"Ngày sinh: {dob}")
            lbl_dob.setStyleSheet("color: #1E40AF;")
            
            info_layout.addWidget(lbl_name)
            info_layout.addWidget(lbl_dob)
            layout.addWidget(info_frame)

        # 1. Filter
        filter_layout = QHBoxLayout()
        filter_lbl = QLabel("Tìm Vắc-xin:")
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Nhập tên để lọc...")
        self.filter_input.textChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(filter_lbl)
        filter_layout.addWidget(self.filter_input)
        
        # 2. Combobox
        combo_layout = QHBoxLayout()
        combo_lbl = QLabel("Tên Vắc-xin:")
        self.vaccine_combo = QComboBox()
        self.populate_combobox(self.full_vaccine_list)
        combo_layout.addWidget(combo_lbl)
        combo_layout.addWidget(self.vaccine_combo, 1)

        # 3. Date
        date_layout = QHBoxLayout()
        date_lbl = QLabel("Ngày tiêm:")
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat("dd/MM/yyyy")
        date_layout.addWidget(date_lbl)
        date_layout.addWidget(self.date_edit, 1)
        
        # 4. Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.save_btn = QPushButton("Lưu")
        self.save_btn.setIcon(qta.icon('fa5s.save'))
        self.save_btn.setStyleSheet("background-color: #10B981; color: white; font-weight: bold;")
        
        self.cancel_btn = QPushButton("Hủy")
        self.cancel_btn.setIcon(qta.icon('fa5s.times'))
        
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(filter_layout)
        layout.addLayout(combo_layout)
        layout.addLayout(date_layout)
        layout.addStretch()
        layout.addLayout(btn_layout)

    def populate_combobox(self, items):
        self.vaccine_combo.clear()
        self.vaccine_combo.addItem("--- Chọn vắc-xin ---", None)
        for name, vac_id in items:
            self.vaccine_combo.addItem(name, vac_id)

    def on_filter_changed(self, text):
        search_term = text.strip().lower()
        search_norm = DataFormattingService.remove_vietnamese_accents(search_term)
        
        filtered_items = []
        for name, vac_id in self.full_vaccine_list:
            name_norm = DataFormattingService.remove_vietnamese_accents(name.lower())
            if search_norm in name_norm:
                filtered_items.append((name, vac_id))
        
        current_id = self.vaccine_combo.currentData()
        self.populate_combobox(filtered_items)
        
        if current_id is not None:
            idx = self.vaccine_combo.findData(current_id)
            if idx >= 0:
                self.vaccine_combo.setCurrentIndex(idx)

    def get_data(self):
        vac_id = self.vaccine_combo.currentData()
        date_val = self.date_edit.date().toString("dd/MM/yyyy")
        return vac_id, date_val