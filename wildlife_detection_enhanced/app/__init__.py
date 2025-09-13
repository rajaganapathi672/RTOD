"""
Flask Application Factory
Initializes and configures the Flask application with all extensions
"""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config

# Initialize extensions
db = SQLAlchemy()


def create_app(config_name='default'):
    """
    Application factory pattern
    Creates and configures the Flask application
    
    Args:
        config_name (str): Configuration environment name
    
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Ensure upload and processed folders exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)
    
    # Initialize extensions with app
    db.init_app(app)
    
    # Register blueprints
    from app.blueprints.auth import auth_bp
    from app.blueprints.dashboard import dashboard_bp
    from app.blueprints.detection import detection_bp
    from app.blueprints.admin import admin_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(detection_bp, url_prefix='/detection')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Create database tables
    with app.app_context():
        from app.models.user import User, Admin, OTP
        from app.models.detection import DetectionHistory
        db.create_all()
        
        # Create default admin if not exists
        create_default_admin(app)
    
    # Register custom filters
    import json
    @app.template_filter('from_json')
    def from_json_filter(value):
        try:
            return json.loads(value)
        except (ValueError, TypeError):
            return []

    # Register error handlers
    register_error_handlers(app)
    
    # Root route
    @app.route('/')
    def index():
        from flask import redirect, url_for
        return redirect(url_for('auth.login'))
    
    return app


def create_default_admin(app):
    """
    Create default admin account if it doesn't exist
    
    Args:
        app: Flask application instance
    """
    from app.models.user import Admin
    from werkzeug.security import generate_password_hash
    
    admin_email = app.config['ADMIN_EMAIL']
    admin_password = app.config['ADMIN_PASSWORD']
    
    existing_admin = Admin.query.filter_by(email=admin_email).first()
    
    if not existing_admin:
        admin = Admin(
            name='System Administrator',
            email=admin_email,
            password=generate_password_hash(admin_password, method='pbkdf2:sha256')
        )
        db.session.add(admin)
        db.session.commit()
        print(f"Default admin created: {admin_email}")


def register_error_handlers(app):
    """
    Register error handlers for common HTTP errors
    
    Args:
        app: Flask application instance
    """
    from flask import render_template
    
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403
        