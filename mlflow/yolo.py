from ultralytics import YOLO, settings
import os
import torch

settings.update({"mlflow": True})

# Load mô hình YOLOv11 đã được pretrain
model = YOLO("yolo11n.pt")

# Huấn luyện mô hình
results = model.train(
    data="/home/siu/MLOp/data.yaml",  # Đường dẫn đến dataset
    epochs=2,  # Số epoch
    imgsz=320,  # Kích thước ảnh
    optimizer="Adam",  # Optimizer
    project="YOLOv11_Experiment",  # Tên dự án
    name="Run_1"  # Tên chạy (run)
)

# Sau khi train, các thông số, metrics, và artifacts sẽ được lưu tự động trên MLflow.
