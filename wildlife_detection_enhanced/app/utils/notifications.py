"""
Notification System Module
Handles in-app notifications and real-time alerts
"""

from flask import session
from datetime import datetime
import json
from app import db


class NotificationManager:
    """Manages in-app notifications for detection events"""
    
    @staticmethod
    def create_notification(user_id, title, message, notification_type='info', data=None):
        """
        Create a new notification
        
        Args:
            user_id (int): User ID
            title (str): Notification title
            message (str): Notification message
            notification_type (str): Type (success, info, warning, danger)
            data (dict): Additional notification data
        
        Returns:
            dict: Notification object
        """
        notification = {
            'id': datetime.now().timestamp(),
            'user_id': user_id,
            'title': title,
            'message': message,
            'type': notification_type,
            'data': data or {},
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'read': False
        }
        
        # Store in session for in-memory notifications
        if 'notifications' not in session:
            session['notifications'] = []
        
        session['notifications'].append(notification)
        session.modified = True
        
        return notification
    
    @staticmethod
    def create_detection_notification(user_id, detection_data):
        """
        Create detection-specific notification
        
        Args:
            user_id (int): User ID
            detection_data (dict): Detection information
        
        Returns:
            dict: Notification object
        """
        human_count = detection_data.get('human_count', 0)
        animal_count = detection_data.get('animal_count', 0)
        detected_animals = detection_data.get('detected_animals', [])
        detection_type = detection_data.get('detection_type', 'upload')
        
        # Build notification message
        if human_count > 0 and animal_count > 0:
            title = "🚨 High Priority Detection!"
            message = f"Detected {human_count} human(s) and {animal_count} animal(s)"
            notif_type = 'danger'
        elif human_count > 0:
            title = "⚠️ Human Detected!"
            message = f"Detected {human_count} human(s)"
            notif_type = 'warning'
        elif animal_count > 0:
            title = "🐾 Animal Detected!"
            animals_str = ', '.join(detected_animals[:3])
            if len(detected_animals) > 3:
                animals_str += f' and {len(detected_animals) - 3} more'
            message = f"Detected {animal_count} animal(s): {animals_str}"
            notif_type = 'info'
        else:
            title = "✓ Detection Complete"
            message = "No detections found"
            notif_type = 'success'
        
        # Add detection mode to message
        mode = "Real-time Camera" if detection_type == "realtime" else "Uploaded File"
        message += f" ({mode})"
        
        return NotificationManager.create_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notif_type,
            data={
                'human_count': human_count,
                'animal_count': animal_count,
                'detected_animals': detected_animals,
                'detection_type': detection_type
            }
        )
    
    @staticmethod
    def get_user_notifications(user_id, unread_only=False, limit=10):
        """
        Get notifications for a user
        
        Args:
            user_id (int): User ID
            unread_only (bool): Return only unread notifications
            limit (int): Maximum notifications to return
        
        Returns:
            list: List of notifications
        """
        if 'notifications' not in session:
            return []
        
        notifications = [
            n for n in session['notifications']
            if n['user_id'] == user_id
        ]
        
        if unread_only:
            notifications = [n for n in notifications if not n['read']]
        
        # Sort by timestamp (newest first)
        notifications.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return notifications[:limit]
    
    @staticmethod
    def mark_as_read(notification_id):
        """
        Mark notification as read
        
        Args:
            notification_id: Notification ID
        
        Returns:
            bool: Success status
        """
        if 'notifications' not in session:
            return False
        
        for notification in session['notifications']:
            if notification['id'] == notification_id:
                notification['read'] = True
                session.modified = True
                return True
        
        return False
    
    @staticmethod
    def clear_notifications(user_id):
        """
        Clear all notifications for a user
        
        Args:
            user_id (int): User ID
        
        Returns:
            int: Number of notifications cleared
        """
        if 'notifications' not in session:
            return 0
        
        original_count = len(session['notifications'])
        session['notifications'] = [
            n for n in session['notifications']
            if n['user_id'] != user_id
        ]
        session.modified = True
        
        return original_count - len(session['notifications'])
          