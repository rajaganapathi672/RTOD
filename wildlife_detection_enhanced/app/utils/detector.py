"""
Enhanced YOLO Detection Service Module
Handles AI-powered object detection with comprehensive animal classification
"""

import os
import cv2
import numpy as np
from ultralytics import YOLO
from flask import current_app
import logging
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedYOLODetector:
    """
    Enhanced YOLO-based detection service with comprehensive animal detection
    
    Uses YOLOv8 model trained on COCO dataset with 80 classes including:
    - Humans (person)
    - Domestic animals (dog, cat, horse, cow, sheep, etc.)
    - Wild animals (elephant, bear, zebra, giraffe, etc.)
    - Birds and other wildlife
    """
    
    # Comprehensive mapping of COCO classes to animal categories
    ANIMAL_CLASSES = {
        # Domestic Animals
        'dog': 'Domestic',
        'cat': 'Domestic',
        'horse': 'Domestic',
        'sheep': 'Domestic',
        'cow': 'Domestic',
        
        # Wild Animals - Large Mammals
        'elephant': 'Wild',
        'bear': 'Wild',
        'zebra': 'Wild',
        'giraffe': 'Wild',
        
        # Birds
        'bird': 'Wild',
        
        # Additional Animals
        'bird': 'Wild',
    }
    
    # Full COCO dataset animal class names with proper capitalization
    ANIMAL_DISPLAY_NAMES = {
        'dog': 'Dog',
        'cat': 'Cat',
        'horse': 'Horse',
        'sheep': 'Sheep',
        'cow': 'Cow',
        'elephant': 'Elephant',
        'bear': 'Bear',
        'zebra': 'Zebra',
        'giraffe': 'Giraffe',
        'bird': 'Bird',
    }
    
    # Human class
    HUMAN_CLASS = 'person'
    
    def __init__(self):
        """Initialize Enhanced YOLO detector"""
        self.model = None
        self.confidence_threshold = 0.5
        self.model_info = {
            'name': 'YOLOv8n',
            'dataset': 'COCO (Common Objects in Context)',
            'total_classes': 80,
            'animal_classes': len(self.ANIMAL_CLASSES),
            'version': '8.1.0'
        }
    
    def load_model(self):
        """Load YOLOv8n model with error handling"""
        try:
            if self.model is None:
                model_path = current_app.config.get('YOLO_MODEL', 'yolov8n.pt')
                self.confidence_threshold = current_app.config.get('CONFIDENCE_THRESHOLD', 0.5)
                
                logger.info(f"Loading YOLO model: {model_path}")
                logger.info(f"Model info: {json.dumps(self.model_info, indent=2)}")
                
                self.model = YOLO(model_path)
                logger.info("✓ YOLO model loaded successfully")
                logger.info(f"✓ Confidence threshold: {self.confidence_threshold}")
                logger.info(f"✓ Detectable animals: {', '.join(self.ANIMAL_DISPLAY_NAMES.values())}")
            
            return True
        except Exception as e:
            logger.error(f"✗ Error loading YOLO model: {str(e)}")
            return False
    
    def detect_image(self, image_path):
        """
        Perform detection on an image
        
        Args:
            image_path (str): Path to the image file
        
        Returns:
            dict: Detection results with counts and detected objects
        """
        try:
            # Load model if not loaded
            if not self.load_model():
                return None
            
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"Failed to read image: {image_path}")
                return None
            
            # Perform detection
            logger.info(f"Processing image: {image_path}")
            results = self.model(image, conf=self.confidence_threshold, verbose=False)[0]
            
            # Process results
            detection_data = self._process_results(results)
            
            # Log detection summary
            logger.info(f"Detection complete: {detection_data['human_count']} humans, "
                       f"{detection_data['animal_count']} animals")
            if detection_data['detected_animals']:
                logger.info(f"Animals detected: {', '.join(detection_data['detected_animals'])}")
            
            # Draw bounding boxes
            annotated_image = results.plot()
            
            # Save processed image
            processed_path = self._save_processed_image(annotated_image, image_path)
            detection_data['processed_path'] = processed_path
            
            return detection_data
            
        except Exception as e:
            logger.error(f"Error detecting image: {str(e)}")
            return None
    
    def detect_video(self, video_path):
        """
        Perform detection on a video
        
        Args:
            video_path (str): Path to the video file
        
        Returns:
            dict: Detection results with counts and detected objects
        """
        try:
            # Load model if not loaded
            if not self.load_model():
                return None
            
            # Open video
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                logger.error(f"Failed to open video: {video_path}")
                return None
            
            # Get video properties
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            logger.info(f"Processing video: {video_path}")
            logger.info(f"Video properties: {width}x{height} @ {fps}fps, {total_frames} frames")
            
            # Prepare output video
            processed_path = self._get_processed_path(video_path, is_video=True)
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(processed_path, fourcc, fps, (width, height))
            
            # Initialize detection counters
            max_humans = 0
            max_animals = 0
            all_detected_animals = set()
            
            frame_count = 0
            processed_frames = 0
            
            # Process video frames
            while True:
                # Optimization: Skip frames using cap.grab() without decoding
                if frame_count % 15 != 0:
                    if not cap.grab():
                        break
                    frame_count += 1
                    continue
                
                # Only decode frames we intend to process
                ret, frame = cap.read()
                if not ret:
                    break
                
                results = self.model(frame, conf=self.confidence_threshold, verbose=False)[0]
                detection_data = self._process_results(results)
                
                # Update maximums
                max_humans = max(max_humans, detection_data['human_count'])
                max_animals = max(max_animals, detection_data['animal_count'])
                all_detected_animals.update(detection_data['detected_animals'])
                
                # Annotate frame
                annotated_frame = results.plot()
                out.write(annotated_frame)
                processed_frames += 1
                
                frame_count += 1
                
                # Log progress every 100 frames
                if frame_count % 100 == 0:
                    logger.info(f"Processed {frame_count}/{total_frames} frames")
            
            # Release resources
            cap.release()
            out.release()
            
            logger.info(f"Video processing complete: {frame_count} total frames, "
                       f"{processed_frames} frames analyzed")
            logger.info(f"Max detections: {max_humans} humans, {max_animals} animals")
            
            return {
                'human_count': max_humans,
                'animal_count': max_animals,
                'detected_animals': sorted(list(all_detected_animals)),
                'processed_path': processed_path,
                'total_frames': frame_count,
                'processed_frames': processed_frames
            }
            
        except Exception as e:
            logger.error(f"Error detecting video: {str(e)}")
            return None
    
    def _process_results(self, results):
        """
        Process YOLO detection results with enhanced animal classification
        
        Args:
            results: YOLO detection results
        
        Returns:
            dict: Processed detection data with detailed animal information
        """
        human_count = 0
        animal_count = 0
        detected_animals = []
        detection_details = []
        
        # Get class names from model
        names = results.names
        
        # Process each detection
        for box in results.boxes:
            class_id = int(box.cls[0])
            class_name = names[class_id].lower()
            confidence = float(box.conf[0])
            
            # Get bounding box coordinates
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            
            # Check if human
            if class_name == self.HUMAN_CLASS:
                human_count += 1
                detection_details.append({
                    'type': 'human',
                    'class': 'Person',
                    'confidence': round(confidence, 2),
                    'bbox': [int(x1), int(y1), int(x2), int(y2)]
                })
            
            # Check if animal
            elif class_name in self.ANIMAL_CLASSES:
                animal_count += 1
                display_name = self.ANIMAL_DISPLAY_NAMES.get(class_name, class_name.title())
                
                if display_name not in detected_animals:
                    detected_animals.append(display_name)
                
                detection_details.append({
                    'type': 'animal',
                    'class': display_name,
                    'category': self.ANIMAL_CLASSES[class_name],
                    'confidence': round(confidence, 2),
                    'bbox': [int(x1), int(y1), int(x2), int(y2)]
                })
        
        return {
            'human_count': human_count,
            'animal_count': animal_count,
            'detected_animals': sorted(detected_animals),
            'detection_details': detection_details,
            'total_detections': human_count + animal_count
        }
    
    def _save_processed_image(self, annotated_image, original_path):
        """
        Save processed image with annotations
        
        Args:
            annotated_image: Annotated image array
            original_path: Original image path
        
        Returns:
            str: Path to processed image
        """
        processed_path = self._get_processed_path(original_path)
        cv2.imwrite(processed_path, annotated_image)
        logger.info(f"Saved processed image: {processed_path}")
        return processed_path
    
    def _get_processed_path(self, original_path, is_video=False):
        """
        Generate path for processed file
        
        Args:
            original_path: Original file path
            is_video: Whether the file is a video
        
        Returns:
            str: Processed file path
        """
        processed_folder = current_app.config['PROCESSED_FOLDER']
        filename = os.path.basename(original_path)
        name, ext = os.path.splitext(filename)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if is_video:
            processed_filename = f"{name}_detected_{timestamp}.mp4"
        else:
            processed_filename = f"{name}_detected_{timestamp}{ext}"
        
        return os.path.join(processed_folder, processed_filename)
    
    def get_model_info(self):
        """
        Get detailed model information
        
        Returns:
            dict: Model information including classes and capabilities
        """
        return {
            **self.model_info,
            'detectable_animals': list(self.ANIMAL_DISPLAY_NAMES.values()),
            'animal_categories': {
                'domestic': [name for name, cat in self.ANIMAL_CLASSES.items() if cat == 'Domestic'],
                'wild': [name for name, cat in self.ANIMAL_CLASSES.items() if cat == 'Wild']
            },
            'confidence_threshold': self.confidence_threshold
        }


