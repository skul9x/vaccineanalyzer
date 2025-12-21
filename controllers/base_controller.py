from PySide6.QtCore import QObject

class BaseController(QObject):
    def __init__(self, main_controller):
        super().__init__()
        self.main = main_controller
        self.view = main_controller.view
    
    @property
    def services(self):
        return self.main.services
    
    @property
    def state(self):
        return self.main.state