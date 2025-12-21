# live_worker/process_worker.py
"""
Process Worker: Chạy bằng Requests trong một tiến trình riêng biệt.
Giao tiếp với luồng GUI chính thông qua Queues.
(ĐÃ LOẠI BỎ HOÀN TOÀN PLAYWRIGHT)
"""
import time
import re
import requests
from bs4 import BeautifulSoup

# Các hằng số và hàm tiện ích đã được cập nhật
from .constants import (
    LOGIN_URL, INDEX_URL, SEARCH_URL, DETAIL_URL,
    LOGIN_TIMEOUT, FORM_TIMEOUT,
    ADD_VACCINE_URL
)
from .utils import extract_subject_info, extract_vaccine_info

# --- State của tiến trình ---
WORKER_USERNAME = None
WORKER_PASSWORD = None
DEFAULT_CO_SO_ID = "26953"

def _log(out_queue, msg, level="INFO"):
    """Gửi log về cho GUI qua queue."""
    out_queue.put({"type": "log", "payload": f"[{level}] {msg}"})

def _is_login_page(html_content: str) -> bool:
    """Kiểm tra xem nội dung HTML có phải là trang đăng nhập không."""
    return "UserName" in html_content and "__RequestVerificationToken" in html_content

def _extract_subjects_from_html(out_queue, html_content) -> list:
    """Trích xuất danh sách đối tượng từ HTML (dùng BeautifulSoup)."""
    subjects = []
    try:
        _log(out_queue, "Đang phân tích HTML kết quả tìm kiếm...")
        soup = BeautifulSoup(html_content, 'lxml')
        
        table = soup.find("table", id="doiTuongSearchResult")
        if not table:
            _log(out_queue, "Không tìm thấy table#doiTuongSearchResult trong HTML.", "WARNING")
            return []

        rows = table.find("tbody").find_all("tr")
        _log(out_queue, f"Tìm thấy {len(rows)} hàng trong bảng kết quả.")

        for row_tag in rows:
            subject_info = extract_subject_info(row_tag, out_queue)
            if subject_info and subject_info.get('id'):
                subjects.append(subject_info)
        _log(out_queue, f"Trích xuất thành công {len(subjects)} đối tượng.")
    except Exception as e:
        _log(out_queue, f"Lỗi khi trích xuất đối tượng từ HTML: {e}", "ERROR")
    return subjects

def _extract_vaccines_from_html(out_queue, html_content) -> list:
    """Trích xuất danh sách vắc-xin từ HTML chi tiết (dùng BeautifulSoup)."""
    vaccines = []
    try:
        _log(out_queue, "Đang phân tích HTML chi tiết đối tượng...")
        soup = BeautifulSoup(html_content, 'lxml')
        
        table = soup.find("table", id="tblVacxin")
        if not table:
            _log(out_queue, "Không tìm thấy table#tblVacxin trong HTML.", "WARNING")
            return []

        rows = table.find("tbody").find_all("tr")
        _log(out_queue, f"Tìm thấy {len(rows)} mũi tiêm trong bảng.")

        for row_tag in rows:
            vaccine_info = extract_vaccine_info(row_tag)
            if vaccine_info:
                vaccines.append(vaccine_info)
        
        _log(out_queue, f"Trích xuất xong {len(vaccines)} mũi tiêm.")
    except Exception as e:
        _log(out_queue, f"Lỗi khi trích xuất vắc-xin từ HTML: {e}", "ERROR")
    return vaccines

