# html_parser.py
from bs4 import BeautifulSoup
from collections import defaultdict
from datetime import datetime, date, timezone, timedelta # <<< THÊM timezone, timedelta
import config_data # For HTML element IDs

class HTMLVaccineParser:
    def __init__(self, normalize_func):
        self.normalize_vaccine_name = normalize_func

    def _extract_patient_info(self, soup):
        patient_name = None
        patient_dob_str = None
        system_date_str = None

        name_input = soup.find('input', id=config_data.HTML_PATIENT_NAME_ID)
        if name_input and 'value' in name_input.attrs:
            patient_name = name_input['value'].strip()

        dob_input = soup.find('input', id=config_data.HTML_PATIENT_DOB_ID)
        if not dob_input:
            dob_input = soup.find('input', id=config_data.HTML_PATIENT_DOB_HF_ID)
        if dob_input and 'value' in dob_input.attrs:
            patient_dob_str = dob_input['value'].strip()
        
        system_date_input = soup.find('input', id=config_data.HTML_SYSTEM_DATE_ID)
        if not system_date_input:
            system_date_input = soup.find('input', id=config_data.HTML_SYSTEM_DATE_HF_ID)
        if system_date_input and 'value' in system_date_input.attrs:
            system_date_str = system_date_input['value'].strip()
        else:
            # Lấy ngày hiện tại theo GMT+7 nếu không có trong HTML
            utc_now = datetime.now(timezone.utc)
            gmt7_now = utc_now.astimezone(timezone(timedelta(hours=7)))
            system_date_str = gmt7_now.strftime("%d/%m/%Y") # <<< THAY ĐỔI Ở ĐÂY
        
        return patient_name, patient_dob_str, system_date_str

    def _extract_vaccine_records(self, soup):
        vaccine_table = soup.find('table', id=config_data.HTML_VACCINE_TABLE_ID)
        administered_vaccine_details_map = defaultdict(list)
        administered_for_display = []
        error_msg_vaccine = None

        if not vaccine_table:
            return administered_vaccine_details_map, administered_for_display, "Không tìm thấy bảng vắc-xin (id='tblVacxin')."
        
        tbody = vaccine_table.find('tbody')
        if not tbody:
            return administered_vaccine_details_map, administered_for_display, "Không tìm thấy tbody trong bảng vắc-xin."

        rows = tbody.find_all('tr')
        if not rows:
            return administered_vaccine_details_map, administered_for_display, "Không tìm thấy hàng nào (tr) trong tbody."

        for row_idx, row in enumerate(rows):
            cols = row.find_all('td')
            if len(cols) > 4:
                vaccine_name_cell = cols[1]
                vaccine_name_raw = ""
                if vaccine_name_cell.contents:
                    for content in vaccine_name_cell.contents:
                        if isinstance(content, str) and content.strip():
                            vaccine_name_raw = content.strip()
                            break
                    if not vaccine_name_raw:
                        vaccine_name_raw = vaccine_name_cell.get_text(separator=" ", strip=True)
                
                dose_text_raw = cols[2].text.strip()
                date_text_raw = cols[4].text.strip()
                
                if vaccine_name_raw and date_text_raw:
                    normalized_name = self.normalize_vaccine_name(vaccine_name_raw)
                    administered_for_display.append((vaccine_name_raw, dose_text_raw, date_text_raw))
                    try:
                        dose_number_int = int(dose_text_raw)
                    except ValueError:
                        dose_number_int = 0
                    
                    try:
                        date_obj = datetime.strptime(date_text_raw.replace(" ",""), "%d/%m/%Y").date()
                        administered_vaccine_details_map[normalized_name].append(
                            (dose_number_int, date_obj, vaccine_name_raw, dose_text_raw, date_text_raw)
                        )
                    except ValueError:
                        print(f"Cảnh báo: Định dạng ngày không hợp lệ '{date_text_raw}' cho vắc xin {vaccine_name_raw}")
                        pass
        
        for norm_name in administered_vaccine_details_map:
            administered_vaccine_details_map[norm_name].sort(key=lambda x: x[1])

        if not administered_for_display and not error_msg_vaccine:
            error_msg_vaccine = "Không tìm thấy vắc-xin nào trong bảng có định dạng phù hợp."
            
        return administered_vaccine_details_map, administered_for_display, error_msg_vaccine

    def parse(self, html_content):
        soup = BeautifulSoup(html_content, 'lxml')
        patient_name, patient_dob_str, system_date_str = self._extract_patient_info(soup)
        vaccine_map, display_list, vaccine_err = self._extract_vaccine_records(soup)
        return vaccine_map, display_list, patient_name, patient_dob_str, system_date_str, vaccine_err