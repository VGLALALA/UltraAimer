# --------------------------
# -*- coding: utf-8 -*-
# Bilibi   : 随风而息
# @Time    : 2022/9/22 17:43
# --------------------------
from cmath import *
from ctypes import *
import numpy as np
from win32api import GetCursorPos


class Detector:
    # 初始化函数接口
    def __init__(self, dll_path):
        # 加载dll,实例化
        self.yolov5 = windll.LoadLibrary(dll_path)
        # 声明dll的Build接口参数类型
        self.yolov5.Build.argtypes = [c_char_p, c_char_p, c_int]
        # 声明dll的Init接口的返回类型
        self.yolov5.Init.restype = c_void_p
        # 声明dll的Detect接口参数类型
        self.yolov5.Detect.argtypes = [c_void_p, c_int, c_int, c_float, c_float, POINTER(c_ubyte),
                                       np.ctypeslib.ndpointer(dtype=np.float32, ndim=2, shape=(10, 6),
                                                              flags="C_CONTIGUOUS")]
        # 声明dll的free接口参数类型
        self.yolov5.Free.argtypes = [c_void_p]

    # dll的build接口封装
    def build(self, onnx_path=b"", engine_path=b"", precision=0):
        self.yolov5.Build(onnx_path, engine_path, c_int(precision))

    # 加载engine并初始化资源
    def lodel_engine(self, model_path=b""):
        # 初始化资源，申请内存，显存等资源
        self.trt = self.yolov5.Init(model_path)

    # 推理接口函数
    def predict(self, img, conf, iou):
        # 获取图片宽高
        rows, cols = img.shape[0], img.shape[1]
        # 创建接受dll返回的坐标数组    最多10*[x, y, w, h, cls, conf]    对应信息是目标的中心点和宽高，类别，置信度
        trt_array = np.zeros((10, 6), dtype=np.float32)
        # trt推理接口,传入创建的资源,图片宽,高,置信度,iou,图片数据，接受数组
        self.yolov5.Detect(self.trt, c_int(rows), c_int(cols), c_float(conf), c_float(iou),
                           img.ctypes.data_as(POINTER(c_ubyte)), trt_array)
        # 返回坐标信息
        return trt_array

    # 释放资源
    def free(self):
        self.yolov5.Free(self.trt)


class PID:
    def __init__(self):
        self.SetSpeed = 0
        self.ActualSpeed = 0
        self.Err = 0
        self.Err_Next = 0
        self.Err_last = 0
        self.Integral = 0

    # 增量式
    def PID_Control(self, x, kp, ki, kd):
        self.SetSpeed = x
        self.Err = self.SetSpeed - self.ActualSpeed
        out = kp * (self.Err - self.Err_Next) + ki * self.Err + kd * (self.Err - 2 * self.Err_Next + self.Err_last)
        self.ActualSpeed += out
        self.Err_last = self.Err_Next
        self.Err_Next = self.Err
        return out

    # 位置式
    def PID_Cal(self, x, kp, ki, kd):
        self.SetSpeed = x
        self.Err = self.SetSpeed - self.ActualSpeed
        self.Integral += self.Err
        out = kp * x + ki * self.Integral + kd * (self.Err - self.Err_last)
        self.Err_last = self.Err
        self.ActualSpeed = out
        return out


# pid实例化
pid = PID()

# SendInput实例化
SendInput = windll.user32.SendInput


# SendInput结构体
class MouseInput(Structure):
    _fields_ = [("dx", c_long),
                ("dy", c_long),
                ("mouseData", c_ulong),
                ("dwFlags", c_ulong),
                ("time", c_ulong),
                ("dwExtraInfo", POINTER(c_ulong))]


# SendInput结构体
class Input_I(Union):
    _fields_ = [("mi", MouseInput)]


# SendInput结构体
class INPUT(Structure):
    _fields_ = [("type", c_ulong),
                ("inp_i", Input_I)]


# SendInput 移动
def mouse(x, y):
    inp_i = Input_I()
    inp_i.mi = MouseInput(x, y, 0, 0x0001, 0, pointer(c_ulong(0)))
    input_m = INPUT(0, inp_i)
    windll.user32.SendInput(1, pointer(input_m), sizeof(input_m))


# HFOV
def HFOV(input_x, args):
    x = (args.game_width * 0.5) / (tan(args.game_HFOV * 3.145926 / 180 * 0.5))
    return (atan(input_x / x)) * (args.game_x_pixel / (360 * 3.145926 / 180))


# VFOV
def VFOV(input_y, args):
    y = (args.game_height * 0.5) / (tan(args.game_VFOV * 3.145926 / 180 * 0.5))
    return (atan(input_y / y)) * (args.game_y_pixel / (180 * 3.145926 / 180))


# 自瞄
def aim_move(bbox_array, monitor, cx, cy, img_scale, args):
    box = []
    box_tab = []
    x, y = 0, 0
    # 当前鼠标坐标
    # cx, cy = GetCursorPos()  # 以鼠标为相对
    for temp in bbox_array:
        if temp[0] == 0:  # 跳过为空的值
            continue
        if args.label_off:
            # 平方和
            if temp[4] == args.label_tab:
                box.append((((float(monitor['left']) + (temp[0] * img_scale)) - cx) ** 2) + (
                        ((float(monitor['top']) + (temp[1] * img_scale)) - cy) ** 2))
                box_tab.append(temp)
        else:
            box.append((((float(monitor['left']) + (temp[0] * img_scale)) - cx) ** 2) + (
                    ((float(monitor['top']) + (temp[1] * img_scale)) - cy) ** 2))

    # 屏幕坐标->相对坐标
    if args.label_off:
        if len(box_tab):
            x = (monitor['left'] + box_tab[box.index(min(box))][0] * img_scale) - cx  # # box最小值的索引,对应bbox_array最近的索引
            y = (monitor['top'] + (box_tab[box.index(min(box))][1]) * img_scale) - cy
    else:
        x = (monitor['left'] + bbox_array[box.index(min(box))][0] * img_scale) - cx  # # box最小值的索引,对应bbox_array最近的索引
        y = (monitor['top'] + bbox_array[box.index(min(box))][1] * img_scale) - cy  # Down :偏移公式
    # fov
    # x = HFOV(x, args).real  # 取实部
    # y = VFOV(y, args).real
    # pid
    x = pid.PID_Cal(x, args.kp, args.ki, args.kd)
    # 移动
    mouse(int(x), int(y))
