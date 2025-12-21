from PySide6.QtCore import Slot, QSize
from PySide6.QtWidgets import QListWidgetItem
import qtawesome as qta
from ui_pyside.toast import ToastNotification
from ui_pyside.analysis_tab import PatientResultItem
from .base_controller import BaseController

class SearchController(BaseController):
    def __init__(self, main_controller):
        super().__init__(main_controller)
        self.search_results_map = {}

    def setup_connections(self):
        # Input connections
        self.view.analysis_tab.search_btn.clicked.connect(self.handle_search_click)
        self.view.analysis_tab.phone_input.returnPressed.connect(self.handle_search_click)
        
        # Result list connections
        self.view.analysis_tab.result_list.currentRowChanged.connect(self.handle_patient_selected)
        # itemClicked is better for mouse interaction than currentChanged sometimes
        self.view.analysis_tab.result_list.itemClicked.connect(self.on_item_clicked)
        self.view.analysis_tab.result_list.itemDoubleClicked.connect(self.main.analysis_ctrl.handle_list_double_click)
        
        # Worker signals
        self.services['worker'].signals.search_finished.connect(self.on_search_finished)

    @Slot()
    def handle_search_click(self):
        phone = self.view.analysis_tab.phone_input.text().strip()
        if not phone or not phone.isdigit() or len(phone) < 9:
            self.view.analysis_tab.set_phone_error(True)
            ToastNotification.show_message(self.view, "Số điện thoại không hợp lệ.", type="warning")
            return
        
        self.view.analysis_tab.set_phone_error(False)
        
        # Clear previous state (list stays visible - just cleared)
        self.view.analysis_tab.result_list.clear()
        self.search_results_map.clear()
        
        self.view.analysis_tab.set_loading(True, f"Đang tìm kiếm SĐT: {phone}...")
        self.state['last_failed_task'] = {"type": "search_phone", "payload": {"phone": phone}}
        self.services['worker'].request_search(phone)

    @Slot(list)
    def on_search_finished(self, results):
        self.view.analysis_tab.set_loading(False)
        self.view.analysis_tab.result_list.clear()
        self.search_results_map.clear()
        
        if not results:
            # List stays visible but empty
            ToastNotification.show_message(self.view, "Không tìm thấy SĐT này.", type="warning")
            return
            
        # Populate List with custom PatientResultItem widgets
        for idx, subject in enumerate(results):
            # Create custom widget for the result item
            gender = subject.get('gender', None)
            patient_widget = PatientResultItem(
                name=subject['name'],
                dob=subject['birth'],
                gender=gender,
                row_index=idx
            )
            
            # Connect push icon click to add vaccine handler
            patient_widget.push_clicked.connect(self._handle_push_clicked)
            
            # Create list item and set its size
            item = QListWidgetItem()
            item.setSizeHint(QSize(0, 36))  # Fixed height for each row
            
            self.view.analysis_tab.result_list.addItem(item)
            self.view.analysis_tab.result_list.setItemWidget(item, patient_widget)
            self.search_results_map[idx] = subject
        
        # List is always visible - no need to show()
        
        # Auto-select if only one result
        if len(results) == 1:
            self.view.analysis_tab.result_list.setCurrentRow(0)
        else:
            ToastNotification.show_message(self.view, f"Tìm thấy {len(results)} kết quả.", type="success")

    @Slot(int)
    def _handle_push_clicked(self, row_index):
        """Handle push icon click - triggers add vaccine for that patient"""
        subject = self.search_results_map.get(row_index)
        if subject:
            # Set the current patient first
            self.state['current_patient_id'] = subject['id']
            self.state['current_patient_info'] = subject
            # Trigger add vaccine
            self.main.analysis_ctrl.handle_add_vaccine_click()

    @Slot(QListWidgetItem)
    def on_item_clicked(self, item):
        # Just ensures the row changed logic fires if already selected
        row = self.view.analysis_tab.result_list.row(item)
        self.handle_patient_selected(row)

    @Slot(int)
    def handle_patient_selected(self, row_index):
        if row_index < 0: return
        subject = self.search_results_map.get(row_index)
        if subject:
            self.state['current_patient_id'] = subject['id']
            self.state['current_patient_info'] = subject
            
            # Auto-check HIS match (no longer updating profile since it's removed)
            self.main.his_ctrl.check_his_patient_match()

    @Slot(str)
    def handle_vncdc_search_request(self, phone):
        self.view.sidebar.btn_group.button(0).click()
        self.view.analysis_tab.phone_input.setText(phone)
        self.handle_search_click()