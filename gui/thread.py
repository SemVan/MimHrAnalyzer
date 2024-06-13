import os
import sys

import cv2
import numpy as np
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage

from gui.img_processing import process_img
from Frame_handler_VPG.FrameHandlerVPG import FrameHandlerVPG
from Frame_handler_Mimic.FrameHandlerMimic import FrameHandlerMimic
from vpg_analyzer_for_gui import vpg_analyzer

class Thread(QThread):
    #init signal to picture imaging in gui
    updateFrame = Signal(QImage)

    #init thread 
    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.status = True
        self.cap = True
        self.path = 'Data/'
        self.current_file_name = 'temp'
        self.fps = 0
        self.video = []

        self.THRESHOLD_AREA = 10  # Порог изменения площади в процентах!!!!!!!
        self.THRESHOLD_INTENSITY_MAX = 765
        self.THRESHOLD_INTENSITY_MIN = 0

    #thread main process
    def run(self):
        #get camera and parametrs
        self.cap = cv2.VideoCapture(0)        
        frame_width = int(self.cap.get(3))
        frame_height = int(self.cap.get(4))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        
        #init path for saving results of image processing
        path = os.path.join(self.path, self.current_file_name + '/')
        path1 = path
        
        #init and start handler for hrv
        self.frame_handler = FrameHandlerVPG(os.path.join(path, 'vpg.json'))
        self.frame_handler.start()
        
        #init and start handler for mimic
        self.mimic_frame_handler = FrameHandlerMimic(os.path.join(path, 'mimic.json'))
        self.mimic_frame_handler.start()
        
        #mkdir for saving and tune codec for video saving
        try:
            os.mkdir(path)
        except:
            pass
        path = os.path.join(path, self.current_file_name + '.avi')
        video = cv2.VideoWriter(path, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), self.fps, (frame_width, frame_height))
        
        #registration cycle (status emmited from gui)
        while self.status:
            ret, frame = self.cap.read()
            if not ret:
                continue
            
            self.frame_handler.push(frame)
            self.mimic_frame_handler.push(frame)
            
            self.video.append(frame)
            
            video.write(frame)
            
            #process image and send to gui
            scaled_img = process_img(frame)
            self.updateFrame.emit(scaled_img)  
        
        #waiting for all process ended
        self.frame_handler.finish()
        self.mimic_frame_handler.finish()

        result = self.frame_handler.join()
        self.vpg = result[0]
        areas = result[1]
        intesity = result[2]

        self.mimic_data = self.mimic_frame_handler.join()

        print(path + '/hrv.json')
        
        #process vpg to hrv
        self.hrv_data = vpg_analyzer(self.vpg, self.fps, path1 + '/hrv.json')

        # process area
        self.areas_flags = []
        mean_area = 0
        k = 0
        for area in areas:
            if area is None:
                continue
            mean_area += area
            k += 1
        mean_area = mean_area / k

        for area in areas:
            if area is None:
                self.areas_flags.append(False)
                continue

            if (100 * np.abs(area - mean_area) / mean_area) <= self.THRESHOLD_AREA:
                self.areas_flags.append(True)
            else:
                self.areas_flags.append(False)

        # process intesity
        self.intesity_flags = []

        for inten in intesity:
            if inten is None:
                self.intesity_flags.append(False)
                continue

            if self.THRESHOLD_INTENSITY_MIN <= inten <= self.THRESHOLD_INTENSITY_MAX:
                self.intesity_flags.append(True)
            else:
                self.intesity_flags.append(False)

        self.hrv_data['area'] = self.areas_flags
        self.hrv_data['lum'] = self.intesity_flags
        
        #kill codec
        video.release()
        #sys.exit(-1)
        
       

    def setCurrentFileName(self, current_name):
        if current_name:
            self.current_file_name = current_name

