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
from Frame_handler.FrameHandlerMimic import FrameHandlerMimic
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
        
        #input for file name
        self.inputLine = QLineEdit()
        self.inputLine.setPlaceholderText("Введите название файла")
        
        #left vertical layout
        self.left_vertical_layout = QVBoxLayout()
        self.left_vertical_layout.addWidget(self.videoLabel)
        self.left_vertical_layout.addWidget(self.inputLine)
        
        #info text label
        self.label = QLabel("приложение напомнит вам,\n"
                            "что что-то не так (если не сдохнет),\n"
                            "если не дождаться возвращения плейсхолдера\n"
                            "после окончания записи видео\n\n"
                            "я пока думаю над решением")
        #self.label.setFixedSize(640, 640)
        self.label.setAlignment(Qt.AlignCenter)
        
        #registrate buttons
        self.start_registration_button = QPushButton("начать запись")
        self.stop_registration_button = QPushButton("закончить запись")

        #right vertical layout
        self.right_vertical_layout = QVBoxLayout()
        self.right_vertical_layout.addWidget(self.label)
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

        print('reg stoped')
             
        self.th.cap.release()
        cv2.destroyAllWindows()
        
        self.current_video = self.th.video.copy()
        
        self.stop_registration_button.setEnabled(False)
        self.start_registration_button.setEnabled(False)    
                     
        #self.th.terminate()
        
        self.videoLabel.setPixmap(QPixmap.fromImage(self.placeholder))
        # Give time for the thread to finish
        #time.sleep(1)

    @Slot()
    def start(self):
        #init thread
        self.th = Thread(self)
        self.th.updateFrame.connect(self.setImage)
        
        self.stop_registration_button.setEnabled(True)
        self.start_registration_button.setEnabled(False)
        self.th.setCurrentFileName(self.current_file_name)
        self.th.start()

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