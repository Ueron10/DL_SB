"""
Main pipeline script for SmartBin project.
This script runs the training and evaluation pipeline.
"""

import argparse
import os
from ultralytics import YOLO
import cv2
import numpy as np
from collections import defaultdict
from convert_coco_to_yolo import convert_coco_to_yolo


def train_custom_model():
    """
    Train a custom YOLO model on the waste classification dataset
    """
    # Get the base directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_yaml = os.path.join(base_dir, 'data', 'data.yaml')
    
    # Load a pre-trained YOLOv8 model (nano version for faster training)
    print("Loading YOLOv8n model...")
    model = YOLO(os.path.join(base_dir, 'models', 'yolov8n.pt'))
    
    # Train the model
    print("Starting training...")
    results = model.train(
        data=data_yaml,
        epochs=30,  # Number of training epochs (reduced for faster training)
        imgsz=416,  # Image size (reduced for faster training)
        batch=8,    # Batch size (reduced for CPU)
        device='cpu',  # Use CPU (change to 'cuda' if GPU is available)
        project=base_dir,
        name='runs/waste_classification',
        patience=5,  # Early stopping patience
        save=True,
        plots=False,  # Disable plots for faster training
        verbose=True
    )
    
    print("Training completed!")
    print(f"Best model saved at: {results.save_dir}/weights/best.pt")
    
    # Validate the model
    print("\nValidating model...")
    metrics = model.val()
    print(f"mAP50: {metrics.box.map50}")
    print(f"mAP50-95: {metrics.box.map}")
    
    return model


def evaluate_model(model_path=None, data_yaml=None):
    """
    Evaluate the trained YOLO model on the test dataset
    """
    # Get the base directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Default paths
    if model_path is None:
        model_path = os.path.join(base_dir, "runs", "waste_classification", "weights", "best.pt")
    
    if data_yaml is None:
        data_yaml = os.path.join(base_dir, 'data', 'data.yaml')
    
    # Check if model exists
    if not os.path.exists(model_path):
        print(f"Model not found at {model_path}")
        print("Please train the model first using train_custom_model")
        return None
    
    print(f"Loading model from: {model_path}")
    model = YOLO(model_path)
    
    # Validate the model
    print("\n=== Model Validation ===")
    metrics = model.val(data=data_yaml)
    
    print(f"\n=== Validation Metrics ===")
    print(f"mAP50: {metrics.box.map50:.4f}")
    print(f"mAP50-95: {metrics.box.map:.4f}")
    print(f"Precision: {metrics.box.mp:.4f}")
    print(f"Recall: {metrics.box.mr:.4f}")
    
    # Per-class metrics
    print(f"\n=== Per-Class Metrics ===")
    class_names = ['organik', 'nonorganik', 'sampah_berbahaya']
    for i, class_name in enumerate(class_names):
        if i < len(metrics.box.p):
            print(f"{class_name}:")
            print(f"  Precision: {metrics.box.p[i]:.4f}")
            print(f"  Recall: {metrics.box.r[i]:.4f}")
    
    return metrics


def test_on_images(model_path=None, test_images_dir=None):
    """
    Test the model on individual images and display results
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    if model_path is None:
        model_path = os.path.join(base_dir, "runs", "waste_classification", "weights", "best.pt")
    
    if test_images_dir is None:
        test_images_dir = os.path.join(base_dir, "data", "raw")
    
    if not os.path.exists(model_path):
        print(f"Model not found at {model_path}")
        return
    
    if not os.path.exists(test_images_dir):
        print(f"Test images directory not found at {test_images_dir}")
        return
    
    print(f"Loading model from: {model_path}")
    model = YOLO(model_path)
    
    # Get test images
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
    test_images = []
    for ext in image_extensions:
        test_images.extend([f for f in os.listdir(test_images_dir) if f.lower().endswith(ext)])
    
    print(f"\nFound {len(test_images)} test images")
    
    # Class mapping
    class_mapping = {0: 'organik', 1: 'nonorganik', 2: 'sampah_berbahaya'}
    
    # Results summary
    results_summary = defaultdict(int)
    
    for i, image_name in enumerate(test_images[:10]):  # Test first 10 images
        image_path = os.path.join(test_images_dir, image_name)
        print(f"\n[{i+1}/10] Testing: {image_name}")
        
        # Run inference
        results = model(image_path, verbose=False, conf=0.25)
        
        # Process results
        for result in results:
            if result.boxes:
                for box in result.boxes:
                    class_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    class_name = class_mapping.get(class_id, 'unknown')
                    
                    print(f"  Detected: {class_name} (confidence: {confidence:.2f})")
                    results_summary[class_name] += 1
            else:
                print("  No detection")
                results_summary['no_detection'] += 1
    
    # Print summary
    print(f"\n=== Test Summary ===")
    for class_name, count in results_summary.items():
        print(f"{class_name}: {count}")


def main():
    parser = argparse.ArgumentParser(description='SmartBin Pipeline: Train and Evaluate Model')
    parser.add_argument('--mode', type=str, choices=['train', 'evaluate', 'test', 'all', 'convert'], 
                        default='all', help='Pipeline mode: train, evaluate, test, all, or convert')
    parser.add_argument('--model-path', type=str, default=None, 
                        help='Path to trained model (for evaluation/testing)')
    parser.add_argument('--data-yaml', type=str, default=None, 
                        help='Path to data.yaml file')
    parser.add_argument('--test-images-dir', type=str, default=None, 
                        help='Path to test images directory')
    
    args = parser.parse_args()
    
    print("="*60)
    print("SMARTBIN PIPELINE")
    print("="*60)
    
    if args.mode in ['convert', 'all']:
        print("\n[0/4] Converting COCO to YOLO format...")
        print("-"*60)
        convert_coco_to_yolo()
        print("\nConversion completed!")
    
    if args.mode in ['train', 'all']:
        print("\n[1/4] Training Model...")
        print("-"*60)
        train_custom_model()
        print("\nTraining completed!")
    
    if args.mode in ['evaluate', 'all']:
        print("\n[2/4] Evaluating Model...")
        print("-"*60)
        evaluate_model(model_path=args.model_path, data_yaml=args.data_yaml)
        print("\nEvaluation completed!")
    
    if args.mode in ['test', 'all']:
        print("\n[3/4] Testing on Images...")
        print("-"*60)
        test_on_images(model_path=args.model_path, test_images_dir=args.test_images_dir)
        print("\nTesting completed!")
    
    print("\n" + "="*60)
    print("PIPELINE COMPLETED")
    print("="*60)
    print("\nTo run the GUI application, use: python app/app.py")


if __name__ == "__main__":
    main()
