# group_checkers_special.py
from datetime import date, timedelta
from utils import VaccineAnalysisUtils
from rule_checker_utils import (
    GRACE_PERIOD_DAYS, _add_years, _add_months,
    get_administered_dose_records, _get_age_status_and_earliest_date,
    _check_first_dose_age_validity
)
from series_checkers import check_single_vaccine_series
import config_data

def check_mmr_equivalent_group(rule_key, rule_details, administered_map, missing_items_list, dob, analysis_date, all_vaccine_rules=None):
    group_display_name = rule_details.get("group_display_name", "Nhóm MMR")
    
    mvvac_rule = all_vaccine_rules.get("MVVAC", {})
    mvvac_names_norm = mvvac_rule.get("names_norm", [])
    mvvac_records = get_administered_dose_records(mvvac_names_norm, administered_map)

    if mvvac_records:
        mmr2_names_from_config = rule_details.get("raw_names_members", {}).get("MMR2", [])
        mmr2_normalizer = VaccineAnalysisUtils.normalize_vaccine_name
        mmr2_names_norm = list(set([mmr2_normalizer(n) for n in mmr2_names_from_config]))
        
        mmr2_records = get_administered_dose_records(mmr2_names_norm, administered_map)
        num_mmr2_doses = len(mmr2_records)

        if num_mmr2_doses == 1:
            last_mmr2_date = mmr2_records[0][1]
            next_due_date = _add_years(last_mmr2_date, 3)
            description = f"{group_display_name} - Cần tiêm mũi 2 (phác đồ MVVAC + MMR) sau 3 năm kể từ mũi MMR-II đầu tiên."
            earliest_next_date_for_listing = next_due_date
            status_tags = ["info", "booster_upcoming"] if analysis_date < next_due_date else ["due", "booster_due"]
            if analysis_date >= next_due_date:
                earliest_next_date_for_listing = analysis_date
            
            missing_items_list.append({
                "vaccine_name_for_popup": group_display_name,
                "description": description,
                "earliest_next_dose_date": earliest_next_date_for_listing,
                "status_tags": status_tags
            })
            return
        
        elif num_mmr2_doses >= 2:
            return

    administered_records = get_administered_dose_records(rule_details.get("names_norm_group", []), administered_map)

    if not administered_records:
        age_status_msg, earliest_date, age_tags = _get_age_status_and_earliest_date(dob, analysis_date, rule_details, group_display_name)
        default_doses_str = str(rule_details.get("regimens", [{}])[0].get("doses_required", "một số"))
        desc = f"{group_display_name} (Chưa tiêm - cần {default_doses_str} liều theo phác đồ). {age_status_msg}."
        missing_items_list.append({
            "vaccine_name_for_popup": group_display_name, 
            "description": desc, "earliest_next_dose_date": earliest_date, "status_tags": age_tags
        })
        return

    if not dob:
        missing_items_list.append({
            "vaccine_name_for_popup": group_display_name, 
            "description": f"{group_display_name} - Không thể xác định phác đồ do thiếu ngày sinh.",
            "earliest_next_dose_date": None, "status_tags": ["error_dob"]})
        return

    first_dose_date = administered_records[0][1]
    age_at_first_dose_months, _, _ = VaccineAnalysisUtils.get_age_at_date(dob, first_dose_date)

    if age_at_first_dose_months is None:
        missing_items_list.append({
            "vaccine_name_for_popup": group_display_name, 
            "description": f"{group_display_name} - Lỗi tính tuổi tại mũi đầu tiên của nhóm.",
            "earliest_next_dose_date": None, "status_tags": ["error_age_calculation"]})
        return

    group_age_check_details = {"min_age_months_at_first_dose": rule_details.get("min_age_months_overall_group")}
    if not _check_first_dose_age_validity(dob, first_dose_date, group_age_check_details, group_display_name, missing_items_list):
        missing_items_list.append({
            "vaccine_name_for_popup": group_display_name, 
            "description": f"{group_display_name} - Mũi đầu tiên của nhóm không hợp lệ về tuổi.",
            "earliest_next_dose_date": None, "status_tags": ["error_age_first_dose", "series_restart_needed"]})
        return
        
    applicable_regimen = None
    if not rule_details.get("regimens"):
         missing_items_list.append({
            "vaccine_name_for_popup": group_display_name, 
            "description": f"{group_display_name} - Lỗi cấu hình: không có 'regimens' cho nhóm.",
            "earliest_next_dose_date": None, "status_tags": ["error_config"]})
         return

    for regimen in rule_details["regimens"]:
        min_m = regimen.get("min_age_at_first_dose_months")
        max_m = regimen.get("max_age_at_first_dose_months")
        condition_met = True
        if min_m is not None and age_at_first_dose_months < min_m: condition_met = False
        if max_m is not None and age_at_first_dose_months > max_m: condition_met = False
        if condition_met:
            applicable_regimen = regimen
            break
            
    if not applicable_regimen:
        missing_items_list.append({
            "vaccine_name_for_popup": group_display_name, 
            "description": f"{group_display_name} - Không tìm thấy phác đồ phù hợp cho tuổi tiêm mũi đầu ({age_at_first_dose_months} tháng).",
            "earliest_next_dose_date": None, "status_tags": ["error_no_matching_rule"]})
        return
    
    regimen_specific_display_name = f"{group_display_name} ({applicable_regimen.get('regimen_name', 'theo phác đồ đã chọn')})"
    regimen_specific_rule_details = {
        "display_name": regimen_specific_display_name,
        "names_norm": rule_details.get("names_norm_group", []),
        "doses_required": applicable_regimen["doses_required"],
        "min_interval_days": applicable_regimen.get("min_interval_days", [None] * applicable_regimen["doses_required"]),
        "min_age_months_at_first_dose": applicable_regimen.get("min_age_at_first_dose_months"),
        "dose_specific_rules": applicable_regimen.get("dose_specific_rules", {})
    }
    check_single_vaccine_series(f"{rule_key}_regimen", regimen_specific_rule_details, administered_map, missing_items_list, dob, analysis_date, all_vaccine_rules)