def _perform_login(out_queue, session, username, password):
    """Thực hiện đăng nhập (phiên bản requests)."""
    try:
        _log(out_queue, f"Mở trang đăng nhập (GET): {LOGIN_URL}")
        
        try:
            get_response = session.get(LOGIN_URL, timeout=LOGIN_TIMEOUT)
            get_response.raise_for_status()
        except requests.RequestException as e:
            _log(out_queue, f"Lỗi (GET) khi tải trang Login: {e}", "ERROR")
            raise Exception("Không thể tải trang đăng nhập.")

        _log(out_queue, "Đang tìm kiếm Token chống giả mạo (CSRF)...")
        soup = BeautifulSoup(get_response.text, 'lxml')
        token_tag = soup.find("input", {"name": "__RequestVerificationToken"})
        
        if not token_tag or 'value' not in token_tag.attrs:
            _log(out_queue, "Không tìm thấy __RequestVerificationToken!", "ERROR")
            raise Exception("Lỗi cấu trúc trang, không tìm thấy token.")
            
        token = token_tag['value']
        _log(out_queue, "Đã tìm thấy Token. Đang chuẩn bị (POST)...")

        form_data = {
            '__RequestVerificationToken': (None, token),
            'UserName': (None, username),
            'password': (None, password),
            'remember_me': (None, 'false'),
        }

        try:
            post_response = session.post(
                LOGIN_URL,
                files=form_data, 
                timeout=LOGIN_TIMEOUT,
                allow_redirects=True 
            )
            post_response.raise_for_status()
        except requests.RequestException as e:
            _log(out_queue, f"Lỗi (POST) khi gửi thông tin Login: {e}", "ERROR")
            raise Exception("Gửi thông tin đăng nhập thất bại.")

        if INDEX_URL not in post_response.url:
            _log(out_queue, f"Đăng nhập thất bại. URL cuối cùng: {post_response.url}", "ERROR")
            raise Exception("Đăng nhập thất bại, sai tên hoặc mật khẩu?")
            
        if ".ASPXAUTH" not in session.cookies:
            _log(out_queue, "Đăng nhập thất bại, không nhận được cookie xác thực.", "ERROR")
            raise Exception("Lỗi phiên làm việc, không nhận được cookie.")

        _log(out_queue, "Đăng nhập thành công, đã vào trang Đối tượng.")
        out_queue.put({"type": "login_finished", "payload": {"ok": True, "message": "Đăng nhập thành công."}})
        return True

    except Exception as e:
        _log(out_queue, f"Lỗi trong quá trình đăng nhập: {e}", "ERROR")
        out_queue.put({"type": "login_finished", "payload": {"ok": False, "message": f"Lỗi: {e}"}})
        return False

def _perform_relogin(out_queue, session, username, password):
    """
    Thực hiện đăng nhập lại. 
    Với requests.Session, chúng ta chỉ cần xóa cookie và gọi lại login.
    """
    _log(out_queue, "Thực hiện Logout (xóa cookies) - Login theo yêu cầu...")
    session.cookies.clear() # Xóa sạch cookie của phiên cũ
    
    if _perform_login(out_queue, session, username, password):
        out_queue.put({"type": "relogin_finished", "payload": {"ok": True}})
    else:
        out_queue.put({"type": "relogin_finished", "payload": {"ok": False, "message": "Đăng nhập lại thất bại."}})

def _perform_search(out_queue, session, phone):
    """Thực hiện tìm kiếm SĐT (phiên bản requests)."""
    subjects = []
    try:
        if ".ASPXAUTH" not in session.cookies:
            raise Exception("Chưa đăng nhập (thiếu cookie .ASPXAUTH).")

        _log(out_queue, f"Đang tìm kiếm SĐT (GET): {phone}...")
        
        search_params = {
            'Length': 5, 'LoaiDiaChi': 0, 'VungMienId': '-Khu vực-',
            'ThonApId': '-Thôn/Ấp-', 'NgaySinhTu': '', 'NgaySinhToi': '',
            'GioiTinh': -1, 'LuaTuoi': -1, 'MaDoiTuong': '', 'TenDoiTuong': '',
            'TenMe': '', 'TenBo': '', 'MaDinhDanh': '', 'SoDienThoai': phone,
            'TenNguoiGiamHo': '', 'TinhTrangTheoDoi': -1, 'TinhTrangMangThai': -1,
            'PageNumber': 1, 'PageSize': 20, 'CurrentSystemDate': '',
            'X-Requested-With': 'XMLHttpRequest'
        }
        
        ajax_headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': INDEX_URL
        }

        try:
            response = session.get(
                SEARCH_URL,
                params=search_params,
                headers=ajax_headers,
                timeout=FORM_TIMEOUT
            )
            response.raise_for_status()
        except requests.RequestException as e:
            _log(out_queue, f"Lỗi (GET) khi tìm kiếm: {e}", "ERROR")
            raise Exception("Request tìm kiếm thất bại.")
        
        # Kiểm tra xem có bị trả về trang Login không
        if _is_login_page(response.text):
            _log(out_queue, "Phiên làm việc có thể đã hết hạn (nhận được trang login).", "WARNING")
            raise Exception("Chưa đăng nhập (phiên hết hạn).")

        subjects = _extract_subjects_from_html(out_queue, response.text)

    except Exception as e:
        _log(out_queue, f"Lỗi trong quá trình tìm kiếm SĐT: {e}", "ERROR")
        if "Chưa đăng nhập" in str(e):
             out_queue.put({"type": "session_expired"}) 
    finally:
        # Chỉ gửi 'search_finished' nếu không có lỗi 'Chưa đăng nhập'
        if "Chưa đăng nhập" not in str(locals().get('e', '')):
            out_queue.put({"type": "search_finished", "payload": subjects})

