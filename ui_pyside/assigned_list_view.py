import csv
import re
import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, 
    QDateEdit, QLineEdit, QPushButton, QApplication,
    QLabel, QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView, 
    QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt, QDate, Signal, QUrl, QStandardPaths
from PySide6.QtGui import QDesktopServices
import qtawesome as qta

try:
    import xlsxwriter
    HAS_XLSXWRITER = True
except ImportError:
    HAS_XLSXWRITER = False

class AssignedListView(QWidget):
    request_vncdc_search = Signal(str)
    log_message = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.patient_service = None
        self.current_data = []
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)

        # --- Controls Bar ---
        ctrl_layout = QHBoxLayout()
        ctrl_layout.setSpacing(10)
        ctrl_layout.setContentsMargins(0, 0, 0, 0)
        
        # Date Range
        self.date_from = QDateEdit(QDate.currentDate())
        self.date_from.setCalendarPopup(True)
        self.date_from.setDisplayFormat("dd/MM")
        self.date_from.setFixedWidth(80)
        
        lbl_sep = QLabel("-")
        lbl_sep.setStyleSheet("color: #94A3B8; font-weight: bold;")
        
        self.date_to = QDateEdit(QDate.currentDate())
        self.date_to.setCalendarPopup(True)
        self.date_to.setDisplayFormat("dd/MM")
        self.date_to.setFixedWidth(80)
        
        # Refresh
        btn_refresh = QPushButton()
        btn_refresh.setIcon(qta.icon('fa5s.sync-alt', color='#4F46E5'))
        btn_refresh.setFixedSize(36, 34)
        btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_refresh.clicked.connect(self.load_data)
        
        # Search
        self.search_name = QLineEdit()
        self.search_name.setPlaceholderText("Tìm...")
        self.search_name.setFixedHeight(34)
        self.search_name.returnPressed.connect(self.load_data)
        
        # Export
        self.btn_export = QPushButton()
        self.btn_export.setIcon(qta.icon('fa5s.file-excel', color='#10B981'))
        self.btn_export.setFixedSize(36, 34)
        self.btn_export.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_export.clicked.connect(self.handle_export_excel)
        
        ctrl_layout.addWidget(self.date_from)
        ctrl_layout.addWidget(lbl_sep)
        ctrl_layout.addWidget(self.date_to)
        ctrl_layout.addWidget(btn_refresh)
        ctrl_layout.addWidget(self.search_name)
        ctrl_layout.addWidget(self.btn_export)

        layout.addLayout(ctrl_layout)

        # --- Modern Data Table ---
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setSortingEnabled(True)
        self.table.setWordWrap(False)
        
        self.table.itemDoubleClicked.connect(self.on_item_double_clicked)
        
        layout.addWidget(self.table)

    def set_service(self, service):
        self.patient_service = service

    def load_data(self):
        if self.patient_service is None:
            return

        f_date = f"{self.date_from.date().toString('yyyy-MM-dd')} 00:00:00"
        t_date = f"{self.date_to.date().toString('yyyy-MM-dd')} 23:59:59"
        name = self.search_name.text().strip()
        
        status_val = -1
        
        self.setCursor(Qt.WaitCursor)
        self.table.setSortingEnabled(False)
        
        data = self.patient_service.get_vaccination_queue(f_date, t_date, name, status=status_val)
        
        if data is None: 
            self.setCursor(Qt.ArrowCursor)
            self.table.setSortingEnabled(True)
            return
        
        self.current_data = data 
        
        try:
            data.sort(key=lambda x: int(x.get('stt_kham', 0) or 0))
        except: pass
        
        self.display_data(data)
        
        self.table.setSortingEnabled(True)
        self.setCursor(Qt.ArrowCursor)

    def display_data(self, data):
        self.table.clear()
        if not data:
            self.table.setRowCount(0)
            self.table.setColumnCount(0)
            return

        # --- FIX: Condensed Layout for HIS ---
        # Removed Age & Phone to prioritize Name & Indication visibility.
        # STT: Fixed 40px
        # Name: ResizeToContents (or 130px min)
        # Indication: Stretch (Remaining space)
        columns_config = [
            ("STT", "stt_kham", 0, 40),
            ("Họ và Tên", "ten_benhnhan", 1, 0),
            ("Chỉ định (Vắc-xin)", "chi_dinh", 2, 0),
            ("SĐT", "dien_thoai", 0, 0),   # Hidden, kept for data retrieval
            ("ID", "id_benhnhan", 0, 0),   # Hidden
            ("MA", "ma_luotkham", 0, 0)    # Hidden
        ]
        
        self.table.setColumnCount(len(columns_config))
        self.table.setHorizontalHeaderLabels([c[0] for c in columns_config])
        
        header = self.table.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        for i, (title, key, w_type, w_val) in enumerate(columns_config):
            if w_type == 0: # Fixed
                if w_val == 0: self.table.setColumnHidden(i, True)
                else: 
                    header.setSectionResizeMode(i, QHeaderView.Fixed)
                    self.table.setColumnWidth(i, w_val)
            elif w_type == 1: # ResizeToContents
                header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
            elif w_type == 2: # Stretch
                header.setSectionResizeMode(i, QHeaderView.Stretch)

        self.table.setRowCount(len(data))
        
        for row_idx, item in enumerate(data):
            if row_idx > 0 and row_idx % 20 == 0:
                QApplication.processEvents()

            ma_luotkham = item.get('ma_luotkham')
            id_benhnhan = item.get('id_benhnhan')
            
            vaccines = []
            if ma_luotkham and id_benhnhan and self.patient_service:
                try:
                    vaccines = self.patient_service.get_assigned_vaccines(ma_luotkham, id_benhnhan)
                except: pass
            
            vaccine_str = "; ".join(vaccines) if vaccines else ""
            item['chi_dinh'] = vaccine_str

            for col_idx, (title, key, _, _) in enumerate(columns_config):
                val = item.get(key, "")
                
                table_item = QTableWidgetItem(str(val))
                
                if key == "stt_kham":
                    table_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                
                if key == "chi_dinh" and val:
                    table_item.setForeground(Qt.GlobalColor.darkBlue)
                    table_item.setToolTip(str(val))

                self.table.setItem(row_idx, col_idx, table_item)

    def on_item_double_clicked(self, item):
        row = item.row()
        # Phone is now at index 3 (Hidden)
        phone_number = None
        try:
            item_phone = self.table.item(row, 3) 
            if item_phone:
                phone_number = item_phone.text().strip()
        except AttributeError: pass
        
        if not phone_number:
            QMessageBox.warning(self, "Thiếu thông tin", "Bệnh nhân này không có số điện thoại để tra cứu.")
            return

        self.request_vncdc_search.emit(phone_number)

    def handle_copy_and_execute(self):
        self.on_item_double_clicked(self.table.currentItem())

    def _simplify_address(self, addr):
        if not addr: return ""
        part1 = addr.split(',')[0].strip()
        prefixes = ["Xã ", "Phường ", "Thị Trấn ", "Thị trấn ", "TT "]
        for p in prefixes:
            if part1.lower().startswith(p.lower()):
                return part1[len(p):].strip()
        return part1

    def _clean_vaccine_name(self, name):
        if not name: return ""
        name_lower = name.lower()
        if "vaccin tả uống" in name_lower: return "Morcvax"
        if "influvac" in name_lower: return "Influvac"
        if "gene - hbvax" in name_lower: return "Gene - HBvax"
        if "varivax" in name_lower: return "Varivax"
        if "synflorix" in name_lower: return "Synflorix"
        if "mengoc" in name_lower: return "Mengoc BC"
        if "vat" in name_lower: return "VAT"
        if "rotavin" in name_lower: return "Rotavin"
        if "rotarix" in name_lower: return "Rotarix"
        if "hexaxim" in name_lower: return "Hexaxim"
        cleaned = re.sub(r'\s*\(.*?\)', '', name)
        cleaned = re.sub(r'\s*(?:0[.,]5|1)\s*ml', '', cleaned, flags=re.IGNORECASE)
        return cleaned.strip().rstrip("-").strip()

    def handle_export_excel(self):
        if not self.current_data:
            QMessageBox.warning(self, "Thông báo", "Không có dữ liệu để xuất!")
            return

        if not HAS_XLSXWRITER:
            QMessageBox.critical(self, "Thiếu thư viện", 
                "Chức năng này cần thư viện 'xlsxwriter'.\nVui lòng cài đặt bằng lệnh: pip install XlsxWriter")
            return

        d_from = self.date_from.date().toString('ddMMyyyy')
        d_to = self.date_to.date().toString('ddMMyyyy')
        filename_str = f"DS_Tiem_{d_from}.xlsx" if d_from == d_to else f"DS_Tiem_{d_from}_{d_to}.xlsx"

        desktop_path = QStandardPaths.writableLocation(QStandardPaths.DesktopLocation)
        default_name = os.path.join(desktop_path, filename_str)
        
        file_path, _ = QFileDialog.getSaveFileName(self, "Lưu file Excel", default_name, "Excel Files (*.xlsx)")
        
        if not file_path:
            return

        try:
            workbook = xlsxwriter.Workbook(file_path)
            worksheet = workbook.add_worksheet("DanhSachTiem")
            font_props = {'font_name': 'Times New Roman', 'font_size': 16}
            header_fmt = workbook.add_format({**font_props, 'bold': True, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'bg_color': '#D9E1F2'})
            cell_props = {**font_props, 'border': 1, 'valign': 'vcenter', 'text_wrap': True}
            fmt_center = workbook.add_format({**cell_props, 'align': 'center'})
            fmt_left = workbook.add_format({**cell_props, 'align': 'left'})
            
            headers = ["Ngày", "STT", "Họ và tên", "Ngày sinh", "Địa chỉ", "SĐT", "Vắc xin"]
            for col, text in enumerate(headers):
                worksheet.write(0, col, text, header_fmt)

            row = 1
            col_widths = [len(h) for h in headers]
            last_written_date = None
            export_stt = 1

            for item in self.current_data:
                vaccine_str = item.get('chi_dinh', '')
                if not vaccine_str: continue
                vaccines = [v.strip() for v in vaccine_str.split(';') if v.strip()]
                if not vaccines: continue

                date_val = item.get('ngay_tiepdon', '')
                date_str = str(date_val).split(' ')[0].replace('/', '.') if date_val else ""
                
                date_cell_val = ""
                if date_str != last_written_date:
                    date_cell_val = date_str
                    last_written_date = date_str
                
                stt = str(export_stt)
                name = item.get('ten_benhnhan', '')
                dob_val = item.get('ngay_sinh', '') or str(item.get('nam_sinh', ''))
                dob_val = str(dob_val).split(' ')[0].replace('/', '.')
                addr_final = self._simplify_address(item.get('dia_chi', '')).title()
                phone = item.get('dien_thoai', '')
                vac1_final = self._clean_vaccine_name(vaccines[0])

                row_data = [date_cell_val, stt, name, dob_val, addr_final, phone, vac1_final]
                for col, val in enumerate(row_data):
                    val_str = str(val)
                    fmt = fmt_left if col == 2 else fmt_center
                    worksheet.write(row, col, val_str, fmt)
                    if len(val_str) > col_widths[col]: col_widths[col] = len(val_str)
                row += 1

                if len(vaccines) > 1:
                    for vac in vaccines[1:]:
                        vac_final = self._clean_vaccine_name(vac)
                        for col in range(6):
                            fmt = fmt_left if col == 2 else fmt_center
                            worksheet.write(row, col, "", fmt)
                        worksheet.write(row, 6, vac_final, fmt_center)
                        if len(vac_final) > col_widths[6]: col_widths[6] = len(vac_final)
                        row += 1
                export_stt += 1

            for i, width in enumerate(col_widths):
                worksheet.set_column(i, i, width * 1.5 + 2)

            workbook.close()
            QMessageBox.information(self, "Thành công", f"Đã xuất dữ liệu thành công!\n{file_path}")
            QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể xuất file: {e}")