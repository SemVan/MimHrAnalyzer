import os
import sys

from PySide6.QtWidgets import QApplication

from gui.main_window import MainWindow

if __name__ == "__main__":

    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    widget = MainWindow()
    
    widget.show()

    sys.exit(app.exec())