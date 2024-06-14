from ultralytics import YOLOv10
model = YOLOv10.from_pretrained('jameslahm/yolov10n')

#model = YOLOv10('weights/yolov10n.onnx')

model.export(format="engine",half=True, device=0)

# # End-to-End TensorRT
# yolo export model=jameslahm/yolov10{n/s/m/b/l/x} format=engine half=True simplify opset=13 workspace=16
# # or
# trtexec --onnx=yolov10n/s/m/b/l/x.onnx --saveEngine=yolov10n/s/m/b/l/x.engine --fp16
