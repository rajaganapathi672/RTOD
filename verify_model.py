from ultralytics import YOLO
import os

model_path = r"C:\Users\RAJAGANAPATHY\Desktop\RTOD\yolov8n.pt"
image_path = r"C:\Users\RAJAGANAPATHY\Desktop\RTOD\uploads\Snapchat-1265524612.jpg"

print(f"Loading model from: {model_path}")
try:
    model = YOLO(model_path)
    print("Model loaded successfully")
except Exception as e:
    print(f"Failed to load model: {e}")
    exit(1)

print(f"Testing on image: {image_path}")
if not os.path.exists(image_path):
    print("Image file not found!")
    exit(1)

try:
    results = model(image_path)
    print(f"Detection executed. Results: {len(results)}")
    
    for r in results:
        print(f"Boxes: {len(r.boxes)}")
        for box in r.boxes:
            print(f"Class: {box.cls}, Conf: {box.conf}")
            
except Exception as e:
    print(f"Detection failed: {e}")
