from datetime import datetime, date
from PySide6.QtCore import Slot, Qt
from PySide6.QtGui import QShortcut, QKeySequence
from PySide6.QtWidgets import QMessageBox, QTableWidgetItem
from ui_pyside.toast import ToastNotification
from ui_pyside.dialogs.add_patient_dialog import AddPatientDialog
from ui_pyside.dialogs.vaccine_selection_dialog import VaccineSelectionDialog
from .base_controller import BaseController

class HISController(BaseController):
    def __init__(self, main_controller):
        super().__init__(main_controller)

    def setup_connections(self):
        self.view.analysis_tab.schedule_btn.clicked.connect(self.handle_schedule_appointment)
        self.view.analysis_tab.missing_table.itemDoubleClicked.connect(self.handle_missing_item_double_click)
        
        self.f10_shortcut = QShortcut(QKeySequence("F10"), self.view)
        self.f10_shortcut.activated.connect(self.handle_schedule_appointment)

    def check_his_patient_match(self):
        self.state['matched_his_visit'] = None
        
        self.view.analysis_tab.schedule_btn.setEnabled(False)
        self.view.analysis_tab.schedule_btn.setText("Đặt Hẹn (F10) - Chưa khớp HIS")
        self.view.analysis_tab.schedule_btn.setStyleSheet("background-color: #64748B; color: white; border: none;")

        vncdc_info = self.state.get('current_patient_info', {})
        vncdc_name = vncdc_info.get('name', '').strip()
        vncdc_dob_str = vncdc_info.get('birth', '').strip()
        
        if not vncdc_name:
            return

        his_list = []
        try:
            his_list = self.view.analysis_tab.view_assigned.current_data
        except AttributeError:
            print("Warning: AssignedListView has no 'current_data'.")
            return

        if not his_list:
            return

        vncdc_name_norm = self.services['data'].remove_vietnamese_accents(vncdc_name.lower())
        
        vncdc_dob_obj = None
        vncdc_year = 0
        try:
            vncdc_dob_obj = datetime.strptime(vncdc_dob_str, "%d/%m/%Y").date()
            vncdc_year = vncdc_dob_obj.year
        except:
            if len(vncdc_dob_str) == 4 and vncdc_dob_str.isdigit():
                vncdc_year = int(vncdc_dob_str)

        for visit in his_list:
            his_name = visit.get('ten_benhnhan', '')
            his_name_norm = self.services['data'].remove_vietnamese_accents(his_name.lower())
            
            if vncdc_name_norm != his_name_norm:
                continue
            
            match_dob = False
            his_dob_raw = visit.get('ngay_sinh', '')
            his_nam_sinh = visit.get('nam_sinh')
            
            if his_dob_raw and vncdc_dob_obj:
                his_dob_obj = None
                if isinstance(his_dob_raw, (datetime, date)):
                    his_dob_obj = his_dob_raw
                elif isinstance(his_dob_raw, str):
                    try:
                        if "-" in his_dob_raw:
                            his_dob_obj = datetime.strptime(his_dob_raw[:10], "%Y-%m-%d").date()
                        elif "/" in his_dob_raw:
                            his_dob_obj = datetime.strptime(his_dob_raw[:10], "%d/%m/%Y").date()
                    except: pass
                
                if isinstance(his_dob_obj, datetime): his_dob_obj = his_dob_obj.date()
                
                if his_dob_obj == vncdc_dob_obj:
                    match_dob = True
            
            if not match_dob and vncdc_year > 0:
                try:
                    his_year = int(his_nam_sinh) if his_nam_sinh else 0
                    if not his_year and isinstance(his_dob_raw, (datetime, date)):
                        his_year = his_dob_raw.year
                    
                    if his_year == vncdc_year:
                        match_dob = True
                except: pass
            
            if match_dob:
                self.state['matched_his_visit'] = visit
                break
        
        if self.state['matched_his_visit']:
            self.view.analysis_tab.schedule_btn.setEnabled(True)
            self.view.analysis_tab.schedule_btn.setText("Đặt Hẹn (F10)")
            self.view.analysis_tab.schedule_btn.setStyleSheet("") 
            self.view.analysis_tab.schedule_btn.setProperty("class", "primary")
            self.view.analysis_tab.schedule_btn.style().unpolish(self.view.analysis_tab.schedule_btn)
            self.view.analysis_tab.schedule_btn.style().polish(self.view.analysis_tab.schedule_btn)

    @Slot(QTableWidgetItem)
    def handle_missing_item_double_click(self, item):
        if not self.state['matched_his_visit']:
            ToastNotification.show_message(self.view, "Vui lòng kiểm tra và khớp hồ sơ HIS trước (Nút F10).", type="warning")
            return
            
        row = item.row()
        data_item = self.view.analysis_tab.missing_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        if not data_item: return
        
        vaccine_name = data_item.get("vaccine_name_for_popup", "vắc-xin này")
        due_date_str = data_item.get("date_str", "")
        
        default_days = 30
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, "%d/%m/%Y").date()
                today = date.today()
                delta = (due_date - today).days
                default_days = max(1, delta)
            except: 
                pass
        
        mapped_code = self.services['db_vaccine'].get_appt_code_by_name(vaccine_name)
        self.open_schedule_dialog(default_days=default_days, pre_title=vaccine_name, pre_code=mapped_code)

    def open_schedule_dialog(self, default_days=30, pre_title="", pre_code=None):
        patient_id = self.state['matched_his_visit'].get('id_benhnhan')
        patient_name = self.state['matched_his_visit'].get('ten_benhnhan', 'Bệnh nhân')

        dialog = VaccineSelectionDialog(
            self.services['db_vaccine'], 
            self.view, 
            initial_code=pre_code, 
            initial_days=default_days,
            patient_id=patient_id,
            patient_name=patient_name
        )
        
        if pre_title:
            dialog.setWindowTitle(f"Đặt Hẹn: {pre_title}")
        
        if dialog.exec():
            appt_code = dialog.selected_appt_code
            appt_name = dialog.selected_appt_name
            days = dialog.selected_days
            target_date = dialog.selected_date
            
            ma_luotkham = self.state['matched_his_visit'].get('ma_luotkham')
            id_benhnhan = self.state['matched_his_visit'].get('id_benhnhan')
            
            self.view.analysis_tab.set_loading(True, "Đang đặt hẹn trên HIS...")
            
            ok, msg = self.services['db_vaccine'].schedule_appointment(
                ma_luotkham=ma_luotkham,
                id_benhnhan=id_benhnhan,
                vaccine_id=None,
                vaccine_name=appt_name,
                days=days,
                appt_type_code=appt_code,
                item_type="DỊCH VỤ",
                target_date=target_date
            )
            
            self.view.analysis_tab.set_loading(False)
            
            if ok:
                ToastNotification.show_message(self.view, f"Đặt hẹn thành công!\n{msg}", type="success")
            else:
                QMessageBox.critical(self.view, "Lỗi HIS", msg)

    @Slot()
    def handle_schedule_appointment(self):
        table = self.view.analysis_tab.missing_table
        selected_rows = table.selectionModel().selectedRows()
        target_item = None
        
        if selected_rows:
            target_item = table.item(selected_rows[0].row(), 0)
        elif table.rowCount() > 0:
            table.selectRow(0)
            target_item = table.item(0, 0)
            
        if target_item:
            self.handle_missing_item_double_click(target_item)
        else:
            ToastNotification.show_message(self.view, "Danh sách cần tiêm đang trống.", type="warning")