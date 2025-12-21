import sys
import os
import multiprocessing
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, qInstallMessageHandler
from ui_pyside.main_window import MainWindow
from ui_pyside.splash_screen import SplashScreenManager
# Update import to use the new package structure
from controllers.main_controller import MainController

def qt_message_handler(mode, context, message):
    if "SetProcessDpiAwarenessContext() failed" in message: return

def main():
    qInstallMessageHandler(qt_message_handler)
    os.environ["QT_QPA_PLATFORM"] = "windows:darkmode=2"
    try: QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    except Exception: pass
    multiprocessing.freeze_support()
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Use splash screen manager to handle startup
    splash_manager = SplashScreenManager(MainWindow, MainController)
    splash_manager.start()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
