import os

import cv2
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage

from Frame_handler_VPG.FrameHandlerVPG import FrameHandlerVPG
from Frame_handler.FrameHandlerMimic import FrameHandlerMimic
from vpg_analyzer_for_gui import vpg_analyzer

class Thread_Loading(QThread):
    #init signal to picture imaging in gui
    updateFrame = Signal(QImage)

    #init thread 
    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.cap = True
        self.video_path = 'Data/temp/temp.avi'
        self.fps = 0
        self.video = []

    #thread main process
    def run(self):
        #get camera and parametrs
        self.cap = cv2.VideoCapture(self.video_path)        
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        
        #init path for saving results of image processing
        path = os.path.split(self.video_path)[0] + '/'
        
        #init and start handler for hrv
        self.frame_handler = FrameHandlerVPG(os.path.join(path, 'vpg.json'))
        self.frame_handler.start()
        
        #init and start handler for mimic
        self.mimic_frame_handler = FrameHandlerMimic(os.path.join(path, 'mimic.json'))
        self.mimic_frame_handler.start()
        
        #registration cycle (status emmited from gui)
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            self.frame_handler.push(frame)
            self.mimic_frame_handler.push(frame)
            
            self.video.append(frame) 
        
        #waiting for all process ended
        self.frame_handler.finish()
        self.mimic_frame_handler.finish()
        self.vpg = self.frame_handler.join()
        self.mimic_data = self.mimic_frame_handler.join()
        
        #process vpg to hrv
        self.hrv_data = vpg_analyzer(self.vpg, self.fps, os.path.join(path, 'hrv.json'))
              

    def setCurrentFileName(self, current_name):
        if current_name:
            self.video_path = current_name