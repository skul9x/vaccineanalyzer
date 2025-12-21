from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QDateEdit, QLineEdit, QPushButton, QLabel, 
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QFrame,
    QAbstractItemView, QTabWidget, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QDate, Signal, QSize, QDateTime
from PySide6.QtGui import QColor, QBrush, QFont
import qtawesome as qta
from .dialogs.add_patient_dialog import AddPatientDialog
from .dialogs.vaccine_selection_dialog import VaccineSelectionDialog
from .dialogs.patient_search_dialog import PatientSearchDialog

class PatientRegistrationView(QWidget):
    def __init__(self, parent_tab):
        super().__init__()
        self.parent_tab = parent_tab
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # --- Filter Section (Card) ---
        filter_card = QFrame()
        filter_card.setProperty("class", "card")
        
        filter_layout = QHBoxLayout(filter_card)
        filter_layout.setContentsMargins(15, 15, 15, 15)
        filter_layout.setSpacing(12)

        self.entry_from = QDateEdit(QDate.currentDate())
        self.entry_from.setCalendarPopup(True)
        self.entry_from.setFixedWidth(110)
        self.entry_from.setDisplayFormat("dd/MM/yyyy")
        
        self.entry_to = QDateEdit(QDate.currentDate())
        self.entry_to.setCalendarPopup(True)
        self.entry_to.setFixedWidth(110)
        self.entry_to.setDisplayFormat("dd/MM/yyyy")
        
        self.entry_name = QLineEdit()
        self.entry_name.setPlaceholderText("Tên bệnh nhân...")
        self.entry_name.setMinimumWidth(180)
        
        self.entry_phone = QLineEdit()
        self.entry_phone.setPlaceholderText("Số điện thoại...")
        self.entry_phone.setFixedWidth(140)

        btn_search = QPushButton("Tìm kiếm")
        btn_search.setIcon(qta.icon('fa5s.search', color='white'))
        btn_search.setProperty("class", "primary")
        btn_search.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_search.clicked.connect(self.perform_search)

        filter_layout.addWidget(QLabel("Từ ngày:"))
        filter_layout.addWidget(self.entry_from)
        filter_layout.addWidget(QLabel("Đến ngày:"))
        filter_layout.addWidget(self.entry_to)
        filter_layout.addWidget(self.entry_name)
        filter_layout.addWidget(self.entry_phone)
        filter_layout.addWidget(btn_search)
        filter_layout.addStretch()

        layout.addWidget(filter_card)

        # --- Action Toolbar ---
        action_layout = QHBoxLayout()
        action_layout.setSpacing(12)

        btn_add = QPushButton("Thêm Bệnh Nhân")
        btn_add.setIcon(qta.icon('fa5s.user-plus', color='white'))
        btn_add.setProperty("class", "success")
        btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add.clicked.connect(self.parent_tab.open_add_patient_dialog)
        
        btn_del = QPushButton("Xóa Lượt Khám")
        btn_del.setIcon(qta.icon('fa5s.trash-alt', color='#EF4444'))
        btn_del.setFlat(True) # Ghost style for destructive action
        btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_del.setStyleSheet("color: #EF4444; font-weight: 600;")
        btn_del.clicked.connect(self.delete_patient)

        btn_search_patient = QPushButton("Tra cứu (HIS)")
        btn_search_patient.setIcon(qta.icon('fa5s.search-plus', color='white'))
        btn_search_patient.setProperty("class", "primary") # Changed to Primary
        btn_search_patient.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_search_patient.clicked.connect(self.open_search_dialog)

        action_layout.addWidget(btn_add)
        action_layout.addWidget(btn_del)
        action_layout.addStretch()
        action_layout.addWidget(btn_search_patient)

        layout.addLayout(action_layout)

        # --- Table ---
        self.table = QTableWidget()
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False) # Modern style
        
        layout.addWidget(self.table)

    def perform_search(self):
        f_date = f"{self.entry_from.date().toString('yyyy-MM-dd')} 00:00:00"
        t_date = f"{self.entry_to.date().toString('yyyy-MM-dd')} 23:59:59"
        name = self.entry_name.text()
        phone = self.entry_phone.text().strip()
        
        self.setCursor(Qt.WaitCursor)
        results = self.parent_tab.patient_service.search_patients(f_date, t_date, name, phone)
        self.setCursor(Qt.ArrowCursor)
        
        if results is None: return
        
        if not results:
            self.table.setRowCount(0)
            return
            
        cols = list(results[0].keys())
        self.parent_tab.create_dynamic_table(self.table, cols)
        self.table.setRowCount(len(results))
        for row_idx, item in enumerate(results):
            for col_idx, col in enumerate(cols):
                val = item.get(col, "")
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(val)))

    def delete_patient(self):
        row = self.table.currentRow()
        if row == -1: return
        try:
            ma_luotkham = None
            id_benhnhan = None
            for i in range(self.table.columnCount()):
                header = self.table.horizontalHeaderItem(i).text().lower()
                if header == 'ma_luotkham': ma_luotkham = self.table.item(row, i).text()
                if header == 'id_benhnhan': id_benhnhan = self.table.item(row, i).text()
            
            if not ma_luotkham: return
            
            if QMessageBox.question(self, "Xóa", f"Xóa lượt khám {ma_luotkham}?") == QMessageBox.Yes:
                ok, msg = self.parent_tab.patient_service.delete_patient_visit(ma_luotkham, id_benhnhan)
                if ok:
                    self.table.removeRow(row)
                    QMessageBox.information(self, "OK", msg)
                else:
                    QMessageBox.critical(self, "Lỗi", msg)
        except Exception as e:
            self.parent_tab.log_message.emit(f"Delete Error: {e}")

    def open_search_dialog(self):
        dialog = PatientSearchDialog(self.parent_tab.patient_service, self)
        dialog.patient_selected.connect(self.on_patient_found_from_search)
        dialog.exec()

    def on_patient_found_from_search(self, patient_data):
        dialog = AddPatientDialog(self)
        
        name = patient_data.get('ten_benhnhan', '')
        dialog.inp_name.setText(name)
        dialog.normalize_input(dialog.inp_name) 
        
        phone = patient_data.get('dien_thoai', '')
        dialog.inp_phone.setText(phone)
        
        addr = patient_data.get('dia_chi', '')
        dialog.inp_addr.setText(addr)
        dialog.normalize_input(dialog.inp_addr) 
        
        sex_str = patient_data.get('gioi_tinh', '')
        idx = dialog.inp_sex.findText(sex_str, Qt.MatchFixedString)
        if idx >= 0:
            dialog.inp_sex.setCurrentIndex(idx)
            
        dob_str = patient_data.get('ngay_sinh', '')
        if dob_str:
            dt = QDateTime.fromString(dob_str, "dd/MM/yyyy HH:mm")
            if dt.isValid():
                dialog.inp_dob.setDateTime(dt)
        
        if dialog.exec():
            data = dialog.data
            self.setCursor(Qt.WaitCursor)
            ok, msg = self.parent_tab.patient_service.add_patient(
                data['ten'], data['nam_sinh'], data['ngay_sinh_full'],
                data['is_nam'], data['dia_chi'], data['sdt']
            )
            self.setCursor(Qt.ArrowCursor)
            if ok:
                QMessageBox.information(self, "Thành công", msg)
                self.perform_search()
            else:
                QMessageBox.critical(self, "Lỗi", msg)

