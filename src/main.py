
import os
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '0'
os.environ['TORCH_DISABLE_NVIDIA_TF32'] = '1'

import argparse
from ultralytics import YOLO
import numpy as np
from collections import defaultdict
from convert_coco_to_yolo import convert_coco_to_yolo
import matplotlib.pyplot as plt


def train_custom_model():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_yaml = os.path.join(base_dir, 'data', 'data.yaml')
    
    print("Loading YOLOv8n model...")
    model = YOLO(os.path.join(base_dir, 'models', 'yolov8n.pt'))
    
    print("Starting training...")
    results = model.train(
        data=data_yaml,
        epochs=30,
        imgsz=416,
        batch=8,
        device='cpu',
        project=base_dir,
        name='runs/waste_classification',
        patience=5,
        save=True,
        plots=False,
        verbose=True
    )
    
    print("Training completed!")
    print(f"Best model saved at: {results.save_dir}/weights/best.pt")
    
    print("\nValidating model...")
    metrics = model.val()
    print(f"mAP50: {metrics.box.map50}")
    print(f"mAP50-95: {metrics.box.map}")
    
    return model


def create_visualizations(metrics, base_dir):
    """Create visualization charts for evaluation results"""
    print("\n=== Creating Visualizations ===")
    
    # Create visual folder
    visual_dir = os.path.join(base_dir, 'visual')
    os.makedirs(visual_dir, exist_ok=True)
    
    # Data dari hasil evaluasi
    classes = ['Organik', 'Non-Organik', 'Sampah Berbahaya']
    precision = [float(metrics.box.p[i]) for i in range(3)]
    recall = [float(metrics.box.r[i]) for i in range(3)]
    
    # Dataset distribution
    dataset_info = {
        'Organik': {'images': 103, 'instances': 316},
        'Non-Organik': {'images': 111, 'instances': 123},
        'Sampah Berbahaya': {'images': 100, 'instances': 323}
    }
    
    # VISUALISASI 1: Precision dan Recall per Kelas (Side by Side)
    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(classes))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, precision, width, label='Precision', color='#3498db', alpha=0.8)
    bars2 = ax.bar(x + width/2, recall, width, label='Recall', color='#e74c3c', alpha=0.8)
    
    ax.set_ylabel('Score', fontsize=12, fontweight='bold')
    ax.set_title('Precision dan Recall per Kelas Sampah', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(classes)
    ax.legend(fontsize=11)
    ax.set_ylim(0, 1.0)
    ax.grid(axis='y', alpha=0.3)
    
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.4f}',
                    ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    viz_path = os.path.join(visual_dir, 'precision_recall_comparison.png')
    plt.savefig(viz_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: precision_recall_comparison.png")
    plt.close()
    
    # VISUALISASI 2: Distribusi Dataset
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Distribusi Citra
    images = [dataset_info[cls]['images'] for cls in classes]
    colors = ['#2ecc71', '#3498db', '#e74c3c']
    bars1 = ax1.bar(classes, images, color=colors, alpha=0.8)
    ax1.set_ylabel('Jumlah Citra', fontsize=12, fontweight='bold')
    ax1.set_title('Distribusi Citra per Kelas', fontsize=14, fontweight='bold')
    ax1.grid(axis='y', alpha=0.3)
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                 f'{int(height)}',
                 ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    # Distribusi Instances
    instances = [dataset_info[cls]['instances'] for cls in classes]
    bars2 = ax2.bar(classes, instances, color=colors, alpha=0.8)
    ax2.set_ylabel('Jumlah Instances', fontsize=12, fontweight='bold')
    ax2.set_title('Distribusi Instances per Kelas', fontsize=14, fontweight='bold')
    ax2.grid(axis='y', alpha=0.3)
    for bar in bars2:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                 f'{int(height)}',
                 ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    viz_path = os.path.join(visual_dir, 'dataset_distribution.png')
    plt.savefig(viz_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: dataset_distribution.png")
    plt.close()
    
    # VISUALISASI 3: Overall Metrics
    metrics_names = ['mAP50', 'mAP50-95', 'Precision', 'Recall']
    metrics_values = [float(metrics.box.map50), float(metrics.box.map), 
                      float(metrics.box.mp), float(metrics.box.mr)]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(metrics_names, metrics_values, color=['#9b59b6', '#3498db', '#2ecc71', '#e74c3c'], alpha=0.8)
    ax.set_ylabel('Score', fontsize=12, fontweight='bold')
    ax.set_title('Overall Validation Metrics', fontsize=14, fontweight='bold')
    ax.set_ylim(0, 1.0)
    ax.grid(axis='y', alpha=0.3)
    
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.4f}',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    viz_path = os.path.join(visual_dir, 'overall_metrics.png')
    plt.savefig(viz_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: overall_metrics.png")
    plt.close()
    
    print(f"All visualizations saved to: {visual_dir}")


def evaluate_model(model_path=None, data_yaml=None):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    if model_path is None:
        model_path = os.path.join(base_dir, "runs", "waste_classification", "weights", "best.pt")
    
    if data_yaml is None:
        data_yaml = os.path.join(base_dir, 'data', 'data.yaml')
    
    if not os.path.exists(model_path):
        print(f"Model not found at {model_path}")
        print("Please train the model first using train_custom_model")
        return None
    
    print(f"Loading model from: {model_path}")
    model = YOLO(model_path)
    
    print("\n=== Model Validation ===")
    metrics = model.val(data=data_yaml, plots=False)
    
    print(f"\n=== Validation Metrics ===")
    print(f"mAP50: {metrics.box.map50:.4f}")
    print(f"mAP50-95: {metrics.box.map:.4f}")
    print(f"Precision: {metrics.box.mp:.4f}")
    print(f"Recall: {metrics.box.mr:.4f}")
    
    print(f"\n=== Per-Class Metrics ===")
    class_names = ['organik', 'nonorganik', 'sampah_berbahaya']
    for i, class_name in enumerate(class_names):
        if i < len(metrics.box.p):
            print(f"{class_name}:")
            print(f"  Precision: {metrics.box.p[i]:.4f}")
            print(f"  Recall: {metrics.box.r[i]:.4f}")
    
    # Create visualizations
    create_visualizations(metrics, base_dir)
    
    return metrics


def test_on_images(model_path=None, test_images_dir=None):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    if model_path is None:
        model_path = os.path.join(base_dir, "runs", "waste_classification", "weights", "best.pt")
    
    if test_images_dir is None:
        test_images_dir = os.path.join(base_dir, "data", "yolo_dataset", "test", "images")
    
    if not os.path.exists(model_path):
        print(f"Model not found at {model_path}")
        return
    
    if not os.path.exists(test_images_dir):
        print(f"Test images directory not found at {test_images_dir}")
        return
    
    print(f"Loading model from: {model_path}")
    model = YOLO(model_path)
    
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
    test_images = []
    for ext in image_extensions:
        test_images.extend([f for f in os.listdir(test_images_dir) if f.lower().endswith(ext)])
    
    print(f"\nFound {len(test_images)} test images")
    
    class_mapping = {0: 'organik', 1: 'nonorganik', 2: 'sampah_berbahaya'}
    results_summary = defaultdict(int)
    
    for i, image_name in enumerate(test_images[:10]):
        image_path = os.path.join(test_images_dir, image_name)
        print(f"\n[{i+1}/10] Testing: {image_name}")
        
        results = model(image_path, verbose=False, conf=0.25)
        
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
    parser.add_argument('--force-train', action='store_true',
                        help='Force training even if model already exists')
    
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
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        default_model_path = os.path.join(base_dir, "runs", "waste_classification", "weights", "best.pt")
        
        if os.path.exists(default_model_path) and not args.force_train:
            print("\n[1/4] Training Model...")
            print("-"*60)
            print(f"Model already exists at: {default_model_path}")
            print("Skipping training. Use --force-train to retrain.")
            print("\nTraining skipped!")
        else:
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
