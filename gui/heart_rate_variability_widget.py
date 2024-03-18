import os
import sys

import pyqtgraph as pg
import cv2
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QAction, QImage, QKeySequence, QPixmap, QResizeEvent
from PySide6.QtWidgets import (QApplication, QComboBox, QGroupBox, QSlider,
                               QHBoxLayout, QLabel, QMainWindow, QPushButton,
                               QSizePolicy, QVBoxLayout, QWidget,
                               QStackedWidget, QFileDialog)

from gui.img_processing import process_img

class Heart_rate_variability_page(QWidget):
    
    def __init__(self):
        QWidget.__init__(self)
        
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
        
        self.right_vertical_layout = QVBoxLayout()
        
        self.plot_widget_1 = pg.PlotWidget()
        self.plot_widget_2 = pg.PlotWidget()
        self.plot_widget_3 = pg.PlotWidget()
        
        self.right_vertical_layout.addWidget(self.plot_widget_1)
        self.right_vertical_layout.addWidget(self.plot_widget_2)
        self.right_vertical_layout.addWidget(self.plot_widget_3)
        
        self.horizontal_layout = QHBoxLayout()
        
        self.horizontal_layout.addLayout(self.left_vertical_layout)
        self.horizontal_layout.addLayout(self.right_vertical_layout)
        
        self.setLayout(self.horizontal_layout)
        
        #
        #self.loadButton.clicked.connect(self.open_video)
     
    @Slot()
    def open_video(self):
        filename, filter = self.dialog.getOpenFileName(caption='Open file', dir='.', filter='*.avi')
        
    @Slot()
    def process_video(self):
        pass
        
    def setPosition(self, position):
        print(position)
        
 
if __name__ == "__main__":

    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    widget = Heart_rate_variability_page()
    widget.resize(800, 400)
    
    widget.show()

    sys.exit(app.exec())