"""Cross-platform screen capture and debugging helpers."""

import importlib

import cv2
import mss
import numpy as np
from config import ConfigReader


class Screenshot:
    def __init__(self, config_reader=None):
        cfg = (config_reader or ConfigReader()).get_screen_config()
        self.mode = cfg["mode"].lower()
        self.auto_detection = cfg["auto_detection"]
        self.width, self.height = cfg["width"], cfg["height"]
        self.scr = self._initialize()

    def _initialize(self):
        if self.mode == "mss":
            return mss.mss()
        if self.mode == "cv2":
            return cv2.VideoCapture(0)
        if self.mode == "dxcam":
            return importlib.import_module("dxcam").create()
        if self.mode == "d3dshot":
            return importlib.import_module("d3dshot").create()
        raise ValueError(f"Invalid screenshot mode: {self.mode}")

    def detect_screen_size(self):
        if self.auto_detection:
            if self.mode == "mss":
                monitor = self.scr.monitors[1]
                self.width, self.height = monitor["width"], monitor["height"]
            else:
                import pyautogui

                self.width, self.height = pyautogui.size()
        return self.width, self.height

    def take_screenshot(self):
        self.detect_screen_size()
        capture = getattr(self, f"take_screenshot_{self.mode}", None)
        if capture is None:
            raise RuntimeError(f"Screenshot mode {self.mode!r} is not implemented")
        frame = capture()
        if frame is None:
            raise RuntimeError(f"Screenshot mode {self.mode!r} returned no frame")
        return frame

    def take_screenshot_cv2(self):
        ok, frame = self.scr.read()
        if not ok:
            raise RuntimeError("Camera capture failed")
        return frame

    def take_screenshot_mss(self):
        monitor = {"left": 0, "top": 0, "width": self.width, "height": self.height}
        return cv2.cvtColor(np.asarray(self.scr.grab(monitor)), cv2.COLOR_BGRA2BGR)

    def take_screenshot_dxcam(self):
        return self.scr.grab()

    def take_screenshot_d3dshot(self):
        return np.asarray(self.scr.screenshot())

    def close(self):
        if self.mode == "cv2":
            self.scr.release()
        close = getattr(self.scr, "close", None)
        if close:
            close()

    @staticmethod
    def draw_box_yolo(image, boxes, elapsed_ms, image_scale):
        height, width = image.shape[:2]
        half = min(320, width // 2, height // 2)
        x1, y1 = width // 2 - half, height // 2 - half
        cropped = image[y1 : y1 + 2 * half, x1 : x1 + 2 * half].copy()
        fps = int(1000 / max(elapsed_ms, 0.001))
        cv2.putText(cropped, f"FPS:{fps}", (10, 30), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
        for x, y, box_width, box_height, *_ in boxes:
            left, top = int(x * image_scale - x1), int(y * image_scale - y1)
            right = int((x + box_width) * image_scale - x1)
            bottom = int((y + box_height) * image_scale - y1)
            cv2.rectangle(cropped, (left, top), (right, bottom), (0, 255, 0), 2)
        return cropped
