"""
Detection History Database Model
Stores all detection records with detailed information
"""

from datetime import datetime
from app import db


class DetectionHistory(db.Model):
    """
    Detection history model to track all detection events
    """
    __tablename__ = 'detection_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Detection metadata
    detection_type = db.Column(db.String(20), nullable=False)  # 'realtime' or 'upload'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Detection counts
    human_count = db.Column(db.Integer, default=0)
    animal_count = db.Column(db.Integer, default=0)
    
    # Detected animals (comma-separated)
    detected_animals = db.Column(db.Text)
    
    # File information (for uploads)
    filename = db.Column(db.String(255))
    file_type = db.Column(db.String(20))  # 'image' or 'video'
    processed_path = db.Column(db.String(500))
    
    # Detection details (JSON format)
    detection_details = db.Column(db.Text)  # Store as JSON string
    
    def __repr__(self):
        return f'<Detection {self.id} - {self.detection_type}>'
    
    def to_dict(self):
        """Convert detection record to dictionary"""
        return {
            'id': self.id,
            'detection_type': self.detection_type,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'human_count': self.human_count,
            'animal_count': self.animal_count,
            'detected_animals': self.detected_animals,
            'filename': self.filename,
            'file_type': self.file_type
        }
    
    @classmethod
    def create_detection(cls, user_id, detection_type, human_count, animal_count, 
                        detected_animals, filename=None, file_type=None, 
                        processed_path=None, detection_details=None):
        """
        Create a new detection record
        
        Args:
            user_id (int): ID of the user
            detection_type (str): Type of detection (realtime/upload)
            human_count (int): Number of humans detected
            animal_count (int): Number of animals detected
            detected_animals (str): Comma-separated list of animal types
            filename (str): Original filename (for uploads)
            file_type (str): Type of file (image/video)
            processed_path (str): Path to processed file
            detection_details (str): JSON string with detailed detection info
        
        Returns:
            DetectionHistory: Created detection record
        """
        detection = cls(
            user_id=user_id,
            detection_type=detection_type,
            human_count=human_count,
            animal_count=animal_count,
            detected_animals=detected_animals,
            filename=filename,
            file_type=file_type,
            processed_path=processed_path,
            detection_details=detection_details
        )
        
        db.session.add(detection)
        db.session.commit()
        
        return detection
    
    @classmethod
    def get_user_detections(cls, user_id, limit=None):
        """
        Get all detections for a specific user
        
        Args:
            user_id (int): User ID
            limit (int): Maximum number of records to return
        
        Returns:
            list: List of detection records
        """
        query = cls.query.filter_by(user_id=user_id).order_by(cls.timestamp.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @classmethod
    def get_total_detections(cls, user_id):
        """
        Get total number of detections for a user
        
        Args:
            user_id (int): User ID
        
        Returns:
            int: Total detection count
        """
        return cls.query.filter_by(user_id=user_id).count()
    
    @classmethod
    def get_detection_stats(cls, user_id):
        """
        Get detection statistics for a user
        
        Args:
            user_id (int): User ID
        
        Returns:
            dict: Statistics dictionary
        """
        detections = cls.query.filter_by(user_id=user_id).all()
        
        total_humans = sum(d.human_count for d in detections)
        total_animals = sum(d.animal_count for d in detections)
        
        return {
            'total_detections': len(detections),
            'total_humans': total_humans,
            'total_animals': total_animals,
            'realtime_count': len([d for d in detections if d.detection_type == 'realtime']),
            'upload_count': len([d for d in detections if d.detection_type == 'upload'])
        }
       