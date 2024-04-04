import os
import sys
import random

from PySide6.QtGui import QFontDatabase

from PySide6.QtCore import Qt, Slot, QSize

from PySide6.QtWidgets import (QApplication, QComboBox, QGroupBox, QSpacerItem,
                               QHBoxLayout, QLabel, QMainWindow, QPushButton,
                               QSizePolicy, QVBoxLayout, QWidget, QStackedWidget)


class Main_menu(QWidget):
    
    def __init__(self):
        QWidget.__init__(self)
        
        self.horintal_layout = QHBoxLayout()
        
        self.video_button = QPushButton("Видео")
        self.hrv_button = QPushButton("ВСР")
        self.emotions_button = QPushButton("Эмоции")
                
        self.video_button.setEnabled(False)
        
        self.video_button.setStyleSheet("font-family : ALS Sector;" 
                                        "font: bold;"
                                        "background-color : #006cdc;"  
                                        "color : black;"
                                        "min-height: 2em;"
                                        "border-radius: 5px")
        self.hrv_button.setStyleSheet("font-family : ALS Sector;"
                                      "font: bold;"
                                      "background-color : #00b8ff;"
                                        "min-height: 2em;"
                                        "border-radius: 5px")
        self.emotions_button.setStyleSheet("font-family : ALS Sector;"
                                           "font: bold;"
                                           "background-color : #00b8ff;"
                                        "min-height: 2em;"
                                        "border-radius: 5px")

        
        self.horintal_layout.addWidget(self.video_button)
        self.horintal_layout.addWidget(self.hrv_button)
        self.horintal_layout.addWidget(self.emotions_button)
        
        self.spacer = QSpacerItem(1, 1)
        
        self.horintal_layout.addSpacerItem(self.spacer)
        
        self.setLayout(self.horintal_layout)
        
    def resizeEvent(self, event):
        self.spacer.changeSize(self.size().width()*0.66, 1)
        # self.video_button.setGeometry(self.size().width()*0.01, self.size().height()*0.1, 
        #                               self.size().width()*0.12, self.size().height()*0.8)
        QMainWindow.resizeEvent(self, event)
        
if __name__ == "__main__":

    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    widget = Main_menu()
    widget.resize(800, 400)
    
    widget.show()

    sys.exit(app.exec())