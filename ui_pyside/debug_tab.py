from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QPlainTextEdit

class DebugTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        self.generate_btn = QPushButton("📊 Tạo báo cáo & Copy vào Clipboard")
        
        self.log_viewer = QPlainTextEdit()
        self.log_viewer.setReadOnly(True)
        self.log_viewer.setStyleSheet("font-family: Consolas, Monospace; font-size: 10pt;")
        
        layout.addWidget(self.generate_btn)
        layout.addWidget(self.log_viewer)