def _perform_load_vaccines(out_queue, session, doi_tuong_id):
    """Tải lịch sử tiêm (phiên bản requests)."""
    vaccines = []
    try:
        if ".ASPXAUTH" not in session.cookies:
            raise Exception("Chưa đăng nhập (thiếu cookie .ASPXAUTH).")

        _log(out_queue, f"Bắt đầu tải lịch sử cho ID: {doi_tuong_id}")
        
        detail_params = {'doiTuongId': doi_tuong_id}
        ajax_headers = {'X-Requested-With': 'XMLHttpRequest', 'Referer': INDEX_URL}
        
        try:
            response = session.get(
                DETAIL_URL,
                params=detail_params,
                headers=ajax_headers,
                timeout=FORM_TIMEOUT
            )
            response.raise_for_status()
        except requests.RequestException as e:
            _log(out_queue, f"Lỗi (GET) khi tải chi tiết: {e}", "ERROR")
            raise Exception("Request tải chi tiết thất bại.")

        # Kiểm tra xem có bị trả về trang Login không
        if _is_login_page(response.text):
            _log(out_queue, "Phiên làm việc có thể đã hết hạn (nhận được trang login).", "WARNING")
            raise Exception("Chưa đăng nhập (phiên hết hạn).")

        vaccines = _extract_vaccines_from_html(out_queue, response.text)

    except Exception as e:
        _log(out_queue, f"Lỗi khi tải lịch sử tiêm: {e}", "ERROR")
        if "Chưa đăng nhập" in str(e):
             out_queue.put({"type": "session_expired"})
    finally:
        # Chỉ gửi 'vaccines_loaded' nếu không có lỗi 'Chưa đăng nhập'
        if "Chưa đăng nhập" not in str(locals().get('e', '')):
            out_queue.put({"type": "vaccines_loaded", "payload": vaccines})

