import os
from datetime import date, timedelta
from PySide6.QtCore import Slot, Qt, QUrl
from PySide6.QtWidgets import QListWidgetItem, QTableWidgetItem, QMessageBox
from PySide6.QtGui import QColor, QBrush, QDesktopServices, QFont
import qtawesome as qta

from ui_pyside.toast import ToastNotification
from ui_pyside.add_vaccine_dialog import AddVaccineDialog
from .base_controller import BaseController

class AnalysisController(BaseController):
    def __init__(self, main_controller):
        super().__init__(main_controller)

    def setup_connections(self):
        # Note: view_history_btn and add_vaccine_btn were removed from UI
        # Double-click on search results triggers handle_view_history
        # Push icon on search results triggers handle_add_vaccine_click
        self.view.analysis_tab.export_vaccinated_btn.clicked.connect(self.handle_export_vaccinated)
        self.view.analysis_tab.delete_vaccinated_img_btn.clicked.connect(self.handle_delete_vaccinated)
        self.view.analysis_tab.export_missing_btn.clicked.connect(self.handle_export_missing)
        self.view.analysis_tab.delete_missing_img_btn.clicked.connect(self.handle_delete_missing)
        self.view.analysis_tab.admin_search.textChanged.connect(self.on_admin_search_changed)
        self.view.analysis_tab.missing_search.textChanged.connect(self.on_missing_search_changed)
        
        self.services['worker'].signals.vaccines_loaded.connect(self.on_vaccines_loaded)
        self.services['worker'].signals.add_vaccine_failed.connect(self.on_add_vaccine_failed)

    @Slot(QListWidgetItem)
    def handle_list_double_click(self, item):
        self.handle_view_history()

    @Slot()
    def handle_view_history(self):
        if not self.state['current_patient_id']:
            ToastNotification.show_message(self.view, "Chưa chọn đối tượng.", type="warning")
            return
        self.view.analysis_tab.set_loading(True, "Đang tải dữ liệu tiêm chủng...")
        self.state['last_failed_task'] = {"type": "get_vaccines", "payload": {"doi_tuong_id": self.state['current_patient_id']}}
        self.services['worker'].request_history(self.state['current_patient_id'])

    @Slot(list)
    def on_vaccines_loaded(self, vaccine_list):
        self.view.analysis_tab.set_loading(False)
        # Note: view_history_btn was removed from UI
        
        if self.state['current_patient_info']:
            result = self.services['analysis'].analyze(self.state['current_patient_info'], vaccine_list)
            self.state['analysis_results'] = result
            if result.get("error"):
                ToastNotification.show_message(self.view, result["error"], type="error")
            else:
                self.update_ui_with_results(result)
                ToastNotification.show_message(self.view, "Đã phân tích dữ liệu.", type="success")

    def update_ui_with_results(self, data):
        admin_list = data.get("administered", [])
        missing_list = data.get("missing", [])
        
        # Profile status update removed - profile panel was eliminated

        # --- Update Administered Table (History) ---
        self.view.analysis_tab.admin_table.setSortingEnabled(False) # Optimize reload
        self.view.analysis_tab.admin_table.setRowCount(len(admin_list))
        
        brush_secondary = QBrush(QColor("#334155")) # Slate 700 for text
        brush_dim = QBrush(QColor("#64748B"))       # Slate 500 for date/dose
        
        for row, item in enumerate(admin_list):
            name_item = QTableWidgetItem(str(item['name']))
            name_item.setData(Qt.ItemDataRole.UserRole, item)
            name_item.setForeground(brush_secondary)
            name_item.setIcon(qta.icon('fa5s.check-circle', color='#10B981')) # Green Check
            
            dose_item = QTableWidgetItem(str(item['dose']))
            dose_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            dose_item.setForeground(brush_dim)
            
            date_item = QTableWidgetItem(str(item['date']))
            date_item.setForeground(brush_dim)
            date_item.setIcon(qta.icon('fa5s.calendar-alt', color='#94A3B8'))
            
            self.view.analysis_tab.admin_table.setItem(row, 0, name_item)
            self.view.analysis_tab.admin_table.setItem(row, 1, dose_item)
            self.view.analysis_tab.admin_table.setItem(row, 2, date_item)
        
        self.view.analysis_tab.admin_table.setSortingEnabled(True)

        # --- Update Missing Table (Action Plan) ---
        self.view.analysis_tab.missing_table.setSortingEnabled(False)
        self.view.analysis_tab.missing_table.setRowCount(len(missing_list))
        
        bold_font = QFont()
        bold_font.setBold(True)
        
        for row, item in enumerate(missing_list):
            desc_text = str(item['description'])
            date_str = str(item['date_str'])
            tags = item.get("status_tags", [])
            color_group = self.services['data'].get_status_tags_for_missing_item(tags)
            
            # Detailed Semantic Mapping
            if "due" in tags:
                # Urgent/Due -> Bold Blue
                color_code = "#0284C7" # Sky 600
                icon_name = "fa5s.syringe"
                is_bold = True
            elif "warning" == color_group:
                # Warning -> Amber
                color_code = "#D97706" # Amber 600
                icon_name = "fa5s.exclamation-triangle"
                is_bold = False
            elif any(t.startswith("error") for t in tags):
                # Error -> Red
                color_code = "#DC2626" # Red 600
                icon_name = "fa5s.times-circle"
                is_bold = False
            else:
                # Info/Future -> Slate
                color_code = "#475569" # Slate 600
                icon_name = "fa5s.clock"
                is_bold = False
            
            desc_item = QTableWidgetItem(desc_text)
            desc_item.setIcon(qta.icon(icon_name, color=color_code))
            desc_item.setForeground(QBrush(QColor(color_code)))
            if is_bold: desc_item.setFont(bold_font)
            
            date_item = QTableWidgetItem(date_str)
            date_item.setForeground(QBrush(QColor(color_code)))
            if is_bold: date_item.setFont(bold_font)
            
            desc_item.setToolTip(desc_text)
            
            desc_item.setData(Qt.ItemDataRole.UserRole, item)
            self.view.analysis_tab.missing_table.setItem(row, 0, desc_item)
            self.view.analysis_tab.missing_table.setItem(row, 1, date_item)
            
        self.view.analysis_tab.missing_table.setSortingEnabled(True)
            
        self.view.analysis_tab.admin_search.clear()
        self.view.analysis_tab.missing_search.clear()

    @Slot()
    def handle_add_vaccine_click(self):
        if not self.state['current_patient_id']:
            ToastNotification.show_message(self.view, "Chưa chọn đối tượng.", type="warning")
            return
        
        dialog = AddVaccineDialog(self.view, patient_info=self.state['current_patient_info'])
        if dialog.exec():
            vac_id, date_val = dialog.get_data()
            if not vac_id: return
            self.view.analysis_tab.set_loading(True, "Đang thêm mũi tiêm...")
            payload = {"DOI_TUONG_ID": self.state['current_patient_id'], "VACXIN_ID": vac_id, "NGAY_TIEM": date_val}
            self.state['last_failed_task'] = {"type": "add_vaccine", "payload": payload}
            self.services['worker'].request_add_vaccine(self.state['current_patient_id'], vac_id, date_val)

    @Slot(str)
    def on_add_vaccine_failed(self, message):
        self.view.analysis_tab.set_loading(False)
        ToastNotification.show_message(self.view, f"Lỗi thêm mũi tiêm: {message}", type="error")

    @Slot(str)
    def on_admin_search_changed(self, text):
        term = self.services['data'].remove_vietnamese_accents(text.strip().lower())
        table = self.view.analysis_tab.admin_table
        for i in range(table.rowCount()):
            item = table.item(i, 0)
            should_show = True
            if item:
                cell_text = self.services['data'].remove_vietnamese_accents(item.text().lower())
                if term and term not in cell_text:
                    should_show = False
            table.setRowHidden(i, not should_show)

    @Slot(str)
    def on_missing_search_changed(self, text):
        self.refresh_missing_table_visibility()

    def refresh_missing_table_visibility(self):
        search_term = self.services['data'].remove_vietnamese_accents(self.view.analysis_tab.missing_search.text().strip().lower())
        table = self.view.analysis_tab.missing_table
        
        for i in range(table.rowCount()):
            item = table.item(i, 0)
            if not item: continue
            
            visible_by_search = True
            if search_term:
                cell_text = self.services['data'].remove_vietnamese_accents(item.text().lower())
                if search_term not in cell_text:
                    visible_by_search = False
            
            table.setRowHidden(i, not visible_by_search)

    @Slot()
    def handle_export_vaccinated(self):
        if not self.state['analysis_results'] or not self.state['analysis_results'].get("administered"):
            ToastNotification.show_message(self.view, "Không có dữ liệu đã tiêm để xuất.", type="warning")
            return
            
        items_to_export = []
        table = self.view.analysis_tab.admin_table
        for r in range(table.rowCount()):
            if not table.isRowHidden(r):
                item = table.item(r, 0)
                if item:
                    data = item.data(Qt.ItemDataRole.UserRole)
                    if data: items_to_export.append(data)
        
        if not items_to_export:
             ToastNotification.show_message(self.view, "Danh sách trống.", type="warning")
             return
             
        try:
            path = self.services['image'].generate_image(items_to_export, self.state['analysis_results'], is_missing_list=False)
            self.show_export_success(path)
        except Exception as e:
            ToastNotification.show_message(self.view, str(e), type="error")

    @Slot()
    def handle_delete_vaccinated(self):
        count, error = self.services['image'].delete_images(is_missing_list=False)
        if error: ToastNotification.show_message(self.view, error, type="error")
        elif count == 0: ToastNotification.show_message(self.view, "Thư mục 'Vaccinated' trống.", type="info")
        else: ToastNotification.show_message(self.view, f"Đã xóa {count} ảnh đã tiêm.", type="success")

    @Slot()
    def handle_export_missing(self):
        if not self.state['analysis_results'] or not self.state['analysis_results'].get("missing"):
            ToastNotification.show_message(self.view, "Không có dữ liệu để xuất.", type="warning")
            return
            
        items_to_export = []
        selected_rows = self.view.analysis_tab.missing_table.selectionModel().selectedRows()
        
        if selected_rows:
            for index in selected_rows:
                item_data = self.view.analysis_tab.missing_table.item(index.row(), 0).data(Qt.ItemDataRole.UserRole)
                if item_data: items_to_export.append(item_data)
        else:
            for r in range(self.view.analysis_tab.missing_table.rowCount()):
                if not self.view.analysis_tab.missing_table.isRowHidden(r):
                    item_data = self.view.analysis_tab.missing_table.item(r, 0).data(Qt.ItemDataRole.UserRole)
                    if item_data: items_to_export.append(item_data)
        
        if not items_to_export:
             ToastNotification.show_message(self.view, "Không có dữ liệu phù hợp.", type="warning")
             return
        try:
            prepared_data = self.services['data'].prepare_missing_data_for_export(items_to_export)
            path = self.services['image'].generate_image(prepared_data, self.state['analysis_results'], is_missing_list=True)
            self.show_export_success(path)
        except Exception as e:
            ToastNotification.show_message(self.view, str(e), type="error")
    
    @Slot()
    def handle_delete_missing(self):
        count, error = self.services['image'].delete_images(is_missing_list=True)
        if error: ToastNotification.show_message(self.view, error, type="error")
        elif count == 0: ToastNotification.show_message(self.view, "Thư mục 'Output' trống.", type="info")
        else: ToastNotification.show_message(self.view, f"Đã xóa {count} ảnh cần tiêm.", type="success")

    def show_export_success(self, path):
        ToastNotification.show_message(self.view, "Xuất ảnh thành công!", type="success")
        msg = QMessageBox(self.view)
        msg.setWindowTitle("Xuất Ảnh Thành Công")
        msg.setText(f"Đã lưu ảnh tại:\n{path}")
        msg.addButton("OK", QMessageBox.AcceptRole)
        open_btn = msg.addButton("Mở Ảnh", QMessageBox.ActionRole)
        open_folder_btn = msg.addButton("Mở Thư Mục", QMessageBox.ActionRole)
        msg.exec()
        
        if msg.clickedButton() == open_btn:
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))
        elif msg.clickedButton() == open_folder_btn:
            folder_path = os.path.dirname(path)
            QDesktopServices.openUrl(QUrl.fromLocalFile(folder_path))