from PySide6.QtCore import Slot, QTimer
from ui_pyside.toast import ToastNotification
from .base_controller import BaseController

class AuthController(BaseController):
    def __init__(self, main_controller):
        super().__init__(main_controller)
        
        # --- Cấu hình Ping Timer ---
        self.ping_timer = QTimer()
        self.ping_timer.setInterval(10 * 60 * 1000) # 10 phút (600,000 ms)
        self.ping_timer.timeout.connect(self.send_keep_alive)
    
    def setup_connections(self):
        self.view.relogin_btn.clicked.connect(self.handle_force_relogin)
        
        # Connect Worker signals
        self.services['worker'].signals.worker_ready.connect(self.on_worker_ready)
        self.services['worker'].signals.login_finished.connect(self.on_login_finished)
        self.services['worker'].signals.session_expired.connect(self.on_session_expired)
        self.services['worker'].signals.relogin_finished.connect(self.on_relogin_finished)

    def send_keep_alive(self):
        """Gửi lệnh ping tới worker để giữ kết nối."""
        self.services['worker'].request_ping()

    def perform_login(self, is_retry=False):
        creds = self.services['config'].load_config()
        user = creds.get("username")
        pwd = creds.get("password")
        
        if not user or not pwd:
            self.view.analysis_tab.set_loading(False)
            if not is_retry: 
                ToastNotification.show_message(self.view, "Thiếu thông tin đăng nhập", type="warning")
            return
        
        if not is_retry: 
            self.state['last_failed_task'] = None
            self.services['worker'].request_login(user, pwd)
        else:
            self.services['worker'].request_relogin(user, pwd)

    @Slot()
    def handle_force_relogin(self):
        self.view.analysis_tab.set_loading(True, "Đang xóa cookies và đăng nhập lại...")
        self.perform_login(is_retry=True)

    @Slot()
    def on_worker_ready(self):
        self.view.analysis_tab.set_loading(True, "Đang đăng nhập hệ thống...")
        self.perform_login(is_retry=False)

    @Slot(bool, str)
    def on_login_finished(self, success, message):
        self.view.analysis_tab.set_loading(False)
        if success:
            ToastNotification.show_message(self.view, "Đăng nhập thành công!", type="success")
            self.main.retry_last_task()
            self.ping_timer.start() # Bắt đầu ping định kỳ
        else:
            ToastNotification.show_message(self.view, f"Đăng nhập thất bại: {message}", type="error")
            self.view.stacked_widget.setCurrentIndex(2)
            self.ping_timer.stop()

    @Slot(bool, str)
    def on_relogin_finished(self, success, message):
        self.view.analysis_tab.set_loading(False)
        if success:
            ToastNotification.show_message(self.view, "Đã đăng nhập lại thành công!", type="success")
            self.main.retry_last_task()
            self.ping_timer.start() # Bắt đầu ping định kỳ
        else:
            ToastNotification.show_message(self.view, f"Đăng nhập lại thất bại: {message}", type="error")
            self.view.stacked_widget.setCurrentIndex(2) 
            self.ping_timer.stop()

    @Slot()
    def on_session_expired(self):
        self.ping_timer.stop() # Dừng ping khi phiên hết hạn
        self.view.analysis_tab.set_loading(True, "Phiên hết hạn, đang đăng nhập lại...")
        self.perform_login(is_retry=True)