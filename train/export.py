from ultralytics import YOLOv10
import tensorrt as trt
print(trt.__version__)

model = YOLOv10('/home/vglalala/UltraAimer/yolov10/runs/detect/train4/weights/best.pt')

model.export(format='TensorRT',half=True,opset=13,workspace=16)
