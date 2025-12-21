# utils.py
import re
from datetime import datetime, date, timedelta

class VaccineAnalysisUtils:
    @staticmethod
    def normalize_vaccine_name(name):
        name = str(name)
        
        # --- SỬA ĐỔI: Thêm 2 dòng để chuẩn hóa tốt hơn ---
        name = name.replace(',', '.') # Chuyển "0,5ml" thành "0.5ml"
        name = re.sub(r'\s*\d+mcg/\d+(\.\d+)?ml\s*$', '', name, flags=re.IGNORECASE) # Xóa hậu tố " 3mcg/0.5ml"
        # --- KẾT THÚC SỬA ĐỔI ---

        name = re.sub(r'\s*\(.*?\)\s*', '', name) # Remove text in parentheses
        name = re.sub(r'\s+\d{4}/\d{4}\s*$', '', name) # Remove year/year suffix like 2023/2024
        name = re.sub(r'\s+20XX/20XX\s*$', '', name) # Remove 20XX/20XX suffix
        name = re.sub(r'\s+\d+(\.\d+)?ml\s*$', '', name) # Remove dosage like 0.5ml
        name = name.strip().lower()
        return name

    @staticmethod
    def get_age_at_date(dob, target_date):
        if not dob or not target_date:
            return None, None, None

        total_days = (target_date - dob).days
        if total_days < 0: # Target date is before DOB
            return None, None, None # Or handle as error appropriately

        years = target_date.year - dob.year
        # Adjust years if birthday hasn't occurred yet this year
        if (target_date.month, target_date.day) < (dob.month, dob.day):
            years -= 1
        years = max(0, years) # Ensure years is not negative

        # Calculate total completed months
        months_total = (target_date.year - dob.year) * 12 + (target_date.month - dob.month)
        # Adjust months if target_date's day is before dob's day in the same month (or if month calculation made it too high)
        if target_date.day < dob.day:
            months_total -= 1
        months_total = max(0, months_total) # Ensure months_total is not negative
        
        return months_total, total_days, years

    @staticmethod
    def get_age_string(dob_str, current_date_str):
        try:
            dob_str_cleaned = dob_str.strip().replace(" ", "")
            dob = datetime.strptime(dob_str_cleaned, "%d/%m/%Y").date()
        except ValueError:
            return "Ngày sinh không hợp lệ"
        
        try:
            current_date_str_cleaned = current_date_str.strip().replace(" ", "")
            current_dt = datetime.strptime(current_date_str_cleaned, "%d/%m/%Y").date()
        except ValueError:
            # Fallback to today if current_date_str is invalid or not provided properly
            current_dt = date.today()

        if dob > current_dt:
            return "Ngày sinh trong tương lai"

        months, total_days, years = VaccineAnalysisUtils.get_age_at_date(dob, current_dt)
        
        if months is None: # Should not happen if dob <= current_dt
             return "Lỗi tính tuổi"

        if months < 1 : # Less than 1 completed month
            if total_days < 7: # Less than 1 week old
                return f"{total_days} ngày tuổi"
            else: # Weeks and days
                weeks = total_days // 7
                remaining_days = total_days % 7
                if remaining_days == 0:
                    return f"{weeks} tuần tuổi"
                else:
                    return f"{weeks} tuần {remaining_days} ngày tuổi"
        elif months < 72: # Less than 6 years (72 months)
            return f"{months} tháng tuổi"
        else: # 6 years or older
            return f"{years} tuổi"

    @staticmethod
    def process_raw_vaccine_rules_data(raw_data):
        processed_rules = {}
        normalizer = VaccineAnalysisUtils.normalize_vaccine_name
        for key, details_dict in raw_data.items():
            new_details = details_dict.copy()
            
            # For single vaccines or groups that list primary raw_names (e.g., Flu, 6in1 before it was a group)
            if "raw_names" in new_details:
                new_details["names_norm"] = list(set([normalizer(n) for n in new_details["raw_names"]]))

            # For RULE_TYPE_MMR_EQUIVALENT_GROUP
            if "raw_names_members" in new_details:
                all_member_names_norm = []
                for member_key, raw_names_list in new_details["raw_names_members"].items():
                    all_member_names_norm.extend([normalizer(n) for n in raw_names_list])
                new_details["names_norm_group"] = list(set(all_member_names_norm))
            
            # For groups with alternative courses (Rota, Pneumo, HepA)
            if "courses" in new_details and isinstance(new_details["courses"], list):
                new_courses_list = []
                all_course_names_norm_for_group = [] # To populate names_norm for the group rule itself
                for course_dict in new_details["courses"]:
                    new_course = course_dict.copy()
                    if "raw_names" in new_course:
                        normalized_course_names = [normalizer(n) for n in new_course["raw_names"]]
                        new_course["names_norm"] = list(set(normalized_course_names))
                        all_course_names_norm_for_group.extend(normalized_course_names)
                    new_courses_list.append(new_course)
                new_details["courses"] = new_courses_list
                # For these group types, names_norm should include all names from all courses for get_administered_dose_records if checking group generally
                if not new_details.get("names_norm"): # If not already populated by a primary "raw_names"
                     new_details["names_norm"] = list(set(all_course_names_norm_for_group))


            # For RULE_TYPE_GROUP_CUMULATIVE_UNIQUE_MIN_AGE (like 6in1)
            # If it has "raw_names" like ["Infanrix Hexa", "Hexaxim"], this is already handled by the first "if" block.
            # It effectively becomes a list of interchangeable names for dose counting.

            processed_rules[key] = new_details
        return processed_rules