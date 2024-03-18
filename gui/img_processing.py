import cv2
from PySide6.QtGui import QImage
from PySide6.QtCore import Qt

def process_img(frame):
    
    # Reading the image in RGB to display it
    color_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Creating and scaling QImage
    h, w, ch = color_frame.shape
    img = QImage(color_frame.data, w, h, ch * w, QImage.Format_RGB888)
    scaled_img = img.scaled(640, 480, Qt.KeepAspectRatio)
    
    return scaled_img