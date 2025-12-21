import pyodbc
from db_config import DB_CONFIG

class DbConnection:
    @staticmethod
    def get_connection():
        conn_str = (
            f"DRIVER={DB_CONFIG['DRIVER']};"
            f"SERVER={DB_CONFIG['SERVER']};"
            f"DATABASE={DB_CONFIG['DATABASE']};"
            f"UID={DB_CONFIG['UID']};"
            f"PWD={DB_CONFIG['PWD']};"
        )
        return pyodbc.connect(conn_str)