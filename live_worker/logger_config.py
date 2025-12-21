"""
Cấu hình logging cho ứng dụng
"""
import logging
import sys
import traceback
from .constants import LOG_FILE

logger = logging.getLogger("TiemChungApp")


def setup_logging():
    """Cấu hình logging cho ứng dụng"""
    # Xóa file log cũ mỗi khi khởi động
    try:
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            pass  # Xóa nội dung
    except Exception:
        pass
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8"),
        ]
    )
    
    # Custom exception handler để ghi lại các exception chưa xử lý
    def exception_hook(exctype, value, tb):
        logger.error("Uncaught exception: %s", value, exc_info=(exctype, value, tb))
        print("Uncaught exception:", file=sys.stderr)
        traceback.print_exception(exctype, value, tb)
    
    sys.excepthook = exception_hook
    return logger


def get_logger():
    """Lấy logger instance"""
    return logger
