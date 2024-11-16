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
        print(bbox_array) 
        for temp in bbox_array:
            print(temp)
            # 获取4个坐标信息，并将中心点转为左上角
            bbox = [temp[0], temp[1], temp[2], temp[3]]  # x, y, width, height from YOLOv10 boxes
            # 识别到的类别，转为int
            cls = int(temp[4])  # Class of detected object
            # 识别到的置信度
            conf = temp[5]
            # 绘制方框
            cv2.rectangle(img, (int(bbox[0] * img_scale), int(bbox[1] * img_scale)), (
                int((bbox[0] * img_scale) + (temp[2] * img_scale)), int((bbox[1] * img_scale) + (temp[3] * img_scale))),
                        (0, 255, 0),
                        2)

            cv2.putText(img, f"FPS:{int(1000 / l)}", (10, 30), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
            # cv2.putText(img, f"CLS:{int(temp[4])}", (int(bbox[0] * img_scale) - 10, int(bbox[1] * img_scale) - 30),
            #             cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 225, 0), 2)
        # 返回处理好的图片
        return img