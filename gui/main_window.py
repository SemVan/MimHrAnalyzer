import os
import sys

import cv2, numpy as np
from PySide6.QtCore import Qt, Slot, QSize
from PySide6.QtGui import QScreen, QPixmap
from PySide6.QtWidgets import (QApplication, QComboBox, QGroupBox,
                               QHBoxLayout, QLabel, QMainWindow, QPushButton,
                               QSizePolicy, QVBoxLayout, QWidget, 
                               QStackedWidget, QFileDialog)
#from __feature__ import snake_case, true_property


from gui.all_pages_widget import All_pages
from gui.main_menu_widget import Main_menu
from gui.img_processing import process_img


def read_video(path):
    
    frames = []

    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    while (True):
        ret, frame = cap.read()

        if ret == False:
            cap.release()
            break

        frames.append(frame)

    return np.array(frames), float(fps)
        

        
class MainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        
        #set stylish things
        self.setStyleSheet("background-color : white;")
        self.setWindowTitle("СПО_нейм")
        
        #init file dialog window
        self.dialog = QFileDialog(self)
        self.dialog.setFileMode(QFileDialog.Directory)
        
        #init main menu and pages
        self.main_menu = Main_menu()
        self.all_pages = All_pages()     

        #build certical layout
        self.vertical_layout = QVBoxLayout()
        self.vertical_layout.addWidget(self.main_menu)
        self.vertical_layout.addWidget(self.all_pages)

        #set central widget        
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.vertical_layout)        
        self.setCentralWidget(self.central_widget)
        
        #connections
        self.main_menu.video_button.clicked.connect(self.go_to_video_capture_page)
        self.main_menu.hrv_button.clicked.connect(self.go_to_heart_rate_variability_page)
        self.main_menu.emotions_button.clicked.connect(self.go_to_emotions_page)
        self.all_pages.heart_rate_variability_page.loadButton.clicked.connect(self.open_video)
        self.all_pages.emotions_page.loadButton.clicked.connect(self.open_video)
        self.all_pages.heart_rate_variability_page.positionSlider.sliderMoved.connect(self.setPositionHRV)
        self.all_pages.emotions_page.positionSlider.sliderMoved.connect(self.setPositionEmo)
        
        #init variables
        self.current_video_path = ''
        self.current_video = []
        self.current_video_fps = 0
       
    @Slot()
    def go_to_video_capture_page(self):
        self.all_pages.setCurrentWidget(self.all_pages.video_capture_page)
        
        self.main_menu.video_button.setEnabled(False)
        self.main_menu.hrv_button.setEnabled(True)
        self.main_menu.emotions_button.setEnabled(True)
        
        self.main_menu.video_button.setStyleSheet("background-color : #006cdc; color : black")
        self.main_menu.hrv_button.setStyleSheet("background-color : #00b8ff")
        self.main_menu.emotions_button.setStyleSheet("background-color : #00b8ff")
     
    @Slot()
    def go_to_heart_rate_variability_page(self):
        self.all_pages.setCurrentWidget(self.all_pages.heart_rate_variability_page)
        
        self.main_menu.video_button.setEnabled(True)
        self.main_menu.hrv_button.setEnabled(False)
        self.main_menu.emotions_button.setEnabled(True)
        
        self.main_menu.video_button.setStyleSheet("background-color : #00b8ff")
        self.main_menu.hrv_button.setStyleSheet("background-color : #006cdc; color : black")
        self.main_menu.emotions_button.setStyleSheet("background-color : #00b8ff")
     
    @Slot()
    def go_to_emotions_page(self):
        self.all_pages.setCurrentWidget(self.all_pages.emotions_page)
        
        self.main_menu.video_button.setEnabled(True)
        self.main_menu.hrv_button.setEnabled(True)
        self.main_menu.emotions_button.setEnabled(False)
        
        self.main_menu.video_button.setStyleSheet("background-color : #00b8ff")
        self.main_menu.hrv_button.setStyleSheet("background-color : #00b8ff")
        self.main_menu.emotions_button.setStyleSheet("background-color : #006cdc; color : black")
        
    @Slot()
    def open_video(self):
        filename, filter = self.dialog.getOpenFileName(caption='Open file', dir='.', filter='*.avi')
        
        self.all_pages.heart_rate_variability_page.path_label.setText("Выбран файл " + filename.split("/")[-1].split(".")[0])
        self.all_pages.heart_rate_variability_page.status_label.setText("Видео загружается")
        
        self.all_pages.emotions_page.path_label.setText("Выбран файл " + filename.split("/")[-1].split(".")[0])
        self.all_pages.emotions_page.status_label.setText("Видео загружается")
        
        self.current_video_path = filename
        try: 
            self.current_video, self.current_video_fps = read_video(filename)
            
            self.all_pages.heart_rate_variability_page.status_label.setText("Видео загружено")
            self.all_pages.emotions_page.status_label.setText("Видео загружено")
            
            self.all_pages.heart_rate_variability_page.videoLabel.setPixmap(QPixmap.fromImage(process_img(self.current_video[0])))
            self.all_pages.emotions_page.videoLabel.setPixmap(QPixmap.fromImage(process_img(self.current_video[0])))
            
            self.all_pages.heart_rate_variability_page.positionSlider.setMinimum(0)
            self.all_pages.heart_rate_variability_page.positionSlider.setMaximum(len(self.current_video)-1)
            self.all_pages.heart_rate_variability_page.positionSlider.setSliderPosition(0)
            self.all_pages.heart_rate_variability_page.positionSlider.setEnabled(True)
            
            self.all_pages.emotions_page.positionSlider.setMinimum(0)
            self.all_pages.emotions_page.positionSlider.setMaximum(len(self.current_video)-1)
            self.all_pages.emotions_page.positionSlider.setSliderPosition(0)
            self.all_pages.emotions_page.positionSlider.setEnabled(True)
        except:
            self.all_pages.heart_rate_variability_page.status_label.setText("Что-то пошло не так")
            self.all_pages.emotions_page.status_label.setText("Что-то пошло не так")
            
    def setPositionHRV(self, position):
        self.all_pages.heart_rate_variability_page.videoLabel.setPixmap(QPixmap.fromImage(process_img(self.current_video[position])))
        self.all_pages.emotions_page.videoLabel.setPixmap(QPixmap.fromImage(process_img(self.current_video[position])))
        self.all_pages.emotions_page.positionSlider.setSliderPosition(position)
        
    def setPositionEmo(self, position):
        self.all_pages.heart_rate_variability_page.videoLabel.setPixmap(QPixmap.fromImage(process_img(self.current_video[position])))
        self.all_pages.emotions_page.videoLabel.setPixmap(QPixmap.fromImage(process_img(self.current_video[position])))
        self.all_pages.heart_rate_variability_page.positionSlider.setSliderPosition(position)
            
        
if __name__ == "__main__":

    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    widget = MainWindow()
    
    widget.show()

    sys.exit(app.exec())