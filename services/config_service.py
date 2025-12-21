import os
import sys

class ConfigService:
    def __init__(self):
        self.config_file = "config.txt"
        self._config_data = {
            "username": "", 
            "password": "",
            "theme": "Dark"
        }
        self.load_config()

    def _get_config_path(self):
        base_path = os.path.dirname(os.path.abspath(sys.argv[0] if hasattr(sys, 'frozen') else __file__))
        return os.path.join(base_path, self.config_file)

    def load_config(self):
        path = self._get_config_path()
        if not os.path.exists(path):
            return self._config_data

        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines:
                    line = line.strip()
                    if "=" in line:
                        key, value = line.split("=", 1)
                        self._config_data[key.strip()] = value.strip()
        except Exception as e:
            print(f"Error loading config: {e}")
        
        return self._config_data

    def save_config_file(self):
        """Writes the current in-memory config dictionary to the file."""
        path = self._get_config_path()
        try:
            with open(path, "w", encoding="utf-8") as f:
                for key, value in self._config_data.items():
                    f.write(f"{key}={value}\n")
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def save_config(self, username, password, theme="Dark"):
        """Updates credentials and theme, then saves to file."""
        self._config_data["username"] = username
        self._config_data["password"] = password
        self._config_data["theme"] = theme
        return self.save_config_file()

    def set_value(self, key, value):
        """Sets a value in the in-memory config (does not write to disk immediately)."""
        self._config_data[key] = str(value)

    def get_value(self, key, default=None):
        """Retrieves a value from the in-memory config."""
        return self._config_data.get(key, default)

    def get_credentials(self):
        return self._config_data