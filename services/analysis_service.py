from datetime import datetime, date, timedelta, timezone
from collections import defaultdict
import traceback

# Import core logic modules from the existing codebase
# Assumes these files are in the root directory or PYTHONPATH
try:
    import config_data
    from utils import VaccineAnalysisUtils
    from rule_processor import process_all_vaccine_rules
    from post_processor import apply_spacing_and_sort
except ImportError as e:
    print(f"CRITICAL ERROR: Missing core logic modules: {e}")

class AnalysisService:
    def __init__(self):
        self.vaccine_rules = None
        self.standard_vaccines = []
        self._load_rules()

    def _load_rules(self):
        try:
            raw_rules = config_data.VACCINE_RULES_DATA
            raw_standard_str = config_data.STANDARD_VACCINES_STRING
            
            if not raw_rules or not raw_standard_str:
                raise ValueError("Configuration data is empty.")

            self.vaccine_rules = VaccineAnalysisUtils.process_raw_vaccine_rules_data(raw_rules)
            self.standard_vaccines = [v.strip() for v in raw_standard_str.split(';') if v.strip()]
            
        except Exception as e:
            print(f"Error loading vaccine rules: {e}")
            self.vaccine_rules = {}
            self.standard_vaccines = []

    def analyze(self, patient_info, raw_vaccine_list):
        results = {
            "patient_name": patient_info.get("name"),
            "patient_dob": patient_info.get("birth"),
            "administered": [],
            "missing": [],
            "error": None
        }

        try:
            # 1. Prepare Context
            dob_str = patient_info.get("birth", "")
            patient_dob_obj = None
            if dob_str:
                try:
                    patient_dob_obj = datetime.strptime(dob_str.strip().replace(" ", ""), "%d/%m/%Y").date()
                except ValueError:
                    pass

            utc_now = datetime.now(timezone.utc)
            gmt7_now = utc_now.astimezone(timezone(timedelta(hours=7)))
            analysis_date = gmt7_now.date()

            # 2. Process Administered Data
            administered_map = defaultdict(list)
            
            for record in raw_vaccine_list:
                name = record.get("vaccine_name", "")
                date_text = record.get("date", "")
                dose_text = record.get("dose", "")

                if not name or not date_text:
                    continue

                norm_name = VaccineAnalysisUtils.normalize_vaccine_name(name)
                
                try:
                    dose_int = int(dose_text)
                except ValueError:
                    dose_int = 0

                try:
                    date_obj = datetime.strptime(date_text.replace(" ", ""), "%d/%m/%Y").date()
                    
                    # For logic
                    administered_map[norm_name].append((dose_int, date_obj, name, dose_text, date_text))
                    
                    # For display
                    age_str = ""
                    if patient_dob_obj:
                        age_str = VaccineAnalysisUtils.get_age_string(dob_str, date_text)
                    
                    results["administered"].append({
                        "name": name,
                        "dose": dose_text,
                        "date": date_text,
                        "age": age_str,
                        "raw_date": date_obj
                    })
                except ValueError:
                    continue

            # Sort administered by date
            results["administered"].sort(key=lambda x: (x["raw_date"], x["name"]))
            for key in administered_map:
                administered_map[key].sort(key=lambda x: x[1])

            # 3. Run Core Logic
            if not self.vaccine_rules:
                results["error"] = "Dữ liệu quy tắc vắc-xin chưa được khởi tạo."
                return results

            missing_raw = process_all_vaccine_rules(
                administered_map, 
                self.vaccine_rules, 
                patient_dob_obj, 
                analysis_date, 
                self.standard_vaccines
            )

            missing_final = apply_spacing_and_sort(
                missing_raw, 
                administered_map, 
                self.vaccine_rules, 
                analysis_date
            )

            # 4. Format Missing Data
            for item in missing_final:
                date_obj = item.get("earliest_next_dose_date")
                date_str = date_obj.strftime("%d/%m/%Y") if date_obj else ""
                
                results["missing"].append({
                    "description": item.get("description", ""),
                    "date_str": date_str,
                    "status_tags": item.get("status_tags", []),
                    "vaccine_name_for_popup": item.get("vaccine_name_for_popup", ""),
                    "raw_date": date_obj
                })

        except Exception as e:
            traceback.print_exc()
            results["error"] = f"Lỗi phân tích: {str(e)}"

        return results