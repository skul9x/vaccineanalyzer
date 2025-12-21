import atexit
from datetime import datetime, date
from PySide6.QtCore import QObject, Slot

from services.image_exporter import ImageExportService
from services.data_formatter import DataFormattingService
from services.config_service import ConfigService
from services.worker_service import WorkerService
from services.analysis_service import AnalysisService
from services.patient_service import PatientService
from services.vaccine_service import VaccineService

from .auth_controller import AuthController
from .search_controller import SearchController
from .analysis_controller import AnalysisController
from .his_controller import HISController
from .config_controller import ConfigController

class MainController(QObject):
    def __init__(self, main_window):
        super().__init__()
        self.view = main_window
        
        # --- Shared State ---
        self.state = {
            'current_patient_id': None,
            'current_patient_info': {},
            'matched_his_visit': None,
            'analysis_results': None,
            'last_failed_task': None
        }

        # --- Initialize Services ---
        self.services = {}
        self.init_services()
        
        # --- Initialize Sub-Controllers ---
        self.auth_ctrl = AuthController(self)
        self.search_ctrl = SearchController(self)
        self.analysis_ctrl = AnalysisController(self)
        self.his_ctrl = HISController(self)
        self.config_ctrl = ConfigController(self)
        
        # --- Setup UI & Connections ---
        self.setup_ui_components()
        self.setup_global_connections()
        
        self.auth_ctrl.setup_connections()
        self.search_ctrl.setup_connections()
        self.analysis_ctrl.setup_connections()
        self.his_ctrl.setup_connections()
        self.config_ctrl.setup_connections()
        
        # --- Initial Data Load ---
        self.config_ctrl.load_initial_data()
        
        # --- Start Worker ---
        self.services['worker'].start_worker()
        atexit.register(self.cleanup)

    def init_services(self):
        self.services['data'] = DataFormattingService()
        self.services['image'] = ImageExportService()
        self.services['config'] = ConfigService()
        self.services['worker'] = WorkerService()
        self.services['analysis'] = AnalysisService()
        self.services['db_patient'] = PatientService(logger_callback=self.on_worker_log)
        self.services['db_vaccine'] = VaccineService(logger_callback=self.on_worker_log)

    def setup_ui_components(self):
        # 1. Vaccination Tab (Legacy/Registration)
        self.view.vaccination_tab.patient_service = self.services['db_patient']
        self.view.vaccination_tab.vaccine_service = self.services['db_vaccine']
        self.view.vaccination_tab.request_vncdc_search.connect(self.search_ctrl.handle_vncdc_search_request)
        self.view.vaccination_tab.log_message.connect(self.on_worker_log)
        
        # 2. Analysis Tab (New: Assigned List)
        self.view.analysis_tab.view_assigned.set_service(self.services['db_patient'])
        self.view.analysis_tab.view_assigned.request_vncdc_search.connect(self.search_ctrl.handle_vncdc_search_request)
        # Load initial data for Assigned list
        self.view.analysis_tab.view_assigned.load_data()

    def setup_global_connections(self):
        self.services['worker'].signals.log_received.connect(self.on_worker_log)

    @Slot(str)
    def on_worker_log(self, message):
        self.view.debug_tab.log_viewer.appendPlainText(f"[SYSTEM] {message}")

    def retry_last_task(self):
        if self.state['last_failed_task']:
            self.view.analysis_tab.set_loading(True, "Thử lại tác vụ...")
            task_type = self.state['last_failed_task'].get("type")
            payload = self.state['last_failed_task'].get("payload")
            
            if task_type == "search_phone":
                self.services['worker'].request_search(payload["phone"])
            elif task_type == "get_vaccines":
                self.services['worker'].request_history(payload["doi_tuong_id"])
            elif task_type == "add_vaccine":
                self.services['worker'].request_add_vaccine(payload["DOI_TUONG_ID"], payload["VACXIN_ID"], payload["NGAY_TIEM"])
            
            self.state['last_failed_task'] = None

    def calculate_age_display(self, dob_str):
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

    def cleanup(self):
        # Save config on exit
        self.services['config'].save_config_file()
        self.services['worker'].stop_worker()