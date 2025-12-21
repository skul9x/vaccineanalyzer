import threading
import requests
import json
import os
import qtawesome as qta
from PySide6.QtCore import Slot, Signal
from PySide6.QtWidgets import QApplication
from ui_pyside.toast import ToastNotification
from ui_pyside.styles import AppTheme
from live_worker.vaccine_data import get_base_path
from .base_controller import BaseController

class ConfigController(BaseController):
    vaccine_update_success = Signal(int)
    vaccine_update_error = Signal(str)

    def __init__(self, main_controller):
        super().__init__(main_controller)
        self.current_theme = "Dark"

    def setup_connections(self):
        self.view.config_tab.save_btn.clicked.connect(self.handle_save_config)
        self.view.config_tab.update_vaccine_btn.clicked.connect(self.handle_update_vaccine_list)
        self.view.debug_tab.generate_btn.clicked.connect(self.handle_generate_debug)
        self.view.theme_toggle_btn.clicked.connect(self.handle_theme_toggle)
        
        self.vaccine_update_success.connect(self.on_vaccine_update_success)
        self.vaccine_update_error.connect(self.on_vaccine_update_error)

    def load_initial_data(self):
        creds = self.services['config'].load_config()
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
        new_theme = "Light" if self.current_theme == "Dark" else "Dark"
        self.current_theme = new_theme
        
        idx = self.view.config_tab.theme_combo.findText(new_theme)
        if idx >= 0: self.view.config_tab.theme_combo.setCurrentIndex(idx)
        
        self.apply_app_theme(new_theme)
        self.update_theme_icon()
        self.handle_save_config(silent=True)

    @Slot(bool)
    def handle_save_config(self, silent=False):
        user = self.view.config_tab.username_input.text().strip()
        pwd = self.view.config_tab.password_input.text().strip()
        theme = self.view.config_tab.theme_combo.currentText()
        
        self.current_theme = theme
        self.apply_app_theme(theme)
        self.update_theme_icon()
        
        if self.services['config'].save_config(user, pwd, theme):
            if not silent:
                ToastNotification.show_message(self.view, "Đã lưu cấu hình.", type="success")
            # Refresh UI if results exist to apply color changes potentially
            if self.state['analysis_results']: 
                self.main.analysis_ctrl.update_ui_with_results(self.state['analysis_results'])

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
        if self.state['analysis_results']: 
            self.view.debug_tab.log_viewer.appendPlainText(str(self.state['analysis_results']))
        ToastNotification.show_message(self.view, "Đã tạo báo cáo debug.", type="info")