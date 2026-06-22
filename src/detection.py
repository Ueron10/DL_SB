import cv2
import os
from ultralytics import YOLO

YOLO_CONFIDENCE_THRESHOLD = 0.7
CUSTOM_MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "runs", "waste_classification", "weights", "best.pt")
YOLO_MODEL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models", "yolov8n.pt")
YOLO_MODEL = CUSTOM_MODEL_PATH if os.path.exists(CUSTOM_MODEL_PATH) else YOLO_MODEL

CUSTOM_CLASS_MAPPING = {
    0: "organik",
    1: "nonorganik",
    2: "sampah_berbahaya"
}

class DetectionSystem:
    def __init__(self):
        self.yolo_model = None
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self._initialize()

    def _initialize(self):
        print("Initializing YOLO model...")
        try:
            if os.path.exists(CUSTOM_MODEL_PATH):
                print(f"Loading custom model from: {CUSTOM_MODEL_PATH}")
                self.yolo_model = YOLO(CUSTOM_MODEL_PATH)
                print("Custom YOLO model loaded successfully")
            else:
                print(f"Custom model not found at {CUSTOM_MODEL_PATH}")
                print(f"Loading pre-trained model: {YOLO_MODEL}")
                self.yolo_model = YOLO(YOLO_MODEL)
                print("Pre-trained YOLO model loaded successfully")
        except Exception as e:
            print(f"Error loading YOLO model: {e}")
            raise

    def get_category_from_class_id(self, class_id):
        return CUSTOM_CLASS_MAPPING.get(class_id, None)
    
    def detect(self, frame, in_cooldown=False):
        result = {
            "best_class": None,
            "best_confidence": 0.0,
            "best_box": None,
            "current_category": None,
            "decision_source": "None",
            "api_error_message": ""
        }

        yolo_results = self.yolo_model(frame, verbose=False, conf=YOLO_CONFIDENCE_THRESHOLD)

        for yolo_result in yolo_results:
            for box in yolo_result.boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])

                category = self.get_category_from_class_id(class_id)
                if category is None:
                    continue

                if confidence > result["best_confidence"]:
                    result["best_confidence"] = confidence
                    result["best_class"] = class_id
                    result["current_category"] = category
                    result["best_box"] = box.xyxy[0].cpu().numpy()
                    result["decision_source"] = "Custom YOLO Model"

        return result
    
