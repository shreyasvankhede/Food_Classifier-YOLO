from ultralytics import YOLO
import torch


model=YOLO("yolo26s.pt")


model.train(
    data='/content/dataset/dataset/data2/dataset.yaml',
    imgsz=640,
    batch=16,
    epochs=100,
    workers=0,
    device='cuda',
    project='/content/drive/MyDrive/proj',
    name="food_v8m"
)

