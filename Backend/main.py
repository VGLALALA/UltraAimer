from ultralytics import YOLOv10
from Utils import mouse,screen
from config import configReader
import cv2
import pyautogui
from win32api import *
import time
import numpy as np

M = mouse.Mouse()
S = screen.Screenshot()
config_reader = configReader.ConfigReader()
yolo_config = config_reader.get_yolo_config()
mode_config = config_reader.get_mode_config()
keybind_config = config_reader.get_keybind_config()
debug_config = config_reader.get_debug_config()
mouse_config = config_reader.get_mouse_config()
recoil_separation = mouse_config['recoil_seperation']
offset = mouse_config['offset']
debug_enabled = debug_config['enabled']
aim_mode = mode_config['aim'].lower()
upper_color = mode_config['upper_color'] 
lower_color = mode_config['lower_color']
img_size = yolo_config['img_size']
model_folder = yolo_config['model_folder']
model_path = yolo_config['model']
label_off = yolo_config['label_off']
label_tab = yolo_config['label_tab']
key_reload_config = int(keybind_config['key_reload_config'], 16)
key_toggle_aim = int(keybind_config['key_toggle_aim'], 16)
key_toggle_recoil = int(keybind_config['key_toggle_recoil'], 16) 
key_exit = int(keybind_config['key_exit'], 16)
key_trigger = int(keybind_config['key_trigger'], 16)
key_rapid_fire = int(keybind_config['key_rapid_fire'], 16)
aim_keys = int(keybind_config['aim_keys'], 16)
width = GetSystemMetrics(0)
height = GetSystemMetrics(1)
centerx = width / 2
centery = height / 2
len_left, len_top = int(centerx - width / 2), int(centery - height / 2)
monitor = {'left': int(len_left), 'top': int(len_top), 'width': int(width), 'height': int(height)}
img_scale_width = width / img_size
img_scale_height = height / img_size
# Initialize state variables
q = 0  # Toggle state for aim

def aim_move(bbox_array,offset):
    img_scale = width/img_size
    locklst = []
    x, y = 0, 0
    cx, cy = GetCursorPos()
    for box in bbox_array:
        if label_off:
            if box[5] == label_tab:
                box_center_x = box[0] + (box[2] / 2)
                box_center_y = box[1] + (box[3] * (1 - offset))
                box.append((box_center_x * img_scale - cx) ** 2 + 
                      (box_center_y * img_scale - cy) ** 2)
        else:
            box_center_x = box[0] + (box[2] / 2)
            box_center_y = box[1] + (box[3] * (1 - offset))            
            box.append((box_center_x * img_scale - cx) ** 2 + 
                      (box_center_y * img_scale - cy) ** 2)

    M.move(x,y)
    
if aim_mode == "yolo":
    model = YOLOv10(model_path)
    while True:
        if GetAsyncKeyState(key_exit):
            break
        shot = S.take_screenshot()
        time_initial = time.time()
        results = model(shot)
        bbox_array = []
        for r in results[0].boxes.data.tolist():
            x, y = r[0], r[1]
            w, h = r[2] - r[0], r[3] - r[1]
            conf = r[4]
            cls = r[5]
            bbox_array.append([x, y, w, h, cls, conf])
        
        if GetAsyncKeyState(key_toggle_aim) and q == 0:
            q = 1
        elif q == 1 and GetAsyncKeyState(key_toggle_aim) is not True:
            q = 2
            print("AIM开")
        elif GetAsyncKeyState(key_toggle_aim) and q == 2:
            q = 3
        elif q == 3 and GetAsyncKeyState(key_toggle_aim) is not True:
            q = 0
            print("AIM关")
        if len(bbox_array) > 0 and q == 2:
            aim_move(bbox_array)
        
        shot = S.draw_box_yolo(shot,bbox_array,((time.time() - time_initial) * 1000),img_scale_width)
        if debug_enabled:
            cv2.imshow("debug_window", shot)
            cv2.waitKey(1)
        
elif aim_mode == "color":
    while True:
        if GetAsyncKeyState(key_exit):
            break
            
        shot = S.take_screenshot()
        hsv = cv2.cvtColor(shot, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, np.array(lower_color), np.array(upper_color))
        kernel = np.ones((3, 3), np.uint8)
        dilated = cv2.dilate(mask, kernel, iterations=3)
        thresh = cv2.threshold(dilated, 60, 255, cv2.THRESH_BINARY)[1]

        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            screen_center = (width // 2, height // 2)
            min_distance = float('inf')
            closest_contour = None

            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                area = cv2.contourArea(contour)

                if area < 500 or area > 10000:
                    continue

                center = (x + w // 2, y + int(h * offset))
                distance = ((center[0] - screen_center[0]) ** 2 + (center[1] - screen_center[1]) ** 2) ** 0.5

                if distance < min_distance:
                    min_distance = distance
                    closest_contour = contour

            if closest_contour is not None and q == 2:
                x, y, w, h = cv2.boundingRect(closest_contour)
                center_x = x + w // 2
                center_y = y + int(h * offset)

                cx, cy = GetCursorPos()
                x_diff = center_x - cx
                y_diff = center_y - cy

                M.move(x_diff, y_diff)

                if debug_enabled:
                    cv2.rectangle(shot, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.circle(shot, (center_x, center_y), 5, (0, 0, 255), -1)
        
        if GetAsyncKeyState(key_toggle_aim) and q == 0:
            q = 1
        elif q == 1 and GetAsyncKeyState(key_toggle_aim) is not True:
            q = 2
            print("AIM开")
        elif GetAsyncKeyState(key_toggle_aim) and q == 2:
            q = 3
        elif q == 3 and GetAsyncKeyState(key_toggle_aim) is not True:
            q = 0
            print("AIM关")
            
        if debug_enabled:
            cv2.imshow("debug_window", shot)
            cv2.waitKey(1)

