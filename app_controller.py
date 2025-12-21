import os
import atexit
import requests
import json
import threading
from datetime import datetime, date, timedelta
from PySide6.QtCore import QObject, Slot, Qt, QUrl, Signal
from PySide6.QtWidgets import QListWidgetItem, QTableWidgetItem, QApplication, QMessageBox
from PySide6.QtGui import QColor, QBrush, QDesktopServices, QShortcut, QKeySequence

import qtawesome as qta

from services.image_exporter import ImageExportService
from services.data_formatter import DataFormattingService
from services.config_service import ConfigService
from services.worker_service import WorkerService
from services.analysis_service import AnalysisService
from services.patient_service import PatientService
from services.vaccine_service import VaccineService
from ui_pyside.add_vaccine_dialog import AddVaccineDialog
from ui_pyside.toast import ToastNotification
from ui_pyside.styles import AppTheme
from ui_pyside.dialogs.vaccine_selection_dialog import VaccineSelectionDialog
from ui_pyside.dialogs.add_patient_dialog import AddPatientDialog
from live_worker.vaccine_data import get_base_path

class AppController(QObject):
    vaccine_update_success = Signal(int)
    vaccine_update_error = Signal(str)

    def __init__(self, main_window):
        super().__init__()
        self.view = main_window
        
        self.current_patient_id = None
        self.current_patient_info = {}
        self.matched_his_visit = None
        
        self.last_failed_task = None
        self.search_results_map = {}
        self.analysis_results = None 
        self.current_theme = "Dark"

        self.init_services()
        self.setup_connections()
        self.setup_vaccination_tab()
        self.load_initial_data()
        
        # Initial state for Schedule button
        self.view.analysis_tab.schedule_btn.setEnabled(False)
        self.view.analysis_tab.schedule_btn.setText("Đặt Hẹn (F10) - Chưa khớp HIS")
        self.view.analysis_tab.schedule_btn.setStyleSheet("background-color: #64748B; color: white; border: none;")
        
        self.worker_service.start_worker()
        atexit.register(self.cleanup)

    def cleanup(self):
        self.worker_service.stop_worker()

    def init_services(self):
        self.data_service = DataFormattingService()
        self.image_service = ImageExportService()
        self.config_service = ConfigService()
        self.worker_service = WorkerService()
        self.analysis_service = AnalysisService()
        
        self.db_patient_service = PatientService(logger_callback=self.on_worker_log)
        self.db_vaccine_service = VaccineService(logger_callback=self.on_worker_log)

    def setup_vaccination_tab(self):
        self.view.vaccination_tab.patient_service = self.db_patient_service
        self.view.vaccination_tab.vaccine_service = self.db_vaccine_service
        self.view.vaccination_tab.request_vncdc_search.connect(self.handle_vncdc_search_request)
        self.view.vaccination_tab.log_message.connect(self.on_worker_log)

    def setup_connections(self):
        self.view.analysis_tab.search_btn.clicked.connect(self.handle_search_click)
        self.view.analysis_tab.phone_input.returnPressed.connect(self.handle_search_click)
        # Removed view_history_btn and add_vaccine_btn connections - buttons removed from UI
        # Double-click now triggers analysis directly
        self.view.analysis_tab.result_list.currentRowChanged.connect(self.handle_patient_selected)
        
        self.view.analysis_tab.result_list.itemDoubleClicked.connect(self.handle_list_double_click)
        
        self.view.analysis_tab.export_vaccinated_btn.clicked.connect(self.handle_export_vaccinated)
        self.view.analysis_tab.delete_vaccinated_img_btn.clicked.connect(self.handle_delete_vaccinated)
        
        self.view.analysis_tab.schedule_btn.clicked.connect(self.handle_schedule_appointment)
        self.view.analysis_tab.export_missing_btn.clicked.connect(self.handle_export_missing)
        self.view.analysis_tab.delete_missing_img_btn.clicked.connect(self.handle_delete_missing)
        
        # Connect Double Click on Missing Table
        self.view.analysis_tab.missing_table.itemDoubleClicked.connect(self.handle_missing_item_double_click)
        
        self.view.analysis_tab.missing_table.itemSelectionChanged.connect(self.on_missing_selection_changed)
        self.view.analysis_tab.admin_search.textChanged.connect(self.on_admin_search_changed)
        self.view.analysis_tab.missing_search.textChanged.connect(self.on_missing_search_changed)

        self.view.config_tab.save_btn.clicked.connect(self.handle_save_config)
        self.view.config_tab.update_vaccine_btn.clicked.connect(self.handle_update_vaccine_list)
        self.view.debug_tab.generate_btn.clicked.connect(self.handle_generate_debug)
        
        self.view.theme_toggle_btn.clicked.connect(self.handle_theme_toggle)
        self.view.relogin_btn.clicked.connect(self.handle_force_relogin)
        
        self.worker_service.signals.log_received.connect(self.on_worker_log)
        self.worker_service.signals.worker_ready.connect(self.on_worker_ready)
        self.worker_service.signals.login_finished.connect(self.on_login_finished)
        self.worker_service.signals.search_finished.connect(self.on_search_finished)
        self.worker_service.signals.vaccines_loaded.connect(self.on_vaccines_loaded)
        self.worker_service.signals.session_expired.connect(self.on_session_expired)
        self.worker_service.signals.add_vaccine_failed.connect(self.on_add_vaccine_failed)
        self.worker_service.signals.relogin_finished.connect(self.on_relogin_finished)

        self.vaccine_update_success.connect(self.on_vaccine_update_success)
        self.vaccine_update_error.connect(self.on_vaccine_update_error)

        self.f10_shortcut = QShortcut(QKeySequence("F10"), self.view)
        self.f10_shortcut.activated.connect(self.handle_schedule_appointment)

    def load_initial_data(self):
        creds = self.config_service.load_config()
        self.view.config_tab.username_input.setText(creds.get("username", ""))
        self.view.config_tab.password_input.setText(creds.get("password", ""))
        
        self.current_theme = creds.get("theme", "Dark")
        idx = self.view.config_tab.theme_combo.findText(self.current_theme)
        if idx >= 0: self.view.config_tab.theme_combo.setCurrentIndex(idx)
        
        self.apply_app_theme(self.current_theme)
        self.update_theme_icon()

    def apply_app_theme(self, theme_name):
        app = QApplication.instance()
        app.setStyleSheet(AppTheme.get_stylesheet(theme_name))
        self.view.help_tab.render_help(theme_name)

    def update_theme_icon(self):
        icon_name = 'fa5s.sun' if self.current_theme == "Dark" else 'fa5s.moon'
        self.view.theme_toggle_btn.setIcon(qta.icon(icon_name, color='#64748B'))

    @Slot()
    def handle_theme_toggle(self):
        if self.current_theme == "Dark":
            new_theme = "Light"
        else:
            new_theme = "Dark"
        
        self.current_theme = new_theme
        idx = self.view.config_tab.theme_combo.findText(new_theme)
        if idx >= 0: self.view.config_tab.theme_combo.setCurrentIndex(idx)
        
        self.apply_app_theme(new_theme)
        self.update_theme_icon()
        self.handle_save_config(silent=True)

    @Slot(str)
    def on_worker_log(self, message):
        self.view.debug_tab.log_viewer.appendPlainText(f"[SYSTEM] {message}")

    @Slot()
    def on_worker_ready(self):
        self.view.analysis_tab.set_loading(True, "Đang đăng nhập hệ thống...")
        self.perform_login(is_retry=False)

    @Slot(bool, str)
    def on_login_finished(self, success, message):
        self.view.analysis_tab.set_loading(False)
        if success:
            ToastNotification.show_message(self.view, "Đăng nhập thành công!", type="success")
            if self.last_failed_task:
                self.view.analysis_tab.set_loading(True, "Thử lại tác vụ...")
                task_type = self.last_failed_task.get("type")
                payload = self.last_failed_task.get("payload")
                if task_type == "search_phone": self.worker_service.request_search(payload["phone"])
                elif task_type == "get_vaccines": self.worker_service.request_history(payload["doi_tuong_id"])
                elif task_type == "add_vaccine": self.worker_service.request_add_vaccine(payload["DOI_TUONG_ID"], payload["VACXIN_ID"], payload["NGAY_TIEM"])
                self.last_failed_task = None
        else:
            ToastNotification.show_message(self.view, f"Đăng nhập thất bại: {message}", type="error")
            self.view.stacked_widget.setCurrentIndex(2)

    @Slot(bool, str)
    def on_relogin_finished(self, success, message):
        self.view.analysis_tab.set_loading(False)
        if success:
            ToastNotification.show_message(self.view, "Đã đăng nhập lại thành công!", type="success")
            if self.last_failed_task:
                self.view.analysis_tab.set_loading(True, "Thử lại tác vụ...")
                task_type = self.last_failed_task.get("type")
                payload = self.last_failed_task.get("payload")
                if task_type == "search_phone": self.worker_service.request_search(payload["phone"])
                elif task_type == "get_vaccines": self.worker_service.request_history(payload["doi_tuong_id"])
                elif task_type == "add_vaccine": self.worker_service.request_add_vaccine(payload["DOI_TUONG_ID"], payload["VACXIN_ID"], payload["NGAY_TIEM"])
                self.last_failed_task = None
        else:
            ToastNotification.show_message(self.view, f"Đăng nhập lại thất bại: {message}", type="error")
            self.view.stacked_widget.setCurrentIndex(2) 

    @Slot(list)
    def on_search_finished(self, results):
        self.view.analysis_tab.set_loading(False)
        self.view.analysis_tab.result_list.clear()
        self.search_results_map.clear()
        
        if not results:
            ToastNotification.show_message(self.view, "Không tìm thấy SĐT này.", type="warning")
            return
            
        for idx, subject in enumerate(results):
            display_text = f"{subject['name']} - NS: {subject['birth']}"
            item = QListWidgetItem(display_text)
            item.setIcon(qta.icon('fa5s.user'))
            self.view.analysis_tab.result_list.addItem(item)
            self.search_results_map[idx] = subject
        
        if len(results) == 1:
            self.view.analysis_tab.result_list.setCurrentRow(0)

    @Slot(list)
    def on_vaccines_loaded(self, vaccine_list):
        self.view.analysis_tab.set_loading(False)
        # Note: view_history_btn was removed from UI
        
        if self.current_patient_info:
            result = self.analysis_service.analyze(self.current_patient_info, vaccine_list)
            self.analysis_results = result
            if result.get("error"):
                ToastNotification.show_message(self.view, result["error"], type="error")
            else:
                self.update_ui_with_results(result)
                ToastNotification.show_message(self.view, "Đã phân tích dữ liệu.", type="success")

    @Slot()
    def on_session_expired(self):
        self.view.analysis_tab.set_loading(True, "Phiên hết hạn, đang đăng nhập lại...")
        self.perform_login(is_retry=True)

    @Slot(str)
    def on_add_vaccine_failed(self, message):
        self.view.analysis_tab.set_loading(False)
        ToastNotification.show_message(self.view, f"Lỗi thêm mũi tiêm: {message}", type="error")

    def perform_login(self, is_retry=False):
        creds = self.config_service.load_config()
        user = creds.get("username")
        pwd = creds.get("password")
        if not user or not pwd:
            self.view.analysis_tab.set_loading(False)
            if not is_retry: ToastNotification.show_message(self.view, "Thiếu thông tin đăng nhập", type="warning")
            return
        
        if not is_retry: 
            self.last_failed_task = None
            self.worker_service.request_login(user, pwd)
        else:
            self.worker_service.request_relogin(user, pwd)

    def _calculate_age_display(self, dob_str):
        try:
            dob = datetime.strptime(dob_str.strip(), "%d/%m/%Y").date()
            today = date.today()
            age_years = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            age_months = (today.year - dob.year) * 12 + today.month - dob.month
            if today.day < dob.day: age_months -= 1
            age_days = (today - dob).days
            if age_years >= 6: return f"{age_years} tuổi"
            elif age_months >= 1: return f"{age_months} tháng tuổi"
            else: return f"{age_days} ngày tuổi"
        except Exception: return ""

    def update_ui_with_results(self, data):
        admin_list = data.get("administered", [])
        missing_list = data.get("missing", [])
        
        total_administered = len(admin_list)
        total_missing = 0
        total_upcoming = 0
        
        today = date.today()
        seven_days_later = today + timedelta(days=7)

        for item in missing_list:
            tags = item.get("status_tags", [])
            status = self.data_service.get_status_tags_for_missing_item(tags)
            if "due" in tags or status == "warning":
                total_missing += 1
            
            raw_date = item.get("raw_date")
            if raw_date and today <= raw_date <= seven_days_later:
                total_upcoming += 1
        
        # Profile status update removed - profile panel was eliminated

        self.view.analysis_tab.admin_table.setRowCount(len(admin_list))
        for row, item in enumerate(admin_list):
            name_item = QTableWidgetItem(str(item['name']))
            
            name_item.setData(Qt.ItemDataRole.UserRole, item)
            
            self.view.analysis_tab.admin_table.setItem(row, 0, name_item)
            self.view.analysis_tab.admin_table.setItem(row, 1, QTableWidgetItem(str(item['dose'])))
            self.view.analysis_tab.admin_table.setItem(row, 2, QTableWidgetItem(str(item['date'])))

        self.view.analysis_tab.missing_table.setRowCount(len(missing_list))
        for row, item in enumerate(missing_list):
            desc_item = QTableWidgetItem(str(item['description']))
            date_item = QTableWidgetItem(str(item['date_str']))
            tags = item.get("status_tags", [])
            color_group = self.data_service.get_status_tags_for_missing_item(tags)
            
            color_map = {
                "due": ("#3B82F6", "fa5s.clock"),
                "warning": ("#EF4444", "fa5s.exclamation-circle"),
                "info": ("#10B981", "fa5s.info-circle"),
                "normal": ("#64748B", "fa5s.circle")
            }
            color_code, icon_name = color_map.get(color_group, color_map["normal"])
            
            desc_item.setIcon(qta.icon(icon_name, color=color_code))
            desc_item.setForeground(QBrush(QColor(color_code)))
            date_item.setForeground(QBrush(QColor(color_code)))
            
            desc_item.setData(Qt.ItemDataRole.UserRole, item)
            self.view.analysis_tab.missing_table.setItem(row, 0, desc_item)
            self.view.analysis_tab.missing_table.setItem(row, 1, date_item)
            
        self.view.analysis_tab.admin_search.clear()
        self.view.analysis_tab.missing_search.clear()

    @Slot()
    def handle_search_click(self):
        phone = self.view.analysis_tab.phone_input.text().strip()
        if not phone or not phone.isdigit() or len(phone) < 10:
            self.view.analysis_tab.set_phone_error(True)
            ToastNotification.show_message(self.view, "Số điện thoại không hợp lệ.", type="warning")
            return
        
        self.view.analysis_tab.set_loading(True, f"Đang tìm kiếm SĐT: {phone}...")
        self.last_failed_task = {"type": "search_phone", "payload": {"phone": phone}}
        self.worker_service.request_search(phone)

    @Slot(int)
    def handle_patient_selected(self, row_index):
        if row_index < 0: return
        subject = self.search_results_map.get(row_index)
        if subject:
            self.current_patient_id = subject['id']
            self.current_patient_info = subject
            
            # Profile panel removed - no longer updating UI elements here
            
            self.check_his_patient_match()

    def check_his_patient_match(self):
        self.matched_his_visit = None
        
        self.view.analysis_tab.schedule_btn.setEnabled(False)
        self.view.analysis_tab.schedule_btn.setText("Đặt Hẹn (F10) - Đang kiểm tra...")
        self.view.analysis_tab.schedule_btn.setStyleSheet("background-color: #64748B; color: white; border: none;")

        phone = self.view.analysis_tab.phone_input.text().strip()
        vncdc_name = self.current_patient_info.get('name', '').strip()
        vncdc_dob_str = self.current_patient_info.get('birth', '').strip()
        
        if not phone or not vncdc_name:
            self.view.analysis_tab.schedule_btn.setText("Đặt Hẹn (F10) - Thiếu thông tin")
            return

        today = datetime.now().strftime("%Y-%m-%d")
        f_date = f"{today} 00:00:00"
        t_date = f"{today} 23:59:59"
        
        try:
            his_results = self.db_patient_service.search_patients(f_date, t_date, "", phone)
            
            if his_results:
                vncdc_name_norm = self.data_service.remove_vietnamese_accents(vncdc_name.lower())
                
                for visit in his_results:
                    his_name = visit.get('ten_benhnhan', '')
                    his_dob_raw = visit.get('ngay_sinh', '')
                    
                    his_name_norm = self.data_service.remove_vietnamese_accents(his_name.lower())
                    
                    if vncdc_name_norm != his_name_norm:
                        continue 
                    
                    dob_match = False
                    try:
                        vncdc_dob_obj = datetime.strptime(vncdc_dob_str, "%d/%m/%Y").date()
                    except:
                        vncdc_dob_obj = None
                    
                    his_dob_obj = None
                    if isinstance(his_dob_raw, datetime) or isinstance(his_dob_raw, date):
                        his_dob_obj = his_dob_raw.date() if isinstance(his_dob_raw, datetime) else his_dob_raw
                    elif isinstance(his_dob_raw, str):
                        try:
                            if "/" in his_dob_raw:
                                his_dob_obj = datetime.strptime(his_dob_raw.split(" ")[0], "%d/%m/%Y").date()
                            elif "-" in his_dob_raw:
                                his_dob_obj = datetime.strptime(his_dob_raw.split(" ")[0], "%Y-%m-%d").date()
                        except: pass
                    
                    if vncdc_dob_obj and his_dob_obj and vncdc_dob_obj == his_dob_obj:
                        dob_match = True
                    
                    if dob_match:
                        self.matched_his_visit = visit
                        break
            
            if self.matched_his_visit:
                self.view.analysis_tab.schedule_btn.setEnabled(True)
                self.view.analysis_tab.schedule_btn.setText("Đặt Hẹn (F10)")
                self.view.analysis_tab.schedule_btn.setProperty("class", "primary")
                self.view.analysis_tab.schedule_btn.setStyleSheet("") 
                self.view.analysis_tab.schedule_btn.style().unpolish(self.view.analysis_tab.schedule_btn)
                self.view.analysis_tab.schedule_btn.style().polish(self.view.analysis_tab.schedule_btn)
            else:
                self.view.analysis_tab.schedule_btn.setText("Đặt Hẹn (F10) - Chưa khớp HIS")
                self.view.analysis_tab.schedule_btn.setStyleSheet("background-color: #64748B; color: white; border: none;")
                
        except Exception as e:
            print(f"Error checking HIS match: {e}")
            self.view.analysis_tab.schedule_btn.setText("Lỗi kiểm tra HIS")

    @Slot(QListWidgetItem)
    def handle_list_double_click(self, item):
        self.handle_view_history()

    @Slot()
    def handle_view_history(self):
        if not self.current_patient_id:
            ToastNotification.show_message(self.view, "Chưa chọn đối tượng.", type="warning")
            return
        self.view.analysis_tab.set_loading(True, "Đang tải dữ liệu tiêm chủng...")
        self.last_failed_task = {"type": "get_vaccines", "payload": {"doi_tuong_id": self.current_patient_id}}
        self.worker_service.request_history(self.current_patient_id)

    @Slot(str)
    def on_admin_search_changed(self, text):
        term = self.data_service.remove_vietnamese_accents(text.strip().lower())
        table = self.view.analysis_tab.admin_table
        for i in range(table.rowCount()):
            item = table.item(i, 0)
            should_show = True
            if item:
                cell_text = self.data_service.remove_vietnamese_accents(item.text().lower())
                if term and term not in cell_text:
                    should_show = False
            table.setRowHidden(i, not should_show)

    @Slot(str)
    def on_missing_search_changed(self, text):
        self.refresh_missing_table_visibility()

    def refresh_missing_table_visibility(self):
        search_term = self.data_service.remove_vietnamese_accents(self.view.analysis_tab.missing_search.text().strip().lower())
        table = self.view.analysis_tab.missing_table
        
        for i in range(table.rowCount()):
            item = table.item(i, 0)
            if not item: continue
            
            visible_by_search = True
            if search_term:
                cell_text = self.data_service.remove_vietnamese_accents(item.text().lower())
                if search_term not in cell_text:
                    visible_by_search = False
            
            table.setRowHidden(i, not visible_by_search)

    @Slot()
    def handle_export_vaccinated(self):
        if not self.analysis_results or not self.analysis_results.get("administered"):
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
            path = self.image_service.generate_image(items_to_export, self.analysis_results, is_missing_list=False)
            self.show_export_success(path)
        except Exception as e:
            ToastNotification.show_message(self.view, str(e), type="error")

    @Slot()
    def handle_delete_vaccinated(self):
        count, error = self.image_service.delete_images(is_missing_list=False)
        if error: ToastNotification.show_message(self.view, error, type="error")
        elif count == 0: ToastNotification.show_message(self.view, "Thư mục 'Vaccinated' trống.", type="info")
        else: ToastNotification.show_message(self.view, f"Đã xóa {count} ảnh đã tiêm.", type="success")

    @Slot()
    def handle_export_missing(self):
        if not self.analysis_results or not self.analysis_results.get("missing"):
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
            prepared_data = self.data_service.prepare_missing_data_for_export(items_to_export)
            path = self.image_service.generate_image(prepared_data, self.analysis_results, is_missing_list=True)
            self.show_export_success(path)
        except Exception as e:
            ToastNotification.show_message(self.view, str(e), type="error")
    
    @Slot()
    def handle_delete_missing(self):
        count, error = self.image_service.delete_images(is_missing_list=True)
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

    @Slot()
    def on_missing_selection_changed(self):
        pass

    @Slot(QTableWidgetItem)
    def handle_missing_item_double_click(self, item):
        if not self.matched_his_visit:
            ToastNotification.show_message(self.view, "Vui lòng kiểm tra và khớp hồ sơ HIS trước (Nút F10).", type="warning")
            return
            
        row = item.row()
        data_item = self.view.analysis_tab.missing_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        if not data_item: return
        
        vaccine_name = data_item.get("vaccine_name_for_popup", "vắc-xin này")
        due_date_str = data_item.get("date_str", "")
        
        confirm_msg = QMessageBox.question(
            self.view,
            "Xác nhận đặt hẹn",
            f"Bạn có muốn đặt hẹn tiêm {vaccine_name} không?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm_msg != QMessageBox.Yes:
            return

        default_days = 30
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, "%d/%m/%Y").date()
                today = date.today()
                delta = (due_date - today).days
                default_days = max(1, delta)
            except: 
                pass
        
        # --- NEW LOGIC: Map Vaccine Name to Code ---
        mapped_code = self.db_vaccine_service.get_appt_code_by_name(vaccine_name)
        
        # Open Dialog with Pre-filled Info
        self.open_schedule_dialog(default_days=default_days, pre_title=vaccine_name, pre_code=mapped_code)

    def open_schedule_dialog(self, default_days=30, pre_title="", pre_code=None):
        # Pass both initial_days and initial_code
        dialog = VaccineSelectionDialog(self.db_vaccine_service, self.view, initial_code=pre_code, initial_days=default_days)
        
        if pre_title:
            dialog.setWindowTitle(f"Đặt Hẹn: {pre_title}")
        
        if dialog.exec():
            appt_code = dialog.selected_appt_code
            appt_name = dialog.selected_appt_name
            days = dialog.selected_days
            
            ma_luotkham = self.matched_his_visit.get('ma_luotkham')
            id_benhnhan = self.matched_his_visit.get('id_benhnhan')
            
            self.view.analysis_tab.set_loading(True, "Đang đặt hẹn trên HIS...")
            
            ok, msg = self.db_vaccine_service.schedule_appointment(
                ma_luotkham=ma_luotkham,
                id_benhnhan=id_benhnhan,
                vaccine_id=None,
                vaccine_name=appt_name,
                days=days,
                appt_type_code=appt_code,
                item_type="DỊCH VỤ"
            )
            
            self.view.analysis_tab.set_loading(False)
            
            if ok:
                ToastNotification.show_message(self.view, f"Đặt hẹn thành công!\n{msg}", type="success")
            else:
                QMessageBox.critical(self.view, "Lỗi HIS", msg)

    @Slot()
    def handle_schedule_appointment(self):
        if not self.current_patient_info:
            ToastNotification.show_message(self.view, "Chưa chọn bệnh nhân (VNCDC).", type="warning")
            return

        if self.matched_his_visit:
            self.open_schedule_dialog()
            return

        phone = self.view.analysis_tab.phone_input.text().strip()
        name = self.current_patient_info.get('name', '')
        
        res = QMessageBox.question(
            self.view, 
            "Chưa có lượt khám", 
            f"Bệnh nhân '{name}' chưa có lượt khám khớp thông tin (Tên + SĐT + NS) trong hôm nay.\nBạn có muốn tạo mới trên HIS không?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if res == QMessageBox.Yes:
            add_dlg = AddPatientDialog(self.view)
            add_dlg.inp_name.setText(name.upper())
            add_dlg.inp_phone.setText(phone)
            
            dob_str = self.current_patient_info.get('birth', '')
            if dob_str:
                try:
                    dob_dt = datetime.strptime(dob_str, "%d/%m/%Y")
                    add_dlg.inp_dob.setDateTime(dob_dt)
                except: pass
            
            if add_dlg.exec():
                data = add_dlg.data
                self.view.analysis_tab.set_loading(True, "Đang tạo lượt khám...")
                ok, msg = self.db_patient_service.add_patient(
                    data['ten'], data['nam_sinh'], data['ngay_sinh_full'],
                    data['is_nam'], data['dia_chi'], data['sdt']
                )
                self.view.analysis_tab.set_loading(False)
                
                if ok:
                    self.check_his_patient_match()
                    if self.matched_his_visit:
                        ToastNotification.show_message(self.view, "Đã tạo lượt khám và khớp hồ sơ!", type="success")
                    else:
                        ToastNotification.show_message(self.view, "Đã tạo nhưng chưa khớp tự động. Vui lòng kiểm tra lại thông tin.", type="warning")
                else:
                    ToastNotification.show_message(self.view, f"Lỗi tạo lượt khám: {msg}", type="error")

    @Slot()
    def handle_add_vaccine_click(self):
        if not self.current_patient_id:
            ToastNotification.show_message(self.view, "Chưa chọn đối tượng.", type="warning")
            return
        dialog = AddVaccineDialog(self.view)
        if dialog.exec():
            vac_id, date_val = dialog.get_data()
            if not vac_id: return
            self.view.analysis_tab.set_loading(True, "Đang thêm mũi tiêm...")
            payload = {"DOI_TUONG_ID": self.current_patient_id, "VACXIN_ID": vac_id, "NGAY_TIEM": date_val}
            self.last_failed_task = {"type": "add_vaccine", "payload": payload}
            self.worker_service.request_add_vaccine(self.current_patient_id, vac_id, date_val)

    @Slot(bool)
    def handle_save_config(self, silent=False):
        user = self.view.config_tab.username_input.text().strip()
        pwd = self.view.config_tab.password_input.text().strip()
        theme = self.view.config_tab.theme_combo.currentText()
        
        self.current_theme = theme
        self.apply_app_theme(theme)
        self.update_theme_icon()
        
        if self.config_service.save_config(user, pwd, theme):
            if not silent:
                ToastNotification.show_message(self.view, "Đã lưu cấu hình.", type="success")
            if self.analysis_results: 
                self.update_ui_with_results(self.analysis_results)
            
    @Slot()
    def handle_update_vaccine_list(self):
        self.view.config_tab.update_vaccine_btn.setEnabled(False)
        self.view.config_tab.update_vaccine_btn.setText("Đang tải...")
        thread = threading.Thread(target=self._run_vaccine_update, daemon=True)
        thread.start()

    def _run_vaccine_update(self):
        try:
            url = "https://tiemchung.vncdc.gov.vn/Vacxin/DsVacxinKhongCovid"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            if isinstance(data, list):
                file_path = os.path.join(get_base_path(), "vaccine_list.json")
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                
                self.vaccine_update_success.emit(len(data))
            else:
                self.vaccine_update_error.emit("Dữ liệu trả về không hợp lệ.")
        except Exception as e:
            self.vaccine_update_error.emit(str(e))

    @Slot(int)
    def on_vaccine_update_success(self, count):
        self.view.config_tab.update_vaccine_btn.setEnabled(True)
        self.view.config_tab.update_vaccine_btn.setText("Cập nhật Dữ liệu Online")
        ToastNotification.show_message(self.view, f"Cập nhật thành công {count} vắc-xin!", type="success")

    @Slot(str)
    def on_vaccine_update_error(self, error_msg):
        self.view.config_tab.update_vaccine_btn.setEnabled(True)
        self.view.config_tab.update_vaccine_btn.setText("Cập nhật Dữ liệu Online")
        ToastNotification.show_message(self.view, f"Lỗi cập nhật: {error_msg}", type="error")

    @Slot()
    def handle_generate_debug(self):
        self.view.debug_tab.log_viewer.appendPlainText("--- User Generated Report ---")
        if self.analysis_results: self.view.debug_tab.log_viewer.appendPlainText(str(self.analysis_results))
        ToastNotification.show_message(self.view, "Đã tạo báo cáo debug.", type="info")

    @Slot()
    def handle_force_relogin(self):
        self.view.analysis_tab.set_loading(True, "Đang xóa cookies và đăng nhập lại...")
        self.perform_login(is_retry=True)

    @Slot(str)
    def handle_vncdc_search_request(self, phone):
        self.view.sidebar.btn_group.button(0).click()
        self.view.analysis_tab.phone_input.setText(phone)
        self.handle_search_click()