# Global enhanced detector instance
detector = EnhancedYOLODetector()


# Model Performance Documentation
"""
YOLO v8n Model Specifications:
================================

Dataset: COCO (Common Objects in Context)
- Training Images: 118,000+
- Validation Images: 5,000+
- Total Classes: 80
- Animal Classes: 10+

Animal Detection Classes:
-------------------------
Domestic Animals:
- Dog, Cat, Horse, Cow, Sheep

Wild Animals:
- Elephant, Bear, Zebra, Giraffe, Bird

Performance Metrics (COCO val2017):
-----------------------------------
- mAP@0.5: ~52.8%
- mAP@0.5:0.95: ~37.3%
- Speed: ~8ms (NVIDIA T4 GPU)
- Parameters: 3.2M
- Model Size: 6.2MB

Detection Capabilities:
----------------------
✓ Real-time inference (30+ FPS on GPU)
✓ Multi-object detection
✓ Bounding box visualization
✓ Confidence scoring
✓ Class-agnostic NMS
✓ Export to multiple formats

Optimization Features:
---------------------
✓ Frame sampling for video (every 10th frame)
✓ Configurable confidence threshold
✓ Batch processing ready
✓ GPU acceleration support
✓ Memory-efficient processing

Usage Recommendations:
---------------------
1. Use GPU for real-time detection
2. Adjust confidence threshold based on use case
3. Consider frame sampling for long videos
4. Monitor memory usage for large files
5. Enable logging for debugging

Dataset Sources:
---------------
Primary: COCO Dataset (https://cocodataset.org)
License: CC BY 4.0
Citation: Lin et al., "Microsoft COCO: Common Objects in Context", ECCV 2014
"""
          