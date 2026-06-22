
import os
import json
import shutil
from pathlib import Path


def convert_coco_to_yolo():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_dir = os.path.join(base_dir, 'data', 'raw')
    yolo_dir = os.path.join(base_dir, 'data', 'yolo_dataset')
    
    class_mapping = {
        'organik': 0,
        'nonorganik': 1,
        'sampah_berbahaya': 2
    }
    
    category_folder_mapping = {
        'Organik': 'organik',
        'Anorganik': 'nonorganik',
        'B3': 'sampah_berbahaya'
    }
    splits = ['train', 'valid', 'test']
    for split in splits:
        os.makedirs(os.path.join(yolo_dir, split, 'images'), exist_ok=True)
        os.makedirs(os.path.join(yolo_dir, split, 'labels'), exist_ok=True)
    
    print("Converting COCO dataset to YOLO format...")
    print(f"Source: {raw_dir}")
    print(f"Target: {yolo_dir}")
    
    # Process each category folder
    for category_folder, class_name in category_folder_mapping.items():
        category_path = os.path.join(raw_dir, category_folder)
        if not os.path.exists(category_path):
            print(f"Warning: {category_path} does not exist, skipping...")
            continue
        
        class_id = class_mapping[class_name]
        print(f"\nProcessing {category_folder} -> {class_name} (class_id: {class_id})")
        
        for split in splits:
            split_path = os.path.join(category_path, split)
            if not os.path.exists(split_path):
                print(f"  Warning: {split_path} does not exist, skipping...")
                continue
            
            coco_json = os.path.join(split_path, '_annotations.coco.json')
            if not os.path.exists(coco_json):
                print(f"  Warning: {coco_json} does not exist, skipping...")
                continue
            
            with open(coco_json, 'r') as f:
                coco_data = json.load(f)
            
            image_id_to_filename = {img['id']: img['file_name'] for img in coco_data['images']}
            
            image_id_to_annotations = {}
            for ann in coco_data['annotations']:
                image_id = ann['image_id']
                if image_id not in image_id_to_annotations:
                    image_id_to_annotations[image_id] = []
                image_id_to_annotations[image_id].append(ann)
            
            for image_id, annotations in image_id_to_annotations.items():
                image_filename = image_id_to_filename.get(image_id)
                if not image_filename:
                    continue
                
                src_image_path = os.path.join(split_path, image_filename)
                dst_image_path = os.path.join(yolo_dir, split, 'images', image_filename)
                
                if os.path.exists(src_image_path):
                    shutil.copy2(src_image_path, dst_image_path)
                else:
                    print(f"  Warning: Image {src_image_path} not found, skipping...")
                    continue
                
                image_info = None
                for img in coco_data['images']:
                    if img['id'] == image_id:
                        image_info = img
                        break
                
                if not image_info:
                    print(f"  Warning: Image info for ID {image_id} not found, skipping...")
                    continue
                
                img_width = image_info['width']
                img_height = image_info['height']
                
                label_filename = os.path.splitext(image_filename)[0] + '.txt'
                label_path = os.path.join(yolo_dir, split, 'labels', label_filename)
                
                with open(label_path, 'w') as f:
                    for ann in annotations:
                        bbox = ann['bbox']
                        x_min, y_min, bbox_width, bbox_height = bbox
                        
                        x_center = x_min + bbox_width / 2
                        y_center = y_min + bbox_height / 2
                        
                        x_center /= img_width
                        y_center /= img_height
                        bbox_width /= img_width
                        bbox_height /= img_height
                        
                        f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {bbox_width:.6f} {bbox_height:.6f}\n")
            
            print(f"  Processed {len(image_id_to_annotations)} images in {split}")
    
    print("\nConversion completed successfully!")
    print(f"YOLO dataset created at: {yolo_dir}")


if __name__ == "__main__":
    convert_coco_to_yolo()
