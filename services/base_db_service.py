from database.db_connection import DbConnection

class BaseDbService:
    def __init__(self, logger_callback=None):
        self.logger = logger_callback

    def log(self, message):
        if self.logger:
            self.logger(message)
        else:
            print(f"[DB-LOG] {message}")

    def get_connection(self):
        return DbConnection.get_connection()