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

class Thread(QThread):
    updateFrame = Signal(QImage)

    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.status = True
        self.cap = True
        self.path = 'Data/'
        self.current_file_name = 'temp.avi'

    def run(self):
        self.cap = cv2.VideoCapture(0)
        
        # frame_width = int(self.cap.get(3))
        # frame_height = int(self.cap.get(4))
        path = os.path.join(self.path, self.current_file_name)
        print(path)
        #video = cv2.VideoWriter(path, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), self.fps, (frame_width, frame_height))
        
        while self.status:
            ret, frame = self.cap.read()
            if not ret:
                continue

            scaled_img = process_img(frame)

            # Emit signal
            self.updateFrame.emit(scaled_img)
        sys.exit(-1)
        
    def setCurrentFileName(self, current_name):
        if current_name:
            self.current_file_name = current_name  + '.avi'

class Video_capture_page(QWidget):
    
    def __init__(self):
        QWidget.__init__(self)
        
        #init variables
        self.current_file_name = ''
        
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
        self.label = QLabel("здесь пока нет никакого текста")
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
        
        self.setLayout(self.horizontal_layout)
        
        #init thread
        self.th = Thread(self)
        
        #connections
        self.start_registration_button.clicked.connect(self.start)
        self.stop_registration_button.clicked.connect(self.kill_thread)
        self.stop_registration_button.setEnabled(False)
        self.th.updateFrame.connect(self.setImage)
        self.inputLine.editingFinished.connect(self.set_file_name)

    @Slot()
    def kill_thread(self):
        print("Finishing...")
        self.status = False
        self.th.cap.release()
        cv2.destroyAllWindows()  
        self.videoLabel.setPixmap(QPixmap.fromImage(self.placeholder)) 
        self.stop_registration_button.setEnabled(False)
        self.start_registration_button.setEnabled(True)                         
        self.th.terminate()
        # Give time for the thread to finish
        time.sleep(1)

    @Slot()
    def start(self):
        print("Starting...")
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
        #print(self.current_file_name)
        
        
if __name__ == "__main__":

    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    widget = Video_capture_page()
    widget.resize(800, 400)
    
    widget.show()

    sys.exit(app.exec())