def _perform_add_vaccine(out_queue, session, payload):
    """Thực hiện thêm mới mũi tiêm (phiên bản requests)."""
    try:
        if ".ASPXAUTH" not in session.cookies:
            raise Exception("Chưa đăng nhập (thiếu cookie .ASPXAUTH).")

        doi_tuong_id = payload.get('DOI_TUONG_ID')
        vacxin_id = payload.get('VACXIN_ID')
        ngay_tiem = payload.get('NGAY_TIEM')

        _log(out_queue, f"Đang thêm mũi tiêm (POST) cho ID: {doi_tuong_id}, VX_ID: {vacxin_id}...")

        form_data = {
            'VACXIN_ID': vacxin_id, 'TRANG_THAI_MUI_TIEM': '2', 'SO_MUI_UV': '',
            'NGAY_TIEM': ngay_tiem, 'CO_SO_ID': DEFAULT_CO_SO_ID,
            'DOI_TUONG_ID': doi_tuong_id, 'FORCE_SAVE': '0'
        }
        ajax_headers = {
            'X-Requested-With': 'XMLHttpRequest', 'Referer': INDEX_URL,
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        }
        
        try:
            response = session.post(
                ADD_VACCINE_URL,
                data=form_data, 
                headers=ajax_headers,
                timeout=FORM_TIMEOUT
            )
            response.raise_for_status()
        except requests.RequestException as e:
            _log(out_queue, f"Lỗi (POST) khi thêm mũi tiêm: {e}", "ERROR")
            raise Exception("Request thêm mũi tiêm thất bại.")
        
        try:
            json_response = response.json()
            if json_response.get("Status") == 1:
                _log(out_queue, f"Thêm thành công! Đang tự động tải lại lịch sử tiêm...")
                _perform_load_vaccines(out_queue, session, doi_tuong_id)
            else:
                error_msg = json_response.get("Message", "Lỗi không xác định từ máy chủ.")
                _log(out_queue, f"Máy chủ báo lỗi: {error_msg}", "ERROR")
                out_queue.put({"type": "add_vaccine_failed", "payload": {"message": error_msg}})
        except Exception as e:
            # Kiểm tra xem có bị trả về trang Login không
            if _is_login_page(response.text):
                _log(out_queue, "Phiên làm việc có thể đã hết hạn (nhận được trang login).", "WARNING")
                raise Exception("Chưa đăng nhập (phiên hết hạn).")
            
            _log(out_queue, f"Lỗi khi đọc JSON phản hồi: {e}. Phản hồi thô: {response.text}", "ERROR")
            raise Exception("Phản hồi không phải JSON.")

    except Exception as e:
        _log(out_queue, f"Lỗi trong quá trình thêm vắc-xin: {e}", "ERROR")
        if "Chưa đăng nhập" in str(e):
             out_queue.put({"type": "session_expired"})
        else:
            out_queue.put({"type": "add_vaccine_failed", "payload": {"message": str(e)}})

def _perform_ping(out_queue, session):
    """Gửi request nhẹ để giữ phiên làm việc không bị timeout."""
    try:
        # Chỉ ping nếu đang có cookie đăng nhập
        if ".ASPXAUTH" in session.cookies:
            # Gọi trang Index (rất nhẹ) để server gia hạn session
            session.get(INDEX_URL, timeout=10)
            # (Tùy chọn) Ghi log để debug nếu cần
            # _log(out_queue, "Đã gửi Ping giữ kết nối.", "INFO") 
    except Exception:
        pass # Lỗi ping thì bỏ qua, không cần báo người dùng

def playwright_process_worker(in_queue, out_queue):
    """
    Hàm chính cho tiến trình worker (ĐÃ VIẾT LẠI BẰNG REQUESTS).
    """
    global WORKER_USERNAME, WORKER_PASSWORD
    
    _log(out_queue, "Tiến trình Requests đã khởi động.")
    
    try:
        with requests.Session() as session:
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0'
            })
            
            _log(out_queue, "Session đã sẵn sàng.")
            out_queue.put({"type": "log", "payload": "Trình duyệt (giả mạo) đã sẵn sàng."})

            while True:
                task = in_queue.get() 
                if task is None:
                    break
                
                task_type = task.get("type")
                payload = task.get("payload")

                try:
                    if task_type == "login":
                        WORKER_USERNAME = payload.get("username")
                        WORKER_PASSWORD = payload.get("password")
                        _perform_login(out_queue, session, **payload)
                    
                    elif task_type == "search_phone":
                        _perform_search(out_queue, session, **payload)
                    
                    elif task_type == "get_vaccines":
                        _perform_load_vaccines(out_queue, session, **payload)
                    
                    elif task_type == "relogin":
                        _perform_relogin(out_queue, session, WORKER_USERNAME, WORKER_PASSWORD)
                    
                    elif task_type == "add_vaccine":
                        _perform_add_vaccine(out_queue, session, payload)
                        
                    elif task_type == "ping":
                        _perform_ping(out_queue, session)
                
                except Exception as e:
                    _log(out_queue, f"Lỗi khi thực thi tác vụ '{task_type}': {e}", "ERROR")
                    out_queue.put({"type": f"{task_type}_finished", "payload": {"ok": False, "message": str(e)}})

    except Exception as e:
        _log(out_queue, f"Lỗi nghiêm trọng trong tiến trình worker: {e}", "ERROR")
    finally:
        _log(out_queue, "Tiến trình Requests đã đóng.")