import re
from datetime import datetime

class DataFormattingService:
    @staticmethod
    def remove_vietnamese_accents(text):
        if not isinstance(text, str):
            return text
        mapping = {
            'á': 'a', 'à': 'a', 'ả': 'a', 'ã': 'a', 'ạ': 'a', 'ă': 'a', 'ắ': 'a', 'ằ': 'a', 'ẳ': 'a', 'ẵ': 'a', 'ặ': 'a', 'â': 'a', 'ấ': 'a', 'ầ': 'a', 'ẩ': 'a', 'ẫ': 'a', 'ậ': 'a', 'đ': 'd', 'é': 'e', 'è': 'e', 'ẻ': 'e', 'ẽ': 'e', 'ẹ': 'e', 'ê': 'e', 'ế': 'e', 'ề': 'e', 'ể': 'e', 'ễ': 'e', 'ệ': 'e', 'í': 'i', 'ì': 'i', 'ỉ': 'i', 'ĩ': 'i', 'ị': 'i', 'ó': 'o', 'ò': 'o', 'ỏ': 'o', 'õ': 'o', 'ọ': 'o', 'ô': 'o', 'ố': 'o', 'ồ': 'o', 'ổ': 'o', 'ỗ': 'o', 'ộ': 'o', 'ơ': 'o', 'ớ': 'o', 'ờ': 'o', 'ở': 'o', 'ỡ': 'o', 'ợ': 'o', 'ú': 'u', 'ù': 'u', 'ủ': 'u', 'ũ': 'u', 'ụ': 'u', 'ư': 'u', 'ứ': 'u', 'ừ': 'u', 'ử': 'u', 'ữ': 'u', 'ự': 'u', 'ý': 'y', 'ỳ': 'y', 'ỷ': 'y', 'ỹ': 'y', 'ỵ': 'y',
            'Á': 'A', 'À': 'A', 'Ả': 'A', 'Ã': 'A', 'Ạ': 'A', 'Ă': 'A', 'Ắ': 'A', 'Ằ': 'A', 'Ẳ': 'A', 'Ẵ': 'A', 'Ặ': 'A', 'Â': 'A', 'Ấ': 'A', 'Ầ': 'A', 'Ẩ': 'A', 'Ẫ': 'A', 'Ậ': 'A', 'Đ': 'D', 'É': 'E', 'È': 'E', 'Ẻ': 'E', 'Ẽ': 'E', 'Ẹ': 'E', 'Ê': 'E', 'Ế': 'E', 'Ề': 'E', 'Ể': 'E', 'Ễ': 'E', 'Ệ': 'E', 'Í': 'I', 'Ì': 'I', 'Ỉ': 'I', 'Ĩ': 'I', 'Ị': 'I', 'Ó': 'O', 'Ò': 'O', 'Ỏ': 'O', 'Õ': 'O', 'Ọ': 'O', 'Ô': 'O', 'Ố': 'O', 'Ồ': 'O', 'Ổ': 'O', 'Ỗ': 'O', 'Ộ': 'O', 'Ơ': 'O', 'Ớ': 'O', 'Ờ': 'O', 'Ở': 'O', 'Ỡ': 'O', 'Ợ': 'O', 'Ú': 'U', 'Ù': 'U', 'Ủ': 'U', 'Ũ': 'U', 'Ụ': 'U', 'Ư': 'U', 'Ứ': 'U', 'Ừ': 'U', 'Ử': 'U', 'Ữ': 'U', 'Ự': 'U', 'Ý': 'Y', 'Ỳ': 'Y', 'Ỷ': 'Y', 'Ỹ': 'Y', 'Ỵ': 'Y'
        }
        translation_table = str.maketrans(mapping)
        return text.translate(translation_table)

    @staticmethod
    def filter_administered_data(full_data_list, search_term):
        if not search_term:
            return full_data_list
            
        term_norm = DataFormattingService.remove_vietnamese_accents(search_term.lower())
        filtered = []
        
        for item in full_data_list:
            if isinstance(item, (tuple, list)):
                item_str = " ".join(map(str, item)).lower()
            elif isinstance(item, dict):
                item_str = " ".join(map(str, item.values())).lower()
            else:
                item_str = str(item).lower()
                
            item_str_norm = DataFormattingService.remove_vietnamese_accents(item_str)
            
            if term_norm in item_str_norm:
                filtered.append(item)
                
        return filtered

    @staticmethod
    def filter_missing_data(missing_items_map, search_term):
        if not search_term:
            return list(missing_items_map.keys())
            
        term_norm = DataFormattingService.remove_vietnamese_accents(search_term.lower())
        matching_ids = []
        
        for iid, item_data in missing_items_map.items():
            desc = item_data.get("description", "")
            date_obj = item_data.get("earliest_next_dose_date")
            date_str = date_obj.strftime("%d/%m/%Y") if date_obj else ""
            
            combined_str = f"{desc} {date_str}".lower()
            combined_norm = DataFormattingService.remove_vietnamese_accents(combined_str)
            
            if term_norm in combined_norm:
                matching_ids.append(iid)
                
        return matching_ids

    @staticmethod
    def get_status_tags_for_missing_item(status_tags_list):
        if any(t in ["due", "flu_second_dose", "flu_annual", "multiple_options"] for t in status_tags_list):
            return "due"
        elif any(t in ["too_young", "error_age_first_dose", "too_early", "series_restart_needed", "too_old_to_start", "too_old_at_first_dose"] for t in status_tags_list):
            return "warning"
        elif any(t in ["info", "coverage_by_other", "flu_interval_note", "info_too_old_or_no_option"] for t in status_tags_list):
            return "info"
        elif any(t.startswith("error") for t in status_tags_list):
            return "error"
        return "normal"

    @staticmethod
    def prepare_missing_data_for_export(items):
        """
        Prepares the raw items (both missing and administered) for ImageExportService.
        """
        items_to_render = []
        EXCLUDED_TAGS = {"coverage_by_other", "coverage_by_alternative", "info_too_old_or_no_option", 
                         "too_old_to_start", "error_config", "error_dob"}
        
        for item in items:
            status_tags = item.get("status_tags", [])
            if any(tag in EXCLUDED_TAGS for tag in status_tags):
                continue
                
            raw_date = item.get("raw_date")
            if not raw_date:
                continue
            
            # Case 1: Missing item (has 'vaccine_name_for_popup')
            if "vaccine_name_for_popup" in item:
                popup_name = item.get("vaccine_name_for_popup", "Vắc xin không rõ")
                clean_name = re.split(r'[:(]', popup_name)[0].strip()
                items_to_render.append({
                    "name": clean_name,
                    "date": raw_date.strftime("%d/%m/%Y"),
                    "raw_date": raw_date
                })
            
            # Case 2: Administered item (has 'name' and 'dose')
            elif "name" in item and "dose" in item:
                items_to_render.append({
                    "name": item["name"],
                    "date": raw_date.strftime("%d/%m/%Y"),
                    "dose": item.get("dose", ""),
                    "age": item.get("age", ""),
                    "raw_date": raw_date
                })

        # Group Flu vaccines logic (similar to legacy)
        processed_items = []
        flu_item_data = None
        flu_keywords = ["vaxigrip", "influvac", "gc flu", "ivacflu-s", "cúm"]
        
        for item in items_to_render:
            is_flu = any(kw in item["name"].lower() for kw in flu_keywords)
            if is_flu:
                if flu_item_data is None:
                    flu_item_data = item.copy()
                    flu_item_data["name"] = "Vắc xin Cúm"
                else:
                    # Keep earliest flu date for Missing, or latest for Administered (logic depends on context, simple sort here)
                    if item["raw_date"] < flu_item_data["raw_date"]:
                        flu_item_data["date"] = item["date"]
                        flu_item_data["raw_date"] = item["raw_date"]
            else:
                processed_items.append(item)
        
        if flu_item_data:
            processed_items.append(flu_item_data)
            
        # Sort by date then name
        processed_items.sort(key=lambda x: (datetime.strptime(x["date"], "%d/%m/%Y").date(), x["name"]))
        
        return processed_items