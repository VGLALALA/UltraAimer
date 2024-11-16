from ultralytics import YOLOv10
from Utils import mouse,screen
from config import configReader
import cv2
import pyautogui
from win32api import *
import time

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
width = GetSystemMetrics(0)  # 获取当前屏幕的宽
height = GetSystemMetrics(1)  # 获取当前屏幕的高
centerx = width / 2  # 屏幕中心点x
centery = height / 2  # 屏幕中心点y
len_left, len_top = int(centerx - width / 2), int(centery - height / 2)  # 截取范围的左上角原点
monitor = {'left': int(len_left), 'top': int(len_top), 'width': int(width), 'height': int(height)}
img_scale_width = width / img_size
img_scale_height = height / img_size
# Initialize state variables
q = 0  # Toggle state for aim

def aim_move(bbox_array,offset):
    img_scale = width/img_size
    locklst = []
    x, y = 0, 0
    cx, cy = GetCursorPos()  # 以鼠标为相对
    for box in bbox_array:
        if label_off:
            # 平方和
            if box[5] == label_tab:
                box_center_x = box[0] + (box[2] / 2)  # x + (width/2)
                box_center_y = box[1] + (box[3] * (1 - offset))  # Adjust y based on offset percentage
                box.append((box_center_x * img_scale - cx) ** 2 + 
                      (box_center_y * img_scale - cy) ** 2)
        else:
            box_center_x = box[0] + (box[2] / 2)  # x + (width/2)
            box_center_y = box[1] + (box[3] * (1 - offset))  # Adjust y based on offset percentage            
            box.append((box_center_x * img_scale - cx) ** 2 + 
                      (box_center_y * img_scale - cy) ** 2)

    M.move(x,y)
    
if aim_mode == "yolo":
    model = YOLOv10(model_path)
    while True:
        # if debug_enabled:
        #     if not cv2.getWindowProperty('mss_test', cv2.WND_PROP_VISIBLE):
        #         cv2.destroyAllWindows()
        #         exit('程序结束...')
        if GetAsyncKeyState(key_exit):
            break
        shot = S.take_screenshot()
        time_initial = time.time()
        results = model(shot)
        bbox_array = []
        for r in results[0].boxes.data.tolist():
            x, y = r[0], r[1]  # Center x, y
            w, h = r[2] - r[0], r[3] - r[1]  # Width, height 
            conf = r[4]  # Confidence
            cls = r[5]  # Class
            bbox_array.append([x, y, w, h, cls, conf])
        
        # results[0].show()
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
        
        shot = S.draw_box_yolo(shot,results,((time.time() - time_initial) * 1000),img_scale_width)
        if debug_enabled:
            cv2.imshow("debug_window", shot)
            cv2.waitKey(1)
        
elif aim_mode == "color":
    while True:
        pass
    pass

