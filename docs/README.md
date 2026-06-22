# SmartBin - Automatic Waste Sorter

SmartBin is an AI-powered waste sorting system that uses computer vision to classify waste into three categories: organic, non-organic, and hazardous waste.

## Project Structure

```
Smart/
├── app/                    # GUI Application
│   ├── __init__.py
│   └── app.py             # Main GUI application (includes SerialComm)
├── src/                    # Source code for ML pipeline
│   ├── __init__.py
│   ├── detection.py       # YOLO detection system
│   ├── main.py            # Pipeline runner (train/evaluate/test)
│   └── requirements.txt   # Python dependencies
├── data/                   # Dataset folder
│   ├── raw/               # Raw training images (COCO format)
│   ├── yolo_dataset/      # Processed YOLO dataset
│   └── data.yaml          # YOLO dataset configuration
├── models/                 # Model folder
│   └── yolov8n.pt        # Pre-trained YOLO model
├── .gitignore            # Git ignore file
└── README.md             # This file
```

## Installation

1. Install dependencies:
```bash
pip install -r src/requirements.txt
```

## Usage

### Run the GUI Application
```bash
python app/app.py
```

### Run the ML Pipeline

The pipeline supports three modes: train, evaluate, test, or all.

**Run complete pipeline (train + evaluate + test):**
```bash
python src/main.py
```

**Train only:**
```bash
python src/main.py --mode train
```

**Evaluate only:**
```bash
python src/main.py --mode evaluate
```

**Test on images only:**
```bash
python src/main.py --mode test
```

**With custom paths:**
```bash
python src/main.py --mode evaluate --model-path path/to/model.pt --data-yaml path/to/data.yaml
```

### Individual Scripts

**Train model:**
```bash
python src/train_custom_model.py
```

**Evaluate model:**
```bash
python src/evaluation.py
```

## Features

- **Real-time Detection**: Uses YOLOv8 for fast object detection
- **Automatic Sorting**: Sends serial commands to control servo motors
- **Custom Training**: Train on your own waste dataset
- **Evaluation Metrics**: mAP, precision, recall for model performance
- **GUI Interface**: User-friendly interface for detection and control

## Configuration

Edit `src/config.py` to adjust:
- `STABILITY_FRAMES_REQUIRED`: Number of frames required for stable detection (default: 3)

Edit `app/serial_comm.py` to adjust:
- `SERIAL_PORT`: Serial port for Arduino communication (default: "COM4")
- `BAUD_RATE`: Serial baud rate (default: 115200)

## Model Training

1. Prepare your dataset in the `yolo_dataset/` folder following YOLO format
2. Update `data.yaml` with your dataset configuration
3. Run training:
```bash
python src/main.py --mode train
```

The trained model will be saved in `runs/waste_classification/weights/best.pt`

## Hardware Requirements

- Camera (webcam or USB camera)
- Arduino or microcontroller with servo motors
- Serial connection (USB)
- Optional: GPU for faster training
