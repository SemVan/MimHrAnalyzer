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
        
        self.current_mimic = 0
        
        #right vertical layout
        self.left_vertical_layout = QVBoxLayout()
        
        #video widget with placeholder
        self.placeholder = process_img(cv2.imread("Resources/placeholder.jpg"))               
        self.videoLabel = QLabel()
        self.videoLabel.setFixedSize(640, 480)
        self.videoLabel.setPixmap(QPixmap.fromImage(self.placeholder))
        self.videoLabel.setAlignment(Qt.AlignCenter)
        
        #position slider
        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setEnabled(False)
        
        #info labels
        self.path_label = QLabel("Видео не выбрано")
        self.path_label.setStyleSheet("font-family : ALS Sector;" 
                                      "color : black;")
        self.status_label = QLabel("Для продолжения работы запишите или выберите ввидео")
        self.status_label.setStyleSheet("font-family : ALS Sector;" 
                                      "color : black;")
        
        #buttons under video
        self.loadButton = QPushButton("Загрузить видео")
        self.loadButton.setStyleSheet("font-family : ALS Sector;" 
                                      "color : black;")
        
        #build left vertical layout
        self.left_vertical_layout.addWidget(self.videoLabel)
        self.left_vertical_layout.addWidget(self.positionSlider)
        self.left_vertical_layout.addWidget(self.path_label)
        self.left_vertical_layout.addWidget(self.status_label)
        self.left_vertical_layout.addWidget(self.loadButton)
        
        #group model of emotions progress bars
        self.emotions_group_model = QGroupBox("Эмоции/состояние")
        self.emotions_group_model.setStyleSheet("font-family : ALS Sector;" 
                                                "font: bold;"
                                                "color : black;")
        self.emotions_group_model.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        
        self.emotions_group_model_layout = QVBoxLayout()

        self.expression_names = ['Нейтральное', 'Радость', 'Грусть', 'Удивление',
                                 'Страх', 'Отвращение', 'Злость', 'Презрение']
        
        self.emotions_progress_bars = []
        self.emotions_labels = []
        for i in range(8):
            self.emotions_labels.append(QLabel(self.expression_names[i]))
            self.emotions_labels[i].setFixedWidth(90)
            self.emotions_labels[i].setAlignment(Qt.AlignCenter)
            self.emotions_labels[i].setStyleSheet("font-family : ALS Sector;" 
                                                  "font: normal;"
                                                  "color : black;")
            self.emotions_progress_bars.append(QProgressBar())
            layout = QHBoxLayout()
            layout.addWidget(self.emotions_labels[i])
            layout.addWidget(self.emotions_progress_bars[i])
            self.emotions_progress_bars[i].setMaximum(1000)
            self.emotions_group_model_layout.addLayout(layout)
        
        self.emotions_group_model.setLayout(self.emotions_group_model_layout)
        
        #group model of movment progress bars
        self.movement_group_model = QGroupBox("Интенсивность двигательных единиц")
        self.movement_group_model.setStyleSheet("font-family : ALS Sector;" 
                                                "font: bold;"
                                                "color : black;")
        self.movement_group_model.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.horizontal_movement_group_model_layout = QHBoxLayout()

        self.intensity_au_names = ['1', '2', '4', '5', '6', '9', '12', '15', '17', '20', '25', '26']
        
        self.left_movement_group_model_layout = QVBoxLayout()
        self.right_movement_group_model_layout = QVBoxLayout()
        
        self.movement_progress_bars = []
        self.movement_labels = []
        for i in range(12):
            self.movement_labels.append(QLabel("ДЕ "+self.intensity_au_names[i]))
            self.movement_labels[i].setFixedWidth(40)
            self.movement_labels[i].setAlignment(Qt.AlignCenter)
            self.movement_labels[i].setStyleSheet("font-family : ALS Sector;" 
                                                  "font: normal;"
                                                  "color : black;")
            self.movement_progress_bars.append(QProgressBar())
            layout = QHBoxLayout()
            layout.addWidget(self.movement_labels[i])
            layout.addWidget(self.movement_progress_bars[i])
            self.movement_progress_bars[i].setMaximum(1000)
            if i<6:
                self.left_movement_group_model_layout.addLayout(layout)
            else:
                self.right_movement_group_model_layout.addLayout(layout)
        
        self.horizontal_movement_group_model_layout.addLayout(self.left_movement_group_model_layout)
        self.horizontal_movement_group_model_layout.addLayout(self.right_movement_group_model_layout)
        self.movement_group_model.setLayout(self.horizontal_movement_group_model_layout)
        
        #group model of movement checkboxes
        self.checkbox_group_model = QGroupBox("Наличие двигательных единиц")
        self.checkbox_group_model.setStyleSheet("font-family : ALS Sector;" 
                                                "font: bold;"
                                                "color : black;")
        self.checkbox_group_model.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.horizontal_checkbox_group_model_layout = QHBoxLayout()
        
        self.left_checkbox_group_model_layout = QVBoxLayout()
        self.right_checkbox_group_model_layout = QVBoxLayout()

        self.presence_au_names = ['1', '2', '4', '6', '7', '10', '12', '14', '15', '17', '23', '24']
        
        self.checkbox_progress_bars = []
        self.checkbox_labels = []
        for i in range(12):
            self.checkbox_progress_bars.append(QCheckBox())
            self.checkbox_labels.append(QLabel('ДЕ ' + self.presence_au_names[i]))
            self.checkbox_labels[i].setFixedWidth(150)
            self.checkbox_labels[i].setAlignment(Qt.AlignCenter)
            self.checkbox_labels[i].setStyleSheet("font-family : ALS Sector;" 
                                                  "font: normal;"
                                                  "color : black;")
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
        
    def updateMimic(self, mimic):
        
        self.current_mimic = mimic
        if self.current_mimic['pred_au_intensity']:
            for i in range(12):
                self.movement_progress_bars[i].setValue(int(1000*self.current_mimic['pred_au_intensity'][i]))
                
        if self.current_mimic['pred_expression']:
            for i in range(8):
                self.emotions_progress_bars[i].setValue(int(1000*self.current_mimic['pred_expression'][i]))
                
        if self.current_mimic['pred_au_presence']:
            for i in range(12):
                self.checkbox_progress_bars[i].setChecked(self.current_mimic['pred_au_presence'][i])
        
        
        
if __name__ == "__main__":

    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    widget = Emotions_page()
    widget.resize(800, 400)
    
    widget.show()

    sys.exit(app.exec())