from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QLabel,
    QMessageBox, QComboBox
)
from PySide6.QtCore import Qt, Signal
import qtawesome as qta
import datetime

class PatientSearchDialog(QDialog):
    # Signal emitting the dictionary of patient data when a row is double-clicked
    patient_selected = Signal(dict)

    def __init__(self, patient_service, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tra cứu bệnh nhân (HIS)")
        self.resize(950, 550)
        self.patient_service = patient_service
        self.search_results = [] # Store results to access data later
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        header_lbl = QLabel("Tra Cứu Lịch Sử Đăng Ký")
        header_lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #3B82F6;")
        layout.addWidget(header_lbl)

        # Search Bar
        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)

        # Combo Box to choose search type
        self.combo_type = QComboBox()
        self.combo_type.addItems(["Tìm theo Số điện thoại", "Tìm theo Họ tên"])
        self.combo_type.setFixedWidth(180)
        self.combo_type.setStyleSheet("""
            QComboBox {
                padding: 8px; border: 1px solid #CBD5E1; border-radius: 6px; background: white;
            }
            QComboBox::drop-down { border: none; }
        """)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Nhập thông tin cần tìm...")
        self.search_input.setStyleSheet("padding: 8px; border: 1px solid #CBD5E1; border-radius: 6px;")
        self.search_input.returnPressed.connect(self.perform_search)
        
        btn_search = QPushButton("Tìm Kiếm")
        btn_search.setIcon(qta.icon('fa5s.search', color='white'))
        btn_search.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6; color: white; font-weight: bold;
                padding: 8px 16px; border-radius: 6px; border: none;
            }
            QPushButton:hover { background-color: #2563EB; }
        """)
        btn_search.clicked.connect(self.perform_search)
        
        search_layout.addWidget(self.combo_type)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(btn_search)
        layout.addLayout(search_layout)

        # Info Label
        lbl_hint = QLabel("💡 Mẹo: Double click vào dòng kết quả để điền thông tin vào form 'Thêm Bệnh Nhân Mới'")
        lbl_hint.setStyleSheet("color: #059669; font-style: italic;")
        layout.addWidget(lbl_hint)

        # Result Table
        self.table = QTableWidget()
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white; border: 1px solid #E2E8F0; border-radius: 8px;
            }
            QHeaderView::section {
                background-color: #F8FAFC; padding: 8px; font-weight: bold; border: none;
                border-bottom: 1px solid #E2E8F0; color: #475569;
            }
            QTableWidget::item:selected {
                background-color: #EFF6FF; color: #1E40AF;
            }
        """)
        # Connect double click signal
        self.table.itemDoubleClicked.connect(self.on_table_double_clicked)
        layout.addWidget(self.table)

    def perform_search(self):
        keyword = self.search_input.text().strip()
        if not keyword:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập từ khóa tìm kiếm!")
            self.search_input.setFocus()
            return

        search_type_idx = self.combo_type.currentIndex() # 0: Phone, 1: Name
        
        phone_val = ""
        name_val = ""

        if search_type_idx == 0: # Phone
            if not keyword.isdigit():
                QMessageBox.warning(self, "Lỗi định dạng", "Số điện thoại chỉ được chứa ký tự số!")
                return
            phone_val = keyword
        else: # Name
            name_val = keyword

        # Use fixed wide date range like C# log: 1990-01-01 -> Today
        from_date = "1990-01-01 00:00:00"
        to_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.setCursor(Qt.WaitCursor)
        # Calling the service with either name or phone based on user selection
        results = self.patient_service.search_patients(from_date, to_date, name=name_val, phone=phone_val)
        self.setCursor(Qt.ArrowCursor)

        if results is None:
            QMessageBox.critical(self, "Lỗi", "Lỗi kết nối cơ sở dữ liệu!")
            return

        self.search_results = results # Save results

        if not results:
            self.table.setRowCount(0)
            QMessageBox.information(self, "Kết quả", "Không tìm thấy bệnh nhân nào phù hợp.")
            return

        display_cols = [
            ("Mã LK", "ma_luotkham"),
            ("Tên Bệnh Nhân", "ten_benhnhan"),
            ("Năm Sinh", "nam_sinh"),
            ("Giới Tính", "gioi_tinh"),
            ("SĐT", "dien_thoai"),
            ("Địa Chỉ", "dia_chi"),
            ("Ngày Tiếp Đón", "ngay_tiepdon")
        ]

        self.table.clear()
        self.table.setColumnCount(len(display_cols))
        self.table.setHorizontalHeaderLabels([title for title, key in display_cols])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.Stretch) # Address stretches

        self.table.setRowCount(len(results))
        for row_idx, item in enumerate(results):
            for col_idx, (title, key) in enumerate(display_cols):
                val = item.get(key, "")
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(val)))

    def on_table_double_clicked(self, item):
        row = item.row()
        if 0 <= row < len(self.search_results):
            patient_data = self.search_results[row]
            self.patient_selected.emit(patient_data)
            self.accept() # Close dialog