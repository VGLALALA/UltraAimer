from ultralytics import YOLOv10

# Load a model
model = YOLOv10("/home/vglalala/UltraAimer/yolov10/runs/detect/train4/weights/best.pt")  # load a custom model

# Validate the model
metrics = model.val()  # no arguments needed, dataset and settings remembered
