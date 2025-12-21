"""
Quản lý cấu hình ứng dụng
"""
from pathlib import Path
from .logger_config import get_logger

logger = get_logger()


class ConfigManager:
    """Quản lý tệp cấu hình ứng dụng"""
    
    def __init__(self, config_file: Path):
        self.config_file = config_file
        self.config = {
            'username': '',
            'password': ''
        }
    
    def load(self) -> dict:
        """Tải cấu hình từ tệp"""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    for line in lines:
                        line = line.strip()
                        if line.startswith("username="):
                            self.config['username'] = line.split("=", 1)[1]
                        elif line.startswith("password="):
                            self.config['password'] = line.split("=", 1)[1]
                logger.info(f"Đã tải cấu hình từ {self.config_file}")
            except Exception as e:
                logger.error(f"Lỗi khi đọc config file: {e}")
        return self.config
    
    def save(self, username: str, password: str):
        """Lưu cấu hình vào tệp"""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                f.write(f"username={username}\n")
                f.write(f"password={password}\n")
            logger.info("Đã lưu cấu hình.")
        except Exception as e:
            logger.error(f"Lỗi khi lưu config file: {e}")
    
    def get(self, key: str, default: str = "") -> str:
        """Lấy giá trị cấu hình"""
        return self.config.get(key, default)