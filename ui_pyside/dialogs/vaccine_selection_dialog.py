from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QGroupBox, QFormLayout, QSpinBox, QPushButton, 
    QMessageBox, QComboBox, QListWidget, QListWidgetItem, QDateEdit, QMenu
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor, QBrush, QAction
import qtawesome as qta

class VaccineSelectionDialog(QDialog):
    def __init__(self, vaccine_service, parent=None, initial_code=None, initial_days=30, patient_id=None, patient_name=""):
        super().__init__(parent)
        self.setWindowTitle("Đặt Hẹn Tiêm Chủng (HIS)")
        self.resize(550, 480)
        self.vaccine_service = vaccine_service
        
        self.selected_appt_code = None
        self.selected_appt_name = None
        self.selected_days = 0
        self.selected_date = None
        self.appt_types = [] 
        
        self.initial_code = initial_code
        self.initial_days = initial_days
        
        self.patient_id = patient_id
        self.patient_name = patient_name

        self.setup_ui()
        self.load_data()
        self.load_future_appointments()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # --- Future Appointments Warning Section ---
        self.group_future = QGroupBox("Các mũi đã hẹn trong tương lai (Đã có trên hệ thống)")
        self.group_future.setStyleSheet("""
            QGroupBox { 
                font-weight: bold; color: #B45309; font-size: 13px; 
                border: 1px solid #FCD34D; border-radius: 8px; margin-top: 10px;
                background-color: #FFFBEB;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
        """)
        future_layout = QVBoxLayout(self.group_future)
        future_layout.setContentsMargins(10, 15, 10, 10)
        
        self.list_future = QListWidget()
        self.list_future.setFixedHeight(90)
        self.list_future.setStyleSheet("""
            QListWidget { border: none; background-color: transparent; }
            QListWidget::item { color: #92400E; padding: 4px; }
            QListWidget::item:selected { background-color: #FEF3C7; color: #B45309; }
        """)
        self.list_future.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_future.customContextMenuRequested.connect(self.show_context_menu)
        
        lbl_hint = QLabel("💡 Chuột phải để xóa mũi hẹn thừa.")
        lbl_hint.setStyleSheet("font-size: 11px; color: #92400E; font-style: italic;")
        
        future_layout.addWidget(self.list_future)
        future_layout.addWidget(lbl_hint)
        
        self.group_future.setVisible(False)
        layout.addWidget(self.group_future)

        # --- Main Configuration Group ---
        group_config = QGroupBox("Thông tin phiếu hẹn mới")
        group_config.setStyleSheet("""
            QGroupBox { 
                font-weight: bold; color: #1E293B; font-size: 14px; 
                border: 1px solid #CBD5E1; border-radius: 8px; margin-top: 10px;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
        """)
        
        form_layout = QFormLayout()
        form_layout.setContentsMargins(15, 20, 15, 15)
        form_layout.setSpacing(15)
        
        # 1. Combobox
        self.cbo_appt_type = QComboBox()
        self.cbo_appt_type.setEditable(True)
        self.cbo_appt_type.setStyleSheet("padding: 6px;")
        form_layout.addRow("Loại vắc xin / Dịch vụ:", self.cbo_appt_type)

        # 2. Spinbox
        self.inp_days = QSpinBox()
        self.inp_days.setRange(1, 3650)
        self.inp_days.setValue(30)
        self.inp_days.setSuffix(" ngày")
        self.inp_days.setStyleSheet("padding: 6px;")
        self.inp_days.valueChanged.connect(self.on_days_changed)
        form_layout.addRow("Hẹn tái khám sau:", self.inp_days)

        # 3. Date Edit
        self.dt_date_preview = QDateEdit()
        self.dt_date_preview.setCalendarPopup(True)
        self.dt_date_preview.setDisplayFormat("dd/MM/yyyy")
        self.dt_date_preview.setDate(QDate.currentDate().addDays(30))
        self.dt_date_preview.setStyleSheet("padding: 6px; color: #16A34A; font-weight: bold;")
        self.dt_date_preview.dateChanged.connect(self.on_date_changed)
        
        form_layout.addRow("Ngày hẹn dự kiến:", self.dt_date_preview)

        group_config.setLayout(form_layout)
        layout.addWidget(group_config)

        # Buttons
        btn_layout = QHBoxLayout()
        
        btn_save = QPushButton("XÁC NHẬN ĐẶT HẸN")
        btn_save.setIcon(qta.icon('fa5s.check-circle', color='white'))
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #8B5CF6; color: white; font-weight: bold; 
                padding: 10px 20px; border-radius: 6px; border: none; font-size: 13px;
            }
            QPushButton:hover { background-color: #7C3AED; }
        """)
        btn_save.clicked.connect(self.accept_selection)
        
        btn_cancel = QPushButton("Hủy Bỏ")
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #E2E8F0; color: #475569; 
                padding: 10px 20px; border-radius: 6px; border: none;
            }
            QPushButton:hover { background-color: #CBD5E1; }
        """)
        btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

    def load_data(self):
        self.cbo_appt_type.clear()
        self.cbo_appt_type.addItem("--- Chọn loại hẹn ---", None)
        
        self.appt_types = self.vaccine_service.get_vaccine_appointment_types()
        for item in self.appt_types:
            self.cbo_appt_type.addItem(f"{item['name']}", item['code'])
            
        if self.initial_code:
            index = self.cbo_appt_type.findData(self.initial_code)
            if index >= 0:
                self.cbo_appt_type.setCurrentIndex(index)
        
        if self.initial_days:
            self.inp_days.setValue(self.initial_days)
            # Sync date edit will happen automatically via signal or we can force it
            self.on_days_changed()

    def load_future_appointments(self):
        if not self.patient_id:
            return

        future_apps = self.vaccine_service.get_future_appointments(self.patient_id)
        
        if future_apps:
            self.group_future.setVisible(True)
            self.list_future.clear()
            for app in future_apps:
                item_text = f"• {app['name']} - Hẹn ngày: {app['date']}"
                item = QListWidgetItem(item_text)
                # Store data needed for deletion
                item.setData(Qt.UserRole, {
                    'header_id': app.get('header_id'), 
                    'mui_thu': app.get('mui_thu'),
                    'name': app['name']
                })
                self.list_future.addItem(item)
        else:
            self.group_future.setVisible(False)

    def show_context_menu(self, pos):
        item = self.list_future.itemAt(pos)
        if not item: return
        
        menu = QMenu(self)
        delete_action = QAction("Xóa lịch hẹn này", self)
        delete_action.triggered.connect(lambda: self.delete_appointment_item(item))
        menu.addAction(delete_action)
        menu.exec(self.list_future.mapToGlobal(pos))

    def delete_appointment_item(self, item):
        data = item.data(Qt.UserRole)
        if not data: return
        
        res = QMessageBox.question(self, "Xác nhận xóa", f"Bạn có chắc muốn xóa lịch hẹn '{data['name']}' không?", QMessageBox.Yes | QMessageBox.No)
        if res == QMessageBox.Yes:
            ok, msg = self.vaccine_service.delete_appointment(data['header_id'], data['mui_thu'])
            if ok:
                row = self.list_future.row(item)
                self.list_future.takeItem(row)
                if self.list_future.count() == 0:
                    self.group_future.setVisible(False)
            else:
                QMessageBox.critical(self, "Lỗi", msg)

    def on_days_changed(self):
        self.inp_days.blockSignals(True)
        self.dt_date_preview.blockSignals(True)
        
        days = self.inp_days.value()
        new_date = QDate.currentDate().addDays(days)
        self.dt_date_preview.setDate(new_date)
        
        self.inp_days.blockSignals(False)
        self.dt_date_preview.blockSignals(False)

    def on_date_changed(self):
        self.inp_days.blockSignals(True)
        self.dt_date_preview.blockSignals(True)
        
        selected_date = self.dt_date_preview.date()
        days = QDate.currentDate().daysTo(selected_date)
        if days < 1: days = 1 # Minimum 1 day
        self.inp_days.setValue(days)
        
        self.inp_days.blockSignals(False)
        self.dt_date_preview.blockSignals(False)

    def accept_selection(self):
        code = self.cbo_appt_type.currentData()
        if not code:
            QMessageBox.warning(self, "Chưa chọn", "Vui lòng chọn Loại vắc xin / Dịch vụ!")
            self.cbo_appt_type.setFocus()
            return
        
        self.selected_appt_code = code
        self.selected_appt_name = self.cbo_appt_type.currentText()
        self.selected_days = self.inp_days.value()
        self.selected_date = self.dt_date_preview.date().toPython()
        
        self.accept()