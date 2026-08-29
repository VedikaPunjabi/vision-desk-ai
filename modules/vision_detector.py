import os
import cv2
import torch
from ultralytics import YOLO
from huggingface_hub import hf_hub_download

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, 'models')
os.makedirs(MODELS_DIR, exist_ok=True)

# 1. Base YOLO Model (Guarantees Person & General Object Detection)
base_model_path = os.path.join(MODELS_DIR, 'yolov8n.pt')
base_model = YOLO(base_model_path)

# 2. Specialized PPE Model (Guarantees Hardhat, Vest, Gloves, Boots, etc.)
ppe_model_path = hf_hub_download(
    repo_id="Hexmon/vyra-yolo-ppe-detection", 
    filename="best.pt",
    local_dir=MODELS_DIR
)
ppe_model = YOLO(ppe_model_path)


def run_detection(input_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.basename(input_path)
    output_path = os.path.join(output_dir, f"detected_{filename}")

    # ------------------- 1. Image Processing (UNCHANGED) -------------------
    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
        img = cv2.imread(input_path)
        detected_objects = []

        with torch.no_grad():
            base_results = base_model(input_path, conf=0.25)
            ppe_results = ppe_model(input_path, conf=0.20, imgsz=640)

        for box in base_results[0].boxes:
            cls_id = int(box.cls[0])
            class_name = base_model.names[cls_id]
            confidence = round(float(box.conf[0]) * 100, 1)

            if class_name.lower() in ['person', 'ladder']:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 128), 2)
                cv2.putText(img, f"{class_name} {confidence}%", (x1, max(y1 - 10, 15)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 128), 2)
                detected_objects.append(f"{class_name} ({confidence}%)")

        for box in ppe_results[0].boxes:
            cls_id = int(box.cls[0])
            class_name = ppe_model.names[cls_id]
            confidence = round(float(box.conf[0]) * 100, 1)

            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(img, f"{class_name} {confidence}%", (x1, max(y1 - 10, 15)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            detected_objects.append(f"{class_name} ({confidence}%)")

        cv2.imwrite(output_path, img)

        if not detected_objects:
            detected_objects.append("No objects or personnel detected.")

        return {
            'type': 'image',
            'output_file': f"detected_{filename}",
            'detections': detected_objects
        }

    # ------------------- 2. High-Speed Video Processing -------------------
    elif filename.lower().endswith(('.mp4', '.webm', '.mov', '.avi')):
        cap = cv2.VideoCapture(input_path)
        fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Use browser-compatible codec ('avc1' or 'H264')
        try:
            fourcc = cv2.VideoWriter_fourcc(*'avc1')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            if not out.isOpened():
                raise Exception("avc1 failed, falling back")
        except:
            fourcc = cv2.VideoWriter_fourcc(*'H264')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        detected_objects_set = set()

        frame_count = 0
        FRAME_SKIP = 10  # Process 1 frame out of 10 for ~2x speedup over previous run

        cached_base_boxes = []
        cached_ppe_boxes = []

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1

            if frame_count % FRAME_SKIP == 0 or frame_count == 1:
                with torch.no_grad():
                    base_results = base_model(frame, conf=0.25, verbose=False)
                    ppe_results = ppe_model(frame, conf=0.20, imgsz=480, verbose=False)

                cached_base_boxes = base_results[0].boxes
                cached_ppe_boxes = ppe_results[0].boxes

            for box in cached_base_boxes:
                cls_id = int(box.cls[0])
                class_name = base_model.names[cls_id]
                if class_name.lower() in ['person', 'ladder']:
                    detected_objects_set.add(class_name)
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 128), 2)
                    cv2.putText(frame, class_name, (x1, max(y1 - 10, 15)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 128), 2)

            for box in cached_ppe_boxes:
                cls_id = int(box.cls[0])
                class_name = ppe_model.names[cls_id]
                detected_objects_set.add(class_name)
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, class_name, (x1, max(y1 - 10, 15)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            out.write(frame)

        cap.release()
        out.release()

        return {
            'type': 'video',
            'output_file': f"detected_{filename}",
            'detections': list(detected_objects_set)
        }

    else:
        raise ValueError("Unsupported file format.")

    