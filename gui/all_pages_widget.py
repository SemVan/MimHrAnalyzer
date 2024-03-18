import os
import sys
import random

from PySide6.QtCore import Qt, Slot

from PySide6.QtWidgets import (QApplication, QComboBox, QGroupBox,
                               QHBoxLayout, QLabel, QMainWindow, QPushButton,
                               QSizePolicy, QVBoxLayout, QWidget, QStackedWidget)

from gui.video_capture_widget import Video_capture_page
from gui.heart_rate_variability_widget import Heart_rate_variability_page     
from gui.emotions_widget import Emotions_page

class All_pages(QStackedWidget):
    
    def __init__(self):
        QStackedWidget.__init__(self)
        
        self.video_capture_page = Video_capture_page()
        self.heart_rate_variability_page = Heart_rate_variability_page()
        self.emotions_page = Emotions_page()
        
        self.addWidget(self.video_capture_page)
        self.addWidget(self.heart_rate_variability_page)
        self.addWidget(self.emotions_page)
        
    def resizeEvent(self, event):
        # self.video_capture_page.setGeometry(0, 0, self.size().width(), self.size().height())
        # print("all pages resized", self.size())
        QMainWindow.resizeEvent(self, event)
        
if __name__ == "__main__":

    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    widget = All_pages()
    widget.resize(800, 400)
    
    widget.show()

    sys.exit(app.exec())