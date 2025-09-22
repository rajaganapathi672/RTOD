"""
Enhanced Detection Blueprint
Real-time and upload detection with comprehensive notification system
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, Response
from werkzeug.utils import secure_filename
from app import db
from app.models.detection import DetectionHistory
from app.utils.detector import detector
from app.utils.email_service import EmailService
from app.utils.notifications import NotificationManager
from functools import wraps
import os
import cv2
import json
from datetime import datetime
import logging

detection_bp = Blueprint('detection', __name__)
logger = logging.getLogger(__name__)


def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def allowed_file(filename):
    """Check if file extension is allowed"""
    from flask import current_app
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@detection_bp.route('/realtime')
@login_required
def realtime():
    """Real-time detection page"""
    return render_template('detection/realtime.html')


@detection_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """Upload detection page with enhanced notifications"""
    if request.method == 'POST':
        # Check if file was uploaded
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            # Secure filename
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"{timestamp}_{filename}"
            
            # Save file
            from flask import current_app
            upload_folder = current_app.config['UPLOAD_FOLDER']
            filepath = os.path.join(upload_folder, unique_filename)
            file.save(filepath)
            
            logger.info(f"File uploaded: {unique_filename}")
            
            # Determine file type
            file_ext = filename.rsplit('.', 1)[1].lower()
            is_video = file_ext in ['mp4', 'avi', 'mov', 'mkv']
            file_type = 'video' if is_video else 'image'
            
            # Perform detection
            logger.info(f"Starting {file_type} detection...")
            if is_video:
                detection_result = detector.detect_video(filepath)
            else:
                detection_result = detector.detect_image(filepath)
            
            if detection_result:
                # Extract detection data
                human_count = detection_result['human_count']
                animal_count = detection_result['animal_count']
                detected_animals = ', '.join(detection_result['detected_animals']) if detection_result['detected_animals'] else 'None'
                processed_path = detection_result['processed_path']
                
                logger.info(f"Detection complete: {human_count} humans, {animal_count} animals")
                
                # Save to database
                user_id = session.get('user_id')
                detection_record = DetectionHistory.create_detection(
                    user_id=user_id,
                    detection_type='upload',
                    human_count=human_count,
                    animal_count=animal_count,
                    detected_animals=detected_animals,
                    filename=unique_filename,
                    file_type=file_type,
                    processed_path=processed_path,
                    detection_details=json.dumps(detection_result)
                )
                
                # Create in-app notification
                notification = NotificationManager.create_detection_notification(
                    user_id=user_id,
                    detection_data={
                        'human_count': human_count,
                        'animal_count': animal_count,
                        'detected_animals': detection_result['detected_animals'],
                        'detection_type': 'upload'
                    }
                )
                logger.info(f"In-app notification created: {notification['title']}")
                
                # Send email alert if any detection
                if human_count > 0 or animal_count > 0:
                    from app.models.user import User
                    user = User.query.get(user_id)
                    
                    email_success, email_msg = EmailService.send_detection_alert(
                        user_email=user.email,
                        admin_email=current_app.config.get('ALERT_EMAIL'),
                        detection_type='upload',
                        human_count=human_count,
                        animal_count=animal_count,
                        detected_animals=detected_animals,
                        timestamp=detection_record.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                    )
                    
                    if email_success:
                        logger.info(f"Detection alert email sent to {user.email}")
                    else:
                        logger.warning(f"Failed to send detection alert: {email_msg}")
                
                # Prepare processed file path for display
                processed_filename = os.path.basename(processed_path)
                processed_url = f'/static/processed/{processed_filename}'
                
                flash('Detection complete! Notifications sent.', 'success')
                
                return render_template(
                    'detection/upload_result.html',
                    detection=detection_record,
                    processed_url=processed_url,
                    file_type=file_type
                )
            else:
                flash('Detection failed. Please try again.', 'error')
                logger.error("Detection processing failed")
                return redirect(request.url)
        else:
            flash('Invalid file format', 'error')
            return redirect(request.url)
    
    return render_template('detection/upload.html')


@detection_bp.route('/history')
@login_required
def history():
    """Detection history page"""
    user_id = session.get('user_id')
    user_type = session.get('user_type')
    
    # Admin can see all detections
    if user_type == 'admin':
        detections = DetectionHistory.query.order_by(DetectionHistory.timestamp.desc()).all()
    else:
        detections = DetectionHistory.get_user_detections(user_id)
    
    return render_template('detection/history.html', detections=detections)


@detection_bp.route('/api/detect-frame', methods=['POST'])
@login_required
def detect_frame():
    """API endpoint for real-time frame detection"""
    try:
        # Get frame data
        data = request.get_json()
        
        if not data or 'frame' not in data:
            return jsonify({'error': 'No frame data'}), 400
        
        # Decode base64 frame
        import base64
        import numpy as np
        
        frame_data = data['frame'].split(',')[1]
        frame_bytes = base64.b64decode(frame_data)
        nparr = np.frombuffer(frame_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({'error': 'Invalid frame data'}), 400
        
        # Load model
        if not detector.load_model():
            return jsonify({'error': 'Model loading failed'}), 500
        
        # Perform detection
        results = detector.model(frame, conf=detector.confidence_threshold, verbose=False)[0]
        detection_data = detector._process_results(results)
        
        # Get annotated frame
        annotated_frame = results.plot()
        
        # Encode frame back to base64
        _, buffer = cv2.imencode('.jpg', annotated_frame)
        frame_base64 = base64.b64encode(buffer).decode('utf-8')
        
        # Check if detection occurred
        has_detection = detection_data['human_count'] > 0 or detection_data['animal_count'] > 0
        
        return jsonify({
            'success': True,
            'frame': f'data:image/jpeg;base64,{frame_base64}',
            'human_count': detection_data['human_count'],
            'animal_count': detection_data['animal_count'],
            'detected_animals': detection_data['detected_animals'],
            'has_detection': has_detection
        })
        
    except Exception as e:
        logger.error(f"Frame detection error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@detection_bp.route('/api/save-detection', methods=['POST'])
@login_required
def save_detection():
    """API endpoint to save real-time detection with notifications"""
    try:
        data = request.get_json()
        
        user_id = session.get('user_id')
        human_count = data.get('human_count', 0)
        animal_count = data.get('animal_count', 0)
        detected_animals = ', '.join(data.get('detected_animals', [])) if data.get('detected_animals') else 'None'
        
        # Save to database
        detection_record = DetectionHistory.create_detection(
            user_id=user_id,
            detection_type='realtime',
            human_count=human_count,
            animal_count=animal_count,
            detected_animals=detected_animals
        )
        
        logger.info(f"Real-time detection saved: ID {detection_record.id}")
        
        # Create in-app notification
        notification = NotificationManager.create_detection_notification(
            user_id=user_id,
            detection_data={
                'human_count': human_count,
                'animal_count': animal_count,
                'detected_animals': data.get('detected_animals', []),
                'detection_type': 'realtime'
            }
        )
        
        # Send email alert
        from app.models.user import User
        from flask import current_app
        
        user = User.query.get(user_id)
        email_success, email_msg = EmailService.send_detection_alert(
            user_email=user.email,
            admin_email=current_app.config.get('ALERT_EMAIL'),
            detection_type='realtime',
            human_count=human_count,
            animal_count=animal_count,
            detected_animals=detected_animals,
            timestamp=detection_record.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        )
        
        if email_success:
            logger.info("Detection alert emails sent successfully")
        
        return jsonify({
            'success': True,
            'message': 'Detection saved and notifications sent',
            'notification': notification
        })
        
    except Exception as e:
        logger.error(f"Save detection error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@detection_bp.route('/api/view/<int:detection_id>')
@login_required
def view_detection(detection_id):
    """API endpoint to view detection details"""
    try:
        detection = DetectionHistory.query.get_or_404(detection_id)
        
        # Ensure user owns this detection or is admin
        if detection.user_id != session['user_id'] and session.get('user_type') != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Get processed file info
        processed_filename = os.path.basename(detection.processed_path) if detection.processed_path else None
        
        return jsonify({
            'success': True,
            'detection': {
                'id': detection.id,
                'timestamp': detection.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'detection_type': detection.detection_type,
                'human_count': detection.human_count,
                'animal_count': detection.animal_count,
                'detected_animals': detection.detected_animals,
                'filename': detection.filename,
                'file_type': detection.file_type,
                'processed_filename': processed_filename,
                'processed_url': f'/static/processed/{processed_filename}' if processed_filename else None
            }
        })
        
    except Exception as e:
        logger.error(f"View detection error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@detection_bp.route('/api/notifications')
@login_required
def get_notifications():
    """API endpoint to get user notifications"""
    try:
        user_id = session.get('user_id')
        limit = request.args.get('limit', 10, type=int)
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        
        notifications = NotificationManager.get_user_notifications(
            user_id=user_id,
            unread_only=unread_only,
            limit=limit
        )
        
        return jsonify({
            'success': True,
            'notifications': notifications,
            'count': len(notifications)
        })
        
    except Exception as e:
        logger.error(f"Get notifications error: {str(e)}")
        return jsonify({'error': str(e)}), 500
           