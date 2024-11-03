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
debug_enabled = debug_config['enabled']
aim_mode = mode_config['aim'].lower()
upper_color = mode_config['upper_color'] 
lower_color = mode_config['lower_color']
img_size = yolo_config['img_size']
model_folder = yolo_config['model_folder']
model_path = yolo_config['model']
label_off = yolo_config['label_off']
label_tab = yolo_config['label_tab']
key_reload_config = keybind_config['key_reload_config']
key_toggle_aim = keybind_config['key_toggle_aim'] 
key_toggle_recoil = keybind_config['key_toggle_recoil']
key_exit = keybind_config['key_exit']
key_trigger = keybind_config['key_trigger']
key_rapid_fire = keybind_config['key_rapid_fire']
aim_keys = keybind_config['aim_keys']
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

def aim_move(bbox_array):
    img_scale = width/img_size
    box = []
    box_tab = []
    x, y = 0, 0
    cx, cy = GetCursorPos()  # 以鼠标为相对
    for temp in bbox_array:
        if temp[0] == 0:  # 跳过为空的值
            continue
        if label_off:
            # 平方和
            if temp[4] == label_tab:
                box.append((((float(monitor['left']) + (temp[0] * img_scale)) - cx) ** 2) + (
                        ((float(monitor['top']) + (temp[1] * img_scale)) - cy) ** 2))
                box_tab.append(temp)
        else:
            box.append((((float(monitor['left']) + (temp[0] * img_scale)) - cx) ** 2) + (
                    ((float(monitor['top']) + (temp[1] * img_scale)) - cy) ** 2))

    # 屏幕坐标->相对坐标
    if label_off:
        if len(box_tab):
            x = (monitor['left'] + box_tab[box.index(min(box))][0] * img_scale) - cx  # # box最小值的索引,对应bbox_array最近的索引
            y = (monitor['top'] + (box_tab[box.index(min(box))][1]) * img_scale) - cy
    else:
        x = (monitor['left'] + bbox_array[box.index(min(box))][0] * img_scale) - cx  # # box最小值的索引,对应bbox_array最近的索引
        y = (monitor['top'] + bbox_array[box.index(min(box))][1] * img_scale) - cy  # Down :偏移公式

    M.move(x,y)
    
if aim_mode == "yolo":
    model = YOLOv10(model_path)
    while True:
        if debug_enabled:
            if not cv2.getWindowProperty('mss_test', cv2.WND_PROP_VISIBLE):
                cv2.destroyAllWindows()
                exit('程序结束...')
        if GetAsyncKeyState(key_exit):
            break
        shot = S.take_screenshot()
        time_initial = time.time()
        results = model(shot)
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
        if (results[0])[0] != 0 and q == 2:
            aim_move(results)
        shot = S.draw_box_yolo(shot,results,(time.time() - time_initial) * 1000,img_scale_width)
        if debug_enabled:
            cv2.imshow("mss_test", shot)
            cv2.waitKey(1)
        
elif aim_mode == "color":
    while True:
        pass
    pass

