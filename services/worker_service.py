import multiprocessing
import queue
import time
from PySide6.QtCore import QObject, QThread, Signal, Slot

# Import the worker logic from the existing backend module
try:
    from live_worker.process_worker import playwright_process_worker
except ImportError:
    playwright_process_worker = None
    print("CRITICAL ERROR: Could not import 'live_worker.process_worker'. Ensure the folder exists.")

class WorkerSignals(QObject):
    """
    Defines the signals available from the running worker thread.
    """
    log_received = Signal(str)
    login_finished = Signal(bool, str)
    search_finished = Signal(list)
    vaccines_loaded = Signal(list)
    session_expired = Signal()
    add_vaccine_failed = Signal(str)
    relogin_finished = Signal(bool, str) # New signal for relogin
    
    # Internal signal to indicate the worker process has started/ready
    worker_ready = Signal()

class WorkerMonitor(QThread):
    """
    A background thread that polls the multiprocessing queue for messages 
    from the worker process and emits PySide6 signals.
    """
    def __init__(self, out_queue, signals):
        super().__init__()
        self.out_queue = out_queue
        self.signals = signals
        self._is_running = True

    def run(self):
        while self._is_running:
            try:
                # Non-blocking get with timeout to allow checking _is_running
                message = self.out_queue.get(timeout=0.1)
                
                if message is None:
                    break

                msg_type = message.get("type")
                payload = message.get("payload")

                if msg_type == "log":
                    self.signals.log_received.emit(payload)
                    # Detect readiness based on log message (legacy behavior adaptation)
                    if "Trình duyệt (giả mạo) đã sẵn sàng" in str(payload):
                        self.signals.worker_ready.emit()
                        
                elif msg_type == "login_finished":
                    self.signals.login_finished.emit(payload.get("ok"), payload.get("message", ""))
                    
                elif msg_type == "search_finished":
                    self.signals.search_finished.emit(payload)
                    
                elif msg_type == "vaccines_loaded":
                    self.signals.vaccines_loaded.emit(payload)
                    
                elif msg_type == "session_expired":
                    self.signals.session_expired.emit()
                    
                elif msg_type == "add_vaccine_failed":
                    self.signals.add_vaccine_failed.emit(payload.get("message", "Lỗi không xác định"))
                
                elif msg_type == "relogin_finished":
                    self.signals.relogin_finished.emit(payload.get("ok"), payload.get("message", ""))

            except queue.Empty:
                continue
            except Exception as e:
                print(f"WorkerMonitor Error: {e}")

    def stop(self):
        self._is_running = False
        self.wait()

class WorkerService(QObject):
    """
    Service to manage the multiprocessing worker and communication.
    """
    def __init__(self):
        super().__init__()
        self.signals = WorkerSignals()
        self.in_queue = multiprocessing.Queue()
        self.out_queue = multiprocessing.Queue()
        self.process = None
        self.monitor = None

    def start_worker(self):
        if playwright_process_worker is None:
            self.signals.log_received.emit("❌ Lỗi: Không tìm thấy module worker.")
            return

        if self.process and self.process.is_alive():
            return

        self.process = multiprocessing.Process(
            target=playwright_process_worker,
            args=(self.in_queue, self.out_queue)
        )
        self.process.start()

        self.monitor = WorkerMonitor(self.out_queue, self.signals)
        self.monitor.start()

    def stop_worker(self):
        if self.monitor:
            self.monitor.stop()
        
        if self.process and self.process.is_alive():
            self.in_queue.put(None)  # Sentinel to stop worker loop
            self.process.join(timeout=2)
            if self.process.is_alive():
                self.process.terminate()
        
        self.process = None
        self.monitor = None

    # --- Task Commands ---

    def request_login(self, username, password):
        self.in_queue.put({
            "type": "login", 
            "payload": {"username": username, "password": password}
        })

    def request_relogin(self, username, password):
        # Triggers the specific relogin logic in worker which clears cookies first
        self.in_queue.put({
            "type": "relogin", 
            "payload": {"username": username, "password": password}
        })

    def request_search(self, phone):
        self.in_queue.put({
            "type": "search_phone", 
            "payload": {"phone": phone}
        })

    def request_history(self, subject_id):
        self.in_queue.put({
            "type": "get_vaccines", 
            "payload": {"doi_tuong_id": subject_id}
        })

    def request_add_vaccine(self, subject_id, vaccine_id, date_str):
        self.in_queue.put({
            "type": "add_vaccine", 
            "payload": {
                "DOI_TUONG_ID": subject_id,
                "VACXIN_ID": vaccine_id,
                "NGAY_TIEM": date_str
            }
        })

    def request_ping(self):
        self.in_queue.put({
            "type": "ping", 
            "payload": {}
        })