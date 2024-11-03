# --------------------------
# -*- coding: utf-8 -*-
# Bilibi   : 随风而息
# @Time    : 2022/9/22 17:36
# --------------------------
import argparse
import time
import cv2  # 安装opencv不要大于4.5.5，可能出现导入错误，如：没有代码提示
import numpy as np
import mss
from win32api import *

from Aim_cf项目示例.Aim_move import Detector, aim_move

parser = argparse.ArgumentParser()
parser.add_argument('--dll-path', type=str, default="../dll/SF_TRT.dll", help='dll路径')
parser.add_argument('--onnx-path', type=str, default=b"../models/cf_v6.onnx", help='onnx模型地址，b不能丢掉')
parser.add_argument('--engine-path', type=str, default=b"../engine/cf_v6.engine", help='engine的生成地址，b不能丢掉')
parser.add_argument('--game-width', type=int, default=1920, help='游戏分辨率的宽')
parser.add_argument('--game-height', type=int, default=1080, help='游戏分辨率的高')
parser.add_argument('--game_HFOV', type=int, default=83.105462, help='实际HFOV')
parser.add_argument('--game_VFOV', type=int, default=53, help='实际VFOV')
parser.add_argument('--game_x_pixel', type=int, default=7020, help='游戏旋转一圈的像素值')
parser.add_argument('--game_y_pixel', type=int, default=7020 / 2, help='游戏视角最高点至最低点的的像素值')
parser.add_argument('--img-size', type=int, default=640, help='模型的输入大小')
parser.add_argument('--conf-thres', type=float, default=0.6, help='置信阈值')
parser.add_argument('--iou-thres', type=float, default=0.1, help='交并比阈值')
parser.add_argument('--scale', type=float, default=0.25, help='截取范围比例，根据个人设置')
parser.add_argument('--VK_KEY', type=int, default=0x24, help='自瞄开关的虚拟键值，0x24:键盘的Home')
parser.add_argument('--label-off', type=bool, default=False, help='自选标签开启，False / True')
parser.add_argument('--label-tab', type=int, default=1, help='选择标签类别')  # 0:身体  1：头
parser.add_argument('--offset', type=int, default=0, help='偏移量')
parser.add_argument('--END-KEY', type=int, default=0x23, help='程序退出按键的虚拟键值,0x23：键盘的END键')
parser.add_argument('--kp', type=float, default=0.6, help='PID kp值')
parser.add_argument('--ki', type=float, default=0.35, help='PID ki值')
parser.add_argument('--kd', type=float, default=0, help='PID kd值')
parser.add_argument('--show-window', type=bool, default=False, help='显示检测框')
args = parser.parse_args()


# 绘制方框
def draw_box(img, bbox_array, l, img_scale):
    # 遍历数组里所有目标框
    for temp in bbox_array:
        # 获取4个坐标信息，并将中心点转为左上角
        bbox = [temp[0] - (temp[2] / 2), temp[1] - (temp[3] / 2), temp[2], temp[3]]  # 左上角x,y,宽高
        # 识别到的类别，转为int
        clas = int(temp[4])
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


# mss截图
def grab_screen_mss(monitor):
    # 将图片的4通道转为3通道，去掉透明通道，因为截取的图片带有一个透明通道，BGRA->BGR
    # 在转为numpy数组
    return cv2.cvtColor(np.array(scr.grab(monitor)), cv2.COLOR_BGRA2BGR)


if __name__ == '__main__':
    # 设置参数变量
    width = GetSystemMetrics(0)  # 获取当前屏幕的宽
    height = GetSystemMetrics(1)  # 获取当前屏幕的高
    cx = width / 2  # 屏幕中心点x
    cy = height / 2  # 屏幕中心点y
    q = 0  # 开关变量

    # ------ trt初始化 ------
    # 1.加载dll并实例化
    trt_det = Detector(dll_path=args.dll_path)  # 实例化类，同时传入dll路径
    # 2.生成engine
    trt_det.build(args.onnx_path, args.engine_path, 1)  # 调用类里的build方法生成engine,传入onnx路径和engine路径，可以单独使用
    # 3.加载engine
    trt_det.lodel_engine(args.engine_path)  # 调用类里的lodel_engine方法，加载engine数据，初始化CPU,GPU等资源

    # ------ 截图设置 ------
    scr = mss.mss()  # 实例化
    len_width, len_height = width * args.scale, width * args.scale  # 截取范围的宽高
    len_left, len_top = int(cx - len_width / 2), int(cy - len_height / 2)  # 截取范围的左上角原点
    monitor = {'left': int(len_left), 'top': int(len_top), 'width': int(len_width), 'height': int(len_height)}  # 生成截取范围
    img_scale_width = len_width / args.img_size
    img_scale_height = len_height / args.img_size

    # ------ 循环 ------
    # 创建显示窗口
    if args.show_window:
        cv2.namedWindow('mss_test', cv2.WINDOW_NORMAL)
    while True:
        # 关闭窗口后退出循环 或者按键退出
        if args.show_window:
            if not cv2.getWindowProperty('mss_test', cv2.WND_PROP_VISIBLE):
                cv2.destroyAllWindows()
                exit('程序结束...')
                break
        if GetAsyncKeyState(args.END_KEY):
            break

        # 截取一张图片    7-8 ms
        ti = time.time()
        img1 = grab_screen_mss(monitor)  # 传入截取范围，返回一张图片

        # 推理，传入图片，置信度，iou,返回坐标信息     19-20ms
        bbox_array = trt_det.predict(img1, args.conf_thres, args.iou_thres)  # 调用类的推理接口，传入图片，置信度，iou, 返回所有目标的坐标信息

        # 开关逻辑
        if GetAsyncKeyState(args.VK_KEY) and q == 0:
            q = 1
        elif q == 1 and GetAsyncKeyState(args.VK_KEY) is not True:
            q = 2
            print("AIM开")
        elif GetAsyncKeyState(args.VK_KEY) and q == 2:
            q = 3
        elif q == 3 and GetAsyncKeyState(args.VK_KEY) is not True:
            q = 0
            print("AIM关")

        # 存在目标且自瞄打开
        if (bbox_array[0])[0] != 0 and q == 2:
            aim_move(bbox_array, monitor, cx, cy, img_scale_width, args)  # 移动

        # 绘制方框   0-1ms
        img1 = draw_box(img1, bbox_array, (time.time() - ti) * 1000, img_scale_width)

        # 显示
        if args.show_window:
            cv2.imshow("mss_test", img1)
            cv2.waitKey(1)

    #  释放资源,程序结束一定要调用释放，不能重复释放，否则出现非法访问
    trt_det.free()
