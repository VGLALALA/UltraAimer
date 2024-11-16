# screenshot.py
import json
import cv2
import numpy as np
import mss
import dxcam
import configparser
import os
import d3dshot
from win32api import GetSystemMetrics
from config import configReader
class Screenshot:
    def __init__(self) -> None:
        config_reader = configReader.ConfigReader()
        screen_config = config_reader.get_screen_config()
        self.mode = screen_config['mode']
        self.auto_detection = screen_config['auto_detection']
        self.width = screen_config['width']
        self.height = screen_config['height']
        self.scr = None
        self.initialize_screenshotter()
        
    def initialize_screenshotter(self):
        if self.mode == "mss":
            self.scr = mss.mss()
        elif self.mode == "dxcam":
            self.scr = dxcam.create()
        elif self.mode == "cv2":
            self.scr = cv2.VideoCapture(0)
        elif self.mode == "d3dshot":
            self.scr = d3dshot.create()
        else:
            raise ValueError(f"Invalid screenshot mode: {self.mode}")
    
    def __init__(self) -> None:
        config_reader = configReader.ConfigReader()
        screen_config = config_reader.get_screen_config()
        self.mode = screen_config['mode']
        self.auto_detection = screen_config['auto_detection']
        self.width = screen_config['width']
        self.height = screen_config['height']
        self.scr = None
        self.initialize_screenshotter()

    def detect_screen_size(self):
        if self.auto_detection:
            self.width = GetSystemMetrics(0)
            self.height = GetSystemMetrics(1)
        else:
            self.width = self.config.getint('Screen', 'width')
            self.height = self.config.getint('Screen', 'height')
        
    def load_config(self, config_file: str) -> configparser.ConfigParser:
        config = configparser.ConfigParser()
        config.read(config_file)
        return config

    def take_screenshot(self):
        self.detect_screen_size()
        if self.mode == "mss":
            return self.take_screenshot_mss()
        elif self.mode == "dxcam":
            return self.take_screenshot_dxcam()
        elif self.mode == "cv2":
            return self.take_screenshot_cv2()
        elif self.mode == "d3dshot":
            return self.take_screenshot_d3dshot()
        
    def take_screenshot_cv2(self):
        ret, frame = self.scr.read()
        self.scr.release()
        return frame

    def take_screenshot_mss(self):
        monitor = {'left': 0, 'top': 0, 'width': self.width, 'height': self.height}
        return cv2.cvtColor(np.array(self.scr.grab(monitor)), cv2.COLOR_BGRA2BGR)

    def take_screenshot_dxcam(self):
        screenshot = self.scr.grab()
        return screenshot


    def take_screenshot_d3dshot(self):
        self.scr.screenshot()

    def draw_box_yolo(self,img, bbox_array, l, img_scale):
        # Get screen dimensions and calculate center crop coordinates
        screen_h, screen_w = img.shape[:2]
        x1 = screen_w//2 - 320  # 320 is half of 640
        y1 = screen_h//2 - 320
        x2 = screen_w//2 + 320
        y2 = screen_h//2 + 320
        
        # Crop image to 640x640 center window
        img = img[y1:y2, x1:x2]
        
        # Draw FPS counter once per frame
        cv2.putText(img, f"FPS:{int(1000 / l)}", (10, 30), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
        
        # Check if bbox_array is empty
        if not bbox_array:
            return img  # Return the image unchanged if there are no bounding boxes
        print(bbox_array)
        
        # Draw boxes for each detection
        for temp in bbox_array:
            if temp != []:
                print(temp)
                # Adjust bbox coordinates for cropped window
                bbox = [
                    temp[0] - x1/img_scale,  # Adjust x coordinate 
                    temp[1] - y1/img_scale,  # Adjust y coordinate
                    temp[2], temp[3]  # Width and height stay the same
                ]
                cls = int(temp[4])  # Class of detected object
                conf = temp[5]  # Confidence score
                
                # Draw bounding box if it falls within the cropped area
                if (0 <= bbox[0] * img_scale <= 640 and 0 <= bbox[1] * img_scale <= 640):
                    cv2.rectangle(img, 
                        (int(bbox[0] * img_scale), int(bbox[1] * img_scale)),
                        (int((bbox[0] * img_scale) + (temp[2] * img_scale)), 
                         int((bbox[1] * img_scale) + (temp[3] * img_scale))),
                        (0, 255, 0),
                        2)
                
        return img