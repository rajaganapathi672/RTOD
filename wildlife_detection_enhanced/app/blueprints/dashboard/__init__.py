"""
Enhanced Dashboard Blueprint
Dashboard with detection viewing and notification support
"""

from flask import Blueprint, render_template, session, redirect, url_for, flash, jsonify
from app.models.detection import DetectionHistory
from app.utils.notifications import NotificationManager
from functools import wraps
import logging

dashboard_bp = Blueprint('dashboard', __name__)
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


@dashboard_bp.route('/')
@login_required
def index():
    """Enhanced main dashboard page with notifications"""
    user_id = session.get('user_id')
    user_type = session.get('user_type')
    user_name = session.get('user_name')
    theme = session.get('theme', 'light')
    
    # Get detection statistics
    stats = DetectionHistory.get_detection_stats(user_id)
    
    # Get recent detections (with processed paths for viewing)
    recent_detections = DetectionHistory.get_user_detections(user_id, limit=10)
    
    # Get unread notifications count
    notifications = NotificationManager.get_user_notifications(user_id, unread_only=True)
    unread_count = len(notifications)
    
    logger.info(f"Dashboard loaded for user {user_name} ({user_type})")
    
    return render_template(
        'dashboard/index.html',
        user_name=user_name,
        user_type=user_type,
        theme=theme,
        stats=stats,
        recent_detections=recent_detections,
        unread_notifications=unread_count
    )
      