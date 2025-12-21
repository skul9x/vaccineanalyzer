"""
Hằng số ứng dụng TiemChung
"""
from pathlib import Path

# URLs
LOGIN_URL = "https://tiemchung.vncdc.gov.vn/Account/Login"
INDEX_URL = "https://tiemchung.vncdc.gov.vn/TiemChung/DoiTuong/Index"
# --- THÊM MỚI: URL cho các nghiệp vụ ---
SEARCH_URL = "https://tiemchung.vncdc.gov.vn/TiemChung/DoiTuong/TimKiem"
DETAIL_URL = "https://tiemchung.vncdc.gov.vn/TiemChung/DoiTuong/Detail"
# <<< THÊM MỚI (START) >>>
ADD_VACCINE_URL = "https://tiemchung.vncdc.gov.vn/TiemChung/DoiTuong/ThemNhanhMuiTiem"
# (Mặc dù chúng ta đã lưu JSON, nhưng vẫn nên giữ URL này cho việc cập nhật sau này)
VACCINE_LIST_URL = "https://tiemchung.vncdc.gov.vn/Vacxin/DsVacxinKhongCovid" 
# <<< THÊM MỚI (END) >>>


# Tệp cấu hình
CONFIG_FILE = Path("config.txt")
LOG_FILE = Path(__file__).parent.parent / "tiemchung_gui.log"
USER_INTERACTION_LOG = Path(__file__).parent.parent / "user_interaction.log" # (Có thể xóa nếu muốn)

# Cấu hình retry
MAX_RETRIES = 3
RETRY_DELAY = 5  # giây

# Timeout (dùng cho requests)
LOGIN_TIMEOUT = 60  # giây (Đổi sang giây cho requests)
FORM_TIMEOUT = 30   # giây (Đổi sang giây cho requests)

# --- XÓA CÁC TIMEOUT CỦA PLAYWRIGHT ---
# REDIRECT_TIMEOUT = 15000
# TABLE_TIMEOUT = 15000
# POPUP_TIMEOUT = 3000