import os
import sys
import random

import cv2
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (QApplication, QComboBox, QGroupBox, QProgressBar, QSlider,
                               QHBoxLayout, QLabel, QMainWindow, QPushButton, QCheckBox, 
                               QSizePolicy, QVBoxLayout, QWidget, QStackedWidget)

from gui.img_processing import process_img

class Emotions_page(QWidget):
    
    def __init__(self):
        QWidget.__init__(self)
        
        #right vertical layout
        self.left_vertical_layout = QVBoxLayout()
        
        #video widget with placeholder
        self.placeholder = process_img(cv2.imread("Resources/placeholder.jpg"))               
        self.videoLabel = QLabel()
        self.videoLabel.setFixedSize(640, 480)
        self.videoLabel.setPixmap(QPixmap.fromImage(self.placeholder))
        
        #position slider
        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setEnabled(False)
        
        #info labels
        self.path_label = QLabel("Видео не выбрано")
        self.status_label = QLabel("Для продолжения работы запишите или выберите ввидео")
        
        #buttons under video
        self.loadButton = QPushButton("load video")
        self.processButton = QPushButton("process video")
        self.button3 = QPushButton("cry about it")
        
        #build left vertical layout
        self.left_vertical_layout.addWidget(self.videoLabel)
        self.left_vertical_layout.addWidget(self.positionSlider)
        self.left_vertical_layout.addWidget(self.path_label)
        self.left_vertical_layout.addWidget(self.status_label)
        self.left_vertical_layout.addWidget(self.loadButton)
        self.left_vertical_layout.addWidget(self.processButton)
        self.left_vertical_layout.addWidget(self.button3)
        
        #group model of emotions progress bars
        self.emotions_group_model = QGroupBox("Emotions")
        self.emotions_group_model.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        
        self.emotions_group_model_layout = QVBoxLayout()
        
        self.emotions_progress_bars = []
        self.emotions_labels = []
        for i in range(8):
            self.emotions_labels.append(QLabel("emotion "+str(i)))
            self.emotions_progress_bars.append(QProgressBar())
            layout = QHBoxLayout()
            layout.addWidget(self.emotions_labels[i])
            layout.addWidget(self.emotions_progress_bars[i])
            self.emotions_group_model_layout.addLayout(layout)
        
        self.emotions_group_model.setLayout(self.emotions_group_model_layout)
        
        #group model of movment progress bars
        self.movement_group_model = QGroupBox("Movement")
        self.movement_group_model.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.horizontal_movement_group_model_layout = QHBoxLayout()
        
        self.left_movement_group_model_layout = QVBoxLayout()
        self.right_movement_group_model_layout = QVBoxLayout()
        
        self.movement_progress_bars = []
        self.movement_labels = []
        for i in range(12):
            self.movement_labels.append(QLabel("mov "+str(i)))
            self.movement_progress_bars.append(QProgressBar())
            layout = QHBoxLayout()
            layout.addWidget(self.movement_labels[i])
            layout.addWidget(self.movement_progress_bars[i])
            if i<6:
                self.left_movement_group_model_layout.addLayout(layout)
            else:
                self.right_movement_group_model_layout.addLayout(layout)
        
        self.horizontal_movement_group_model_layout.addLayout(self.left_movement_group_model_layout)
        self.horizontal_movement_group_model_layout.addLayout(self.right_movement_group_model_layout)
        self.movement_group_model.setLayout(self.horizontal_movement_group_model_layout)
        
        #group model of movement checkboxes
        self.checkbox_group_model = QGroupBox("checkbox")
        self.checkbox_group_model.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.horizontal_checkbox_group_model_layout = QHBoxLayout()
        
        self.left_checkbox_group_model_layout = QVBoxLayout()
        self.right_checkbox_group_model_layout = QVBoxLayout()
        
        self.checkbox_progress_bars = []
        self.checkbox_labels = []
        for i in range(12):
            self.checkbox_progress_bars.append(QCheckBox())
            self.checkbox_labels.append(QLabel('movement ' + str(i)))
            layout = QHBoxLayout()
            layout.addWidget(self.checkbox_labels[i])
            layout.addWidget(self.checkbox_progress_bars[i])
            if i < 6:
                self.left_checkbox_group_model_layout.addLayout(layout)
            else:
                self.right_checkbox_group_model_layout.addLayout(layout)
        
        self.horizontal_checkbox_group_model_layout.addLayout(self.left_checkbox_group_model_layout)
        self.horizontal_checkbox_group_model_layout.addLayout(self.right_checkbox_group_model_layout)
        self.checkbox_group_model.setLayout(self.horizontal_checkbox_group_model_layout)
        
        #right vertical layout
        self.right_vertical_layout = QVBoxLayout()
        self.right_vertical_layout.addWidget(self.emotions_group_model)
        self.right_vertical_layout.addWidget(self.movement_group_model)
        self.right_vertical_layout.addWidget(self.checkbox_group_model)
        
        #main horizontal layout
        self.horizontal_layout = QHBoxLayout()
        
        self.horizontal_layout.addLayout(self.left_vertical_layout)
        self.horizontal_layout.addLayout(self.right_vertical_layout)
        
        self.setLayout(self.horizontal_layout)
        
        
if __name__ == "__main__":

    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    widget = Emotions_page()
    widget.resize(800, 400)
    
    widget.show()

    sys.exit(app.exec())