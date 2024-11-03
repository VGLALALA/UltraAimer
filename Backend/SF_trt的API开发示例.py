# --------------------------
# -*- coding: utf-8 -*-
# Bilibi   : 随风而息
# @Time    : 2022/9/1 21:41
# --------------------------

from ctypes import *
import cv2          # python 3.8 的解释器，安装opencv不要大于4.5.5，可能出现导入错误，如：没有代码提示
import numpy as np
import mss

'''
---------------- 使用方法 -------------------

1. 将《运行库》里的dll放在和SF_TRT.dll目录下，运行库下载链接：https://pan.baidu.com/s/1B0qlaYBOp9D0mnEyFIBe6A?pwd=0000 
2. engine确保必须是自己生成的
3. 在 mian 下修改自己的dll路径，onnx路径和engine路径。 路径记得加点表示同级目录，onnx和engine路径前的b不能去掉
4. 仅支持yolov5的onnx
5. dll内部的字符串显示使用的是 utf-8 编码，在cmd运行为乱码，pycharm显示正常
6. dll开发环境：CUDA 11.6  +  cudann8.4.1  +  Tensorrt 8.4.1  +  vs2019
7. 如果使用python来开发，建议使用pycharm



---------------- c++内部的API接口   ----------------

void* Init(char* model_path)    
    -- 作用：初始化，加载engine模型，和申请内存和显存
    -- 参数：传入char* 类型的engine路径
    -- 返回(void*)类型的实例化对象

void Detect(void* init_trt, int rows, int cols,float conf,float iou, unsigned char* src_data, float(*res_array)[6])
    -- 作用：推理，里面包含了预处理+推理 + 后处理操作
    -- 参数：传入Init返回的实例化对象(void*)，以及图片宽，高，置信度，iou，图片数据，以及接收后处理返回的坐标信息

void Build(char* onnx_name, char* engine_name, int precision=0)
    -- 作用：生成engine
    -- 参数，传入onnx文件，engine生成文件，精度，0是FP16,1是FP32，精度默认为0

void Free(void* init_trt)
    -- 作用：释放初始化创建的资源和内存

'''

# python封装
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
                                       np.ctypeslib.ndpointer(dtype=np.float32, ndim=2, shape=(50, 6), flags="C_CONTIGUOUS")]
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
        # 创建接受dll返回的坐标数组    最多50*[x, y, w, h, cls, conf]    对应信息是目标的中心点和宽高，类别，置信度
        trt_array = np.zeros((50, 6), dtype=np.float32)
        # trt推理接口,传入创建的资源,图片宽,高,置信度,iou,图片数据，接受数组
        self.yolov5.Detect(self.trt, c_int(rows), c_int(cols), c_float(conf), c_float(iou),
                           img.ctypes.data_as(POINTER(c_ubyte)), trt_array)
        # 返回坐标信息
        return trt_array

    # 释放资源
    def free(self):
        self.yolov5.Free(self.trt)


# 绘制方框
def draw_box(img, bbox_array):
    # 遍历数组里所有目标框
    for temp in bbox_array:
        # 获取4个坐标信息，并将中心点转为左上角
        bbox = [temp[0] - (temp[2] / 2), temp[1] - (temp[3] / 2), temp[2], temp[3]]  # 左上角x,y,宽高
        # 识别到的类别，转为int
        clas = int(temp[4])
        # 识别到的置信度
        conf = temp[5]
        # 绘制方框
        cv2.rectangle(img, (int(bbox[0]), int(bbox[1])), (int(bbox[0] + temp[2]), int(bbox[1] + temp[3])), (0, 255, 0),
                      2)
    # 返回处理好的图片
    return img


# mss截图
def grab_screen_mss(monitor):
    # 将图片的4通道转为3通道，去掉透明通道，因为截取的图片带有一个透明通道，BGRA->BGR
    # 在转为numpy数组
    return cv2.cvtColor(np.array(scr.grab(monitor)), cv2.COLOR_BGRA2BGR)


if __name__ == '__main__':
    # 设置参数

    conf = 0.1                                  # 置信度
    iou = 0.1                                   # iou
    dll_path = "dll/SF_TRT.dll"
    onnx_path = b"./models/cf_v6.onnx"          # onnx的路径       b不能丢   b 的作用 ：将str转为 bytes 字符串
    engine_path = b"./engine/cf_v6.engine"      # engine的路径

    # ------ 初始化 ------
    # 1.加载dll并实例化
    trt_det = Detector(dll_path=dll_path)       # 实例化类，同时传入dll路径

    # 2.生成engine
    trt_det.build(onnx_path, engine_path, 1)    # 调用类里的build方法生成engine,传入onnx路径和engine路径，可以单独使用

    # 3.加载engine
    trt_det.lodel_engine(engine_path)           # 调用类里的lodel_engine方法，加载engine数据，初始化CPU,GPU等资源

    # 4. 推理

    # ------ 推理. 示范1—加载图片推理 ------
    # 4.1.1 读取图片
    img = cv2.imread("img/test.png")

    # 4.1.2 调用推理接口，
    bbox_array = trt_det.predict(img, conf, iou)    # 调用类的推理接口，传入图片，置信度，iou, 返回所有目标的坐标信息

    # 4.1.2 绘制方框
    img = draw_box(img, bbox_array)
    # 4.1.3 显示
    cv2.imshow("read_test", img)
    cv2.waitKey(0)

    # ------ 推理. 示范2—mss屏幕截图推理 ------
    # 4.2.1 实例化mss
    scr = mss.mss()
    # 4.2.2 截取的范围，左上角原点x,原点y,宽，高
    monitor = {'left': 640, 'top': 270, 'width': 640, 'height': 640}
    # 4.2.3 创建窗口
    cv2.namedWindow('mss_test', cv2.WINDOW_NORMAL)
    while True:
        # 4.2.4关闭窗口后退出出循环
        if not cv2.getWindowProperty('mss_test', cv2.WND_PROP_VISIBLE):
            cv2.destroyAllWindows()
            exit('程序结束...')
            break

        # 4.2.5 截取一张图片
        img1 = grab_screen_mss(monitor)                     # 传入截取范围，返回一张图片

        # 4.2.6推理，传入图片，置信度，iou,返回坐标信息
        bbox_array = trt_det.predict(img1, conf, iou)       # 调用类的推理接口，传入图片，置信度，iou, 返回所有目标的坐标信息

        # 4.2.7 绘制方框
        img1 = draw_box(img1, bbox_array)

        # 4.2.8 显示
        cv2.imshow("mss_test", img1)
        cv2.waitKey(1)

    # 4.3 释放资源,程序结束一定要调用释放，不能重复释放，否则出现非法访问
    trt_det.free()
