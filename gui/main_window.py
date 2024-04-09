import sys
import time

import json

import cv2, numpy as np
from PySide6.QtCore import Qt, Slot, QSize
from PySide6.QtGui import QScreen, QPixmap, QIcon
from PySide6.QtWidgets import (QApplication, QComboBox, QGroupBox,
                               QHBoxLayout, QLabel, QMainWindow, QPushButton,
                               QSizePolicy, QVBoxLayout, QWidget, 
                               QStackedWidget, QFileDialog)
#from __feature__ import snake_case, true_property


from gui.all_pages_widget import All_pages
from gui.main_menu_widget import Main_menu
from gui.thread import Thread
from gui.thread_for_loading import Thread_Loading
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
        self.setWindowTitle("Анализ ВСР и мимики")
        self.setWindowIcon(QIcon('Resources/bmstu.png'))
        
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
        self.all_pages.video_capture_page.start_registration_button.clicked.connect(self.start_registration)
        self.all_pages.video_capture_page.load_button.clicked.connect(self.open_video)
        
        #init variables
        self.current_video_path = ''
        self.current_video = []
        self.current_vpg = []
        self.current_video_fps = 0
        self.current_vpg_frames = []
        self.current_vpg_start_frame = 0
        self.current_vpg_end_frame = 0
        self.current_mimic_data = []
       
    @Slot()
    def go_to_video_capture_page(self):
        self.all_pages.setCurrentWidget(self.all_pages.video_capture_page)
        
        self.main_menu.video_button.setEnabled(False)
        self.main_menu.hrv_button.setEnabled(True)
        self.main_menu.emotions_button.setEnabled(True)
        
        self.main_menu.video_button.setStyleSheet("font-family : ALS Sector;"
                                                  "font: bold;"
                                                  "background-color : #006cdc;"
                                                  "color : black;"
                                        "min-height: 2em;"
                                        "border-radius: 5px")
        self.main_menu.hrv_button.setStyleSheet("font-family : ALS Sector;"
                                                "font: bold;"
                                                "background-color : #00b8ff;"
                                        "min-height: 2em;"
                                        "border-radius: 5px")
        self.main_menu.emotions_button.setStyleSheet("font-family : ALS Sector;"
                                                     "font: bold;"
                                                     "background-color : #00b8ff;"
                                        "min-height: 2em;"
                                        "border-radius: 5px")
     
    @Slot()
    def go_to_heart_rate_variability_page(self):
        self.all_pages.setCurrentWidget(self.all_pages.heart_rate_variability_page)
        
        self.main_menu.video_button.setEnabled(True)
        self.main_menu.hrv_button.setEnabled(False)
        self.main_menu.emotions_button.setEnabled(True)
        
        self.main_menu.video_button.setStyleSheet("font-family : ALS Sector;"
                                                  "font: bold;"
                                                  "background-color : #00b8ff;"
                                        "min-height: 2em;"
                                        "border-radius: 5px")
        self.main_menu.hrv_button.setStyleSheet("font-family : ALS Sector;"
                                                "font: bold;"
                                                "background-color : #006cdc;"
                                                "color : black;"
                                        "min-height: 2em;"
                                        "border-radius: 5px")
        self.main_menu.emotions_button.setStyleSheet("font-family : ALS Sector;"
                                                     "font: bold;"
                                                     "background-color : #00b8ff;"
                                        "min-height: 2em;"
                                        "border-radius: 5px")
     
    @Slot()
    def go_to_emotions_page(self):
        self.all_pages.setCurrentWidget(self.all_pages.emotions_page)
        
        self.main_menu.video_button.setEnabled(True)
        self.main_menu.hrv_button.setEnabled(True)
        self.main_menu.emotions_button.setEnabled(False)
        
        self.main_menu.video_button.setStyleSheet("font-family : ALS Sector;"
                                                  "font: bold;"
                                                  "background-color : #00b8ff;"
                                        "min-height: 2em;"
                                        "border-radius: 5px")
        self.main_menu.hrv_button.setStyleSheet("font-family : ALS Sector;"
                                                "font: bold;"
                                                "background-color : #00b8ff;"
                                        "min-height: 2em;"
                                        "border-radius: 5px")
        self.main_menu.emotions_button.setStyleSheet("font-family : ALS Sector;"
                                                     "font: bold;"
                                                     "background-color : #006cdc;"
                                                     "color : black;"
                                        "min-height: 2em;"
                                        "border-radius: 5px")
        
    @Slot()
    def open_video(self):
        
        filename, filter = self.dialog.getOpenFileName(caption='Open file', dir='.', filter='*.avi')
        if filename == '': return 0

        self.all_pages.video_capture_page.load_button.setEnabled(False)
        self.all_pages.video_capture_page.start_registration_button.setEnabled(False)
        self.all_pages.video_capture_page.start_registration_button.setEnabled(False)
        self.all_pages.heart_rate_variability_page.loadButton.setEnabled(False)
        self.all_pages.emotions_page.loadButton.setEnabled(False)
  
        self.all_pages.heart_rate_variability_page.path_label.setText("Выбран файл " + filename.split("/")[-1].split(".")[0])
        self.all_pages.heart_rate_variability_page.status_label.setText("Видео загружается")
        
        self.all_pages.emotions_page.path_label.setText("Выбран файл " + filename.split("/")[-1].split(".")[0])
        self.all_pages.emotions_page.status_label.setText("Видео загружается")
        
        self.current_video_path = filename
        mimic_path = filename.split("/")
        mimic_path[-1] = 'mimic.json'
        mimic_path = '/'.join(mimic_path)
        hrv_path = filename.split("/")
        hrv_path[-1] = 'hrv.json'
        hrv_path = '/'.join(hrv_path)
        try: 
            self.current_video, self.current_video_fps = read_video(filename)
            with open(mimic_path, 'r') as file:
                self.current_mimic_data = json.load(file)
            with open(hrv_path, 'r') as file:
                self.current_hrv = json.load(file)
            self.tune_video_widgets()
            self.tune_graphs()
            self.all_pages.emotions_page.updateMimic(self.current_mimic_data[0])
            
        except:
            try:
                self.all_pages.video_capture_page.th = Thread_Loading()
                self.all_pages.video_capture_page.th.finished.connect(self.recall_thread_data)

                self.all_pages.video_capture_page.start_registration_button.setEnabled(False)
                self.all_pages.video_capture_page.stop_registration_button.setEnabled(False)

                self.all_pages.video_capture_page.th.setCurrentFileName(self.current_video_path)
                self.all_pages.video_capture_page.th.start()

            except:
                self.all_pages.heart_rate_variability_page.status_label.setText("Что-то пошло не так")
                self.all_pages.emotions_page.status_label.setText("Что-то пошло не так")

                self.all_pages.video_capture_page.load_button.setEnabled(True)
                self.all_pages.video_capture_page.start_registration_button.setEnabled(True)
                self.all_pages.video_capture_page.stop_registration_button.setEnabled(False)
                self.all_pages.heart_rate_variability_page.loadButton.setEnabled(True)
                self.all_pages.emotions_page.loadButton.setEnabled(True)
            
    def setPositionHRV(self, position):
        self.all_pages.heart_rate_variability_page.videoLabel.setPixmap(QPixmap.fromImage(process_img(self.current_video[position])))
        self.all_pages.emotions_page.videoLabel.setPixmap(QPixmap.fromImage(process_img(self.current_video[position])))
        #self.all_pages.emotions_page.positionSlider.setSliderPosition(position)
        self.all_pages.heart_rate_variability_page.updatePosition(position)
        self.all_pages.emotions_page.updateMimic(self.current_mimic_data[position])
        
    def setPositionEmo(self, position):
        self.all_pages.heart_rate_variability_page.videoLabel.setPixmap(QPixmap.fromImage(process_img(self.current_video[position])))
        self.all_pages.emotions_page.videoLabel.setPixmap(QPixmap.fromImage(process_img(self.current_video[position])))
        #self.all_pages.heart_rate_variability_page.positionSlider.setSliderPosition(position)
        self.all_pages.heart_rate_variability_page.updatePosition(position)
        self.all_pages.emotions_page.updateMimic(self.current_mimic_data[position])
    
    @Slot()
    def start_registration(self):
        #init thread here to necessary connections
        self.all_pages.video_capture_page.th = Thread()
        self.all_pages.video_capture_page.th.updateFrame.connect(self.all_pages.video_capture_page.setImage)
        self.all_pages.video_capture_page.th.finished.connect(self.recall_thread_data)

        self.all_pages.video_capture_page.start_registration_button.setEnabled(False)
        self.all_pages.video_capture_page.stop_registration_button.setEnabled(True)

        self.all_pages.video_capture_page.th.setCurrentFileName(self.all_pages.video_capture_page.current_file_name)
        self.all_pages.video_capture_page.th.start()

    @Slot()
    def recall_thread_data(self):
        
        self.current_video = self.all_pages.video_capture_page.th.video.copy()
        self.current_hrv = self.all_pages.video_capture_page.th.hrv_data.copy()
        self.current_mimic_data = self.all_pages.video_capture_page.th.mimic_data.copy()

        self.all_pages.video_capture_page.videoLabel.setPixmap(QPixmap.fromImage(self.all_pages.video_capture_page.placeholder))

        self.tune_video_widgets()
        self.tune_graphs()

        self.all_pages.emotions_page.updateMimic(self.current_mimic_data[0])
        
        if self.all_pages.video_capture_page.th:
            self.all_pages.video_capture_page.th.terminate()
            time.sleep(1)

        self.all_pages.video_capture_page.start_registration_button.setEnabled(True)
        self.all_pages.video_capture_page.stop_registration_button.setEnabled(False)
        self.all_pages.video_capture_page.load_button.setEnabled(True)
        self.all_pages.heart_rate_variability_page.loadButton.setEnabled(True)
        self.all_pages.emotions_page.loadButton.setEnabled(True)
        
    def tune_video_widgets(self):
        
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

    def tune_graphs(self):

        self.all_pages.heart_rate_variability_page.setHRPlot(self.current_hrv['hr']['hr'])
        self.all_pages.heart_rate_variability_page.setSDANNPlot(self.current_hrv['hr']['hr_hist'])
        self.all_pages.heart_rate_variability_page.setRMSSDPlot(self.current_hrv['hr']['rr'])
        self.all_pages.heart_rate_variability_page.sdann_label.setText(f'SDANN: {self.current_hrv["hr"]["sdann"]}')
        self.all_pages.heart_rate_variability_page.rmssd_label.setText(f'RMSSD: {self.current_hrv["hr"]["rmmsd"]}')
        self.all_pages.heart_rate_variability_page.updatePosition(0)
        
            
        
if __name__ == "__main__":

    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    widget = MainWindow()
    
    widget.show()

    sys.exit(app.exec())