import os
import sys
import time

import cv2

from PySide6.QtCore import Qt, Slot, QThread, Signal
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (QApplication,
                               QHBoxLayout, QLabel, QPushButton,
                               QVBoxLayout, QWidget, QLineEdit)

from gui.img_processing import process_img
from Frame_handler_VPG.FrameHandlerVPG import FrameHandlerVPG
from Frame_handler_Mimic.FrameHandlerMimic import FrameHandlerMimic
from Mimic_Analyzer.MimicAnalyzer import MimicAnalyzer
from gui.thread import Thread

class Video_capture_page(QWidget):
    
    def __init__(self):
        QWidget.__init__(self)
        
        #init variables
        self.current_file_name = ''
        self.vpg = []
        
        #video widget with placeholder
        self.placeholder = process_img(cv2.imread("Resources/placeholder.jpg"))               
        self.videoLabel = QLabel()
        self.videoLabel.setFixedSize(640, 480)
        self.videoLabel.setPixmap(QPixmap.fromImage(self.placeholder))
        self.videoLabel.setAlignment(Qt.AlignCenter)
        
        #input for file name
        self.inputLine = QLineEdit()
        self.inputLine.setPlaceholderText("Введите название файла, под которым будет сохранено видео")
        self.inputLine.setStyleSheet("font-family : ALS Sector;")
        
        #left vertical layout
        self.left_vertical_layout = QVBoxLayout()
        self.left_vertical_layout.addWidget(self.videoLabel)
        self.left_vertical_layout.addWidget(self.inputLine)
        
        #info text label
        self.label = QLabel("Для работы вам необходимо\n"
                            "загрузить видео или записать его\n\n"
                            "Не забудьте назвать видео")
        self.label.setStyleSheet("font-family : ALS Sector;" 
                                 "color : black;")
        self.label.setMinimumWidth(480)
        self.label.setAlignment(Qt.AlignCenter)
        
        #registrate buttons
        self.load_button = QPushButton("Загрузить видео")
        self.load_button.setStyleSheet("font-family : ALS Sector;" 
                                 "color : black;")
        self.start_registration_button = QPushButton("Начать запись")
        self.start_registration_button.setStyleSheet("font-family : ALS Sector;" 
                                 "color : black;")
        self.stop_registration_button = QPushButton("Закончить запись")
        self.stop_registration_button.setStyleSheet("font-family : ALS Sector;" 
                                 "color : black;")

        #right vertical layout
        self.right_vertical_layout = QVBoxLayout()
        self.right_vertical_layout.addWidget(self.label)
        self.right_vertical_layout.addWidget(self.load_button)
        self.right_vertical_layout.addWidget(self.start_registration_button)
        self.right_vertical_layout.addWidget(self.stop_registration_button)
    
        #horizontal layout
        self.horizontal_layout = QHBoxLayout()
        self.horizontal_layout.addLayout(self.left_vertical_layout)
        self.horizontal_layout.addLayout(self.right_vertical_layout)
        
        #main widget layout 
        self.setLayout(self.horizontal_layout)
        
        #connections
        # self.start_registration_button.clicked.connect(self.start)
        self.stop_registration_button.clicked.connect(self.stop_registration)
        self.stop_registration_button.setEnabled(False)
        self.inputLine.editingFinished.connect(self.set_file_name)

    def stop_registration(self):
        #stop registration
        self.th.status = False
             
        self.th.cap.release()
        cv2.destroyAllWindows()
        
        self.current_video = self.th.video.copy()
        
        self.stop_registration_button.setEnabled(False)
        self.start_registration_button.setEnabled(False)    
                     
        #self.th.terminate()
        
        self.videoLabel.setPixmap(QPixmap.fromImage(self.placeholder))
        # Give time for the thread to finish
        #time.sleep(1)

    @Slot(QImage)
    def setImage(self, image):
        self.videoLabel.setPixmap(QPixmap.fromImage(image))
        
    @Slot()
    def set_file_name(self):
        self.current_file_name = self.inputLine.text()
        
        
if __name__ == "__main__":

    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    widget = Video_capture_page()
    widget.resize(800, 400)
    
    widget.show()

    sys.exit(app.exec())