class VaccinationRoomTab(QWidget):
    request_vncdc_search = Signal(str)
    log_message = Signal(str)

    def __init__(self, patient_service, vaccine_service, parent=None):
        super().__init__(parent)
        self.patient_service = patient_service
        self.vaccine_service = vaccine_service
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(24)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header with Icon
        title_container = QFrame()
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(12)
        
        icon_label = QLabel()
        icon_label.setPixmap(qta.icon('fa5s.clinic-medical', color='#0284C7').pixmap(32, 32))
        
        title = QLabel("Quản Lý Phòng Tiêm & Tiếp Đón")
        title.setProperty("class", "header_title")
        title.setStyleSheet("font-size: 22px;") # Override size slightly larger
        
        title_layout.addWidget(icon_label)
        title_layout.addWidget(title)
        title_layout.addStretch()
        
        layout.addWidget(title_container)

        # Tab Widget
        self.tabs = QTabWidget()
        self.view_registration = PatientRegistrationView(self)
        self.tabs.addTab(self.view_registration, "Danh sách & Đăng ký")
        
        layout.addWidget(self.tabs)

    def create_dynamic_table(self, table_widget, columns):
        table_widget.clear()
        table_widget.setColumnCount(len(columns))
        table_widget.setHorizontalHeaderLabels(columns)
        header = table_widget.horizontalHeader()
        header.setStretchLastSection(True)
        for i, col in enumerate(columns):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)

    def open_add_patient_dialog(self):
        dialog = AddPatientDialog(self)
        if dialog.exec():
            data = dialog.data
            self.setCursor(Qt.WaitCursor)
            ok, msg = self.patient_service.add_patient(
                data['ten'], data['nam_sinh'], data['ngay_sinh_full'],
                data['is_nam'], data['dia_chi'], data['sdt']
            )
            self.setCursor(Qt.ArrowCursor)
            if ok:
                QMessageBox.information(self, "Thành công", msg)
                self.view_registration.perform_search()
            else:
                QMessageBox.critical(self, "Lỗi", msg)