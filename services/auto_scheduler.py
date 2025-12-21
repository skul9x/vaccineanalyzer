# [DEPRECATED] This file is no longer used in V4.5 Pro.
# The legacy PyAutoGUI automation logic has been replaced by direct SQL Server integration via VaccineService.
# This file is kept as a placeholder to prevent import errors in legacy references (if any exist).

class AutomationService:
    @staticmethod
    def is_available():
        return False

    @staticmethod
    def execute_schedule(vaccine_description, date_str):
        raise NotImplementedError("Legacy automation is removed. Use F10 (DB scheduling).")