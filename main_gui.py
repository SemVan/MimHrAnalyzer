import os
import sys
import multiprocessing as mp

from PySide6.QtWidgets import QApplication

from gui.main_window import MainWindow


if __name__ == "__main__":
    mp.freeze_support()

    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    widget = MainWindow()
    
    widget.show()

    sys.exit(app.exec())
