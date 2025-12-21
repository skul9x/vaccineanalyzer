"""
Các hàm utility hỗ trợ (ĐÃ CHUYỂN SANG BEAUTIFULSOUP)
"""
from datetime import datetime
import json
import os
import re
from pathlib import Path
from .logger_config import get_logger
from .constants import USER_INTERACTION_LOG

logger = get_logger()

def get_timestamp():
    """Lấy timestamp hiện tại định dạng HH:MM:SS"""
    return datetime.now().strftime("%H:%M:S")

def extract_subject_info(row_tag, out_queue) -> dict:
    """
    Trích xuất thông tin đối tượng từ thẻ <tr> của BeautifulSoup.
    (Thay thế cho hàm dùng Playwright)
    """
    try:
        # Lấy ID từ data-id attribute của row
        id_value = row_tag.get('data-id')
        
        if not id_value:
            # Bỏ qua các hàng không có data-id (ví dụ: header)
            return None
        
        # --- FIX: Xử lý trường hợp ID có dạng "1685693,0" ---
        # Một số trường hợp server trả về ID kèm ",0", cần loại bỏ để lấy ID chính xác (số nguyên)
        if isinstance(id_value, str):
            if "," in id_value:
                id_value = id_value.split(",")[0]
            id_value = id_value.strip()
        # ---------------------------------------------------
        
        out_queue.put({"type": "log", "payload": f"[Debug] Đang xử lý hàng. data-id: '{id_value}'"})
        
        cells = row_tag.find_all("td")
        if len(cells) < 5:
            out_queue.put({"type": "log", "payload": f"[Debug]   -> Lỗi: Hàng không đủ 5 ô (td)."})
            return None

        # Lấy tên từ td thứ 2
        name = cells[1].get_text(strip=True)
        out_queue.put({"type": "log", "payload": f"[Debug]   -> Tên: {name}"})
        
        # Lấy năm sinh từ td cuối cùng (thứ 5)
        birth = cells[4].get_text(strip=True)
        out_queue.put({"type": "log", "payload": f"[Debug]   -> Năm sinh: {birth}"})
        
        return {
            'name': name,
            'birth': birth,
            'id': id_value
        }
    except Exception as e:
        out_queue.put({"type": "log", "payload": f"[ERROR] Lỗi trích xuất hàng (subject): {e}"})
        return None

def extract_vaccine_info(row_tag) -> dict:
    """
    Trích xuất thông tin vắc-xin từ thẻ <tr> của BeautifulSoup.
    (Thay thế cho hàm dùng Playwright)
    """
    try:
        cells = row_tag.find_all("td")
        if len(cells) < 5:
            return None
        
        # Tên vắc-xin (ô thứ 2, index 1)
        # Lấy text node đầu tiên, bỏ qua <span class="sublabel">
        vaccine_name_node = cells[1].contents[0]
        vaccine_name = str(vaccine_name_node).strip()
        
        # Mũi (ô thứ 3, index 2)
        dose_text = cells[2].get_text(strip=True) 
        
        # Ngày tiêm (ô thứ 5, index 4)
        date_text = cells[4].get_text(strip=True)
        
        if vaccine_name and date_text:
            return {
                "vaccine_name": vaccine_name,
                "date": date_text,
                "dose": dose_text
            }
    except Exception as e:
        # Ghi log lỗi nếu cần, nhưng chủ yếu là return None
        print(f"[ERROR] Lỗi trích xuất hàng (vaccine): {e}")
        return None
    
    return None