def check_cumulative_group_doses(rule_key, rule_details, administered_map, missing_items_list, dob, analysis_date, all_vaccine_rules=None):
    rule_display_name = rule_details.get("group_display_name", rule_details.get("display_name", rule_key))
    total_doses_needed = rule_details.get("required_total_unique_doses", 0)
    all_group_records = get_administered_dose_records(rule_details.get("names_norm", []), administered_map)

    if total_doses_needed > 0 and len(all_group_records) >= total_doses_needed:
        return

    if not all_group_records:
        if total_doses_needed > 0:
            age_status_msg, earliest_date, age_tags = _get_age_status_and_earliest_date(dob, analysis_date, rule_details, rule_display_name)
            desc = f"{rule_display_name} (Chưa tiêm - cần {total_doses_needed} liều). {age_status_msg}."
            missing_items_list.append({
                "vaccine_name_for_popup": rule_display_name, 
                "description": desc, "earliest_next_dose_date": earliest_date, "status_tags": age_tags
            })
        return

    if not _check_first_dose_age_validity(dob, all_group_records[0][1], rule_details, rule_display_name, missing_items_list):
        missing_items_list.append({
            "vaccine_name_for_popup": rule_display_name, 
            "description": f"{rule_display_name} - Cần {total_doses_needed} liều (do mũi đầu của nhóm không hợp lệ về tuổi).",
            "earliest_next_dose_date": None, "status_tags": ["error_age_first_dose", "series_restart_needed"]})
        return
        
    num_doses_taken = len(all_group_records)

    if num_doses_taken < total_doses_needed:
        remaining = total_doses_needed - num_doses_taken
        desc = f"{rule_display_name} - Cần thêm {remaining} liều (đã tiêm {num_doses_taken}/{total_doses_needed} liều)."
        missing_items_list.append({
            "vaccine_name_for_popup": rule_display_name, 
            "description": desc,
            "earliest_next_dose_date": analysis_date,
            "status_tags": ["due"]
        })

def check_flu_group(rule_key, rule_details, administered_map, missing_items_list, dob, analysis_date, all_vaccine_rules=None):
    rule_display_name = rule_details["group_display_name"]
    
    # --- START: NEW FLU RECOGNITION LOGIC ---
    recognition_keywords = rule_details.get("recognition_keywords", [])
    administered_records = []
    
    if recognition_keywords:
        # Lặp qua tất cả các vắc-xin đã tiêm để tìm vắc-xin cúm bằng từ khóa
        for norm_name, dose_list in administered_map.items():
            if not dose_list: continue
            # Sử dụng tên gốc từ bản ghi đầu tiên để đối chiếu từ khóa
            raw_name = dose_list[0][2].lower() 
            for keyword in recognition_keywords:
                if keyword.lower() in raw_name:
                    administered_records.extend(dose_list)
                    break # Tìm thấy, chuyển sang loại vắc-xin tiếp theo
    
    # Sắp xếp tất cả các bản ghi tìm được theo ngày để xử lý
    administered_records.sort(key=lambda x: x[1])
    # --- END: NEW FLU RECOGNITION LOGIC ---

    min_age_months_flu = rule_details.get("min_age_months_at_first_dose", 6)

    if not administered_records:
        age_status_msg, earliest_date, age_tags = _get_age_status_and_earliest_date(dob, analysis_date, {"min_age_months_at_first_dose": min_age_months_flu}, rule_display_name)
        desc = f"{rule_display_name} (Chưa tiêm. Lần đầu (nếu <9 tuổi) có thể cần 2 mũi cách nhau ~1 tháng, sau đó nhắc lại hàng năm). {age_status_msg}."
        missing_items_list.append({
            "vaccine_name_for_popup": rule_display_name, 
            "description": desc, "earliest_next_dose_date": earliest_date, "status_tags": age_tags
        })
        return

    if not _check_first_dose_age_validity(dob, administered_records[0][1], {"min_age_months_at_first_dose": min_age_months_flu}, rule_display_name, missing_items_list):
        missing_items_list.append({
            "vaccine_name_for_popup": rule_display_name, 
            "description": f"{rule_display_name} - Cần tiêm lại đúng độ tuổi (lần đầu (nếu <9 tuổi) 2 mũi, sau đó hàng năm).",
            "earliest_next_dose_date": None, "status_tags": ["error_age_first_dose", "series_restart_needed"]})
        return

    num_doses_recorded = len(administered_records)
    age_at_first_flu_shot_years = None
    if dob:
        _, _, age_at_first_flu_shot_years = VaccineAnalysisUtils.get_age_at_date(dob, administered_records[0][1])
    
    is_first_vaccination_under_9 = age_at_first_flu_shot_years is not None and age_at_first_flu_shot_years < 9

    if is_first_vaccination_under_9 and num_doses_recorded == 1:
        required_initial_interval_days = rule_details.get("initial_series_interval_days", 28)
        earliest_next_dose2_date = administered_records[0][1] + timedelta(days=required_initial_interval_days)
        if earliest_next_dose2_date < analysis_date: earliest_next_dose2_date = analysis_date
        desc_second_dose = f"{rule_display_name} - Cần mũi 2 (do <9 tuổi lần đầu tiêm) cách mũi 1 khoảng {required_initial_interval_days // 7} tuần. Sau đó nhắc lại hàng năm."
        
        already_missing_second_dose = any(
            item.get("vaccine_name_for_popup") == rule_display_name and "flu_second_dose" in item.get("status_tags", [])
            for item in missing_items_list
        )
        if not already_missing_second_dose:
            missing_items_list.append({
                "vaccine_name_for_popup": rule_display_name,
                "description": desc_second_dose, 
                "earliest_next_dose_date": earliest_next_dose2_date,
                "status_tags": ["due", "flu_second_dose"]
            })
    
    last_dose_date = administered_records[-1][1]
    days_since_last_flu_shot = (analysis_date - last_dose_date).days
    ideal_next_annual_date = _add_years(last_dose_date, 1)
    earliest_booster_date = ideal_next_annual_date
    if earliest_booster_date < analysis_date: earliest_booster_date = analysis_date

    if days_since_last_flu_shot > (365 - 30):
         months_since_last = days_since_last_flu_shot // 30
         desc_annual = f"{rule_display_name} - Cần tiêm nhắc lại hàng năm (mũi cuối cách đây >{months_since_last} tháng)."
         
         already_missing_annual_booster = any(
            item.get("vaccine_name_for_popup") == rule_display_name and "flu_annual" in item.get("status_tags", [])
            for item in missing_items_list
         )
         if not already_missing_annual_booster:
             missing_items_list.append({
                 "vaccine_name_for_popup": rule_display_name, 
                 "description": desc_annual, "earliest_next_dose_date": earliest_booster_date,
                 "status_tags": ["due", "flu_annual"]
             })
