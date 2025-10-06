"""
Enhanced Authentication Blueprint
Handles user registration with welcome emails, login, OTP verification, and logout
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from app import db
from app.models.user import User, Admin, OTP
from app.utils.email_service import EmailService
from werkzeug.security import generate_password_hash
from datetime import datetime
import re
import logging

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)


def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password):
    """Validate password strength"""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    return True, ""


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page with OTP verification"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        if not all([name, email, password, confirm_password]):
            flash('All fields are required', 'error')
            return render_template('auth/register.html')
        
        if not validate_email(email):
            flash('Invalid email format', 'error')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('auth/register.html')
        
        is_valid, msg = validate_password(password)
        if not is_valid:
            flash(msg, 'error')
            return render_template('auth/register.html')
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered', 'error')
            return render_template('auth/register.html')
        
        # Hash password
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        
        # Create OTP
        from flask import current_app
        otp_expiry = current_app.config['OTP_EXPIRY_MINUTES']
        otp = OTP.create_otp(email, name, hashed_password, otp_expiry)
        
        # Send OTP email
        success, message = EmailService.send_otp_email(email, otp.otp_code, name)
        
        if success:
            flash('OTP sent to your email. Please verify to complete registration.', 'success')
            logger.info(f"OTP sent successfully to {email}")
            return redirect(url_for('auth.verify_otp', email=email))
        else:
            flash(f'Failed to send OTP: {message}', 'error')
            logger.error(f"Failed to send OTP to {email}: {message}")
            return render_template('auth/register.html')
    
    return render_template('auth/register.html')


@auth_bp.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    """OTP verification page"""
    email = request.args.get('email') or request.form.get('email')
    
    if not email:
        flash('Invalid verification request', 'error')
        return redirect(url_for('auth.register'))
    
    if request.method == 'POST':
        otp_code = request.form.get('otp', '').strip()
        
        if not otp_code:
            flash('Please enter OTP', 'error')
            return render_template('auth/verify_otp.html', email=email)
        
        # Find OTP
        otp = OTP.query.filter_by(email=email, is_used=False).order_by(OTP.created_at.desc()).first()
        
        if not otp:
            flash('No OTP found. Please register again.', 'error')
            return redirect(url_for('auth.register'))
        
        # Verify OTP
        is_valid, message = otp.verify(otp_code)
        
        if is_valid:
            # Create user account
            user = User(
                name=otp.temp_name,
                email=otp.email,
                password=otp.temp_password,
                is_verified=True
            )
            
            db.session.add(user)
            otp.is_used = True
            db.session.commit()
            
            logger.info(f"User registered successfully: {user.email}")
            
            # Send welcome email
            welcome_success, welcome_msg = EmailService.send_welcome_email(otp.email, otp.temp_name)
            if welcome_success:
                logger.info(f"Welcome email sent to {otp.email}")
            else:
                logger.warning(f"Failed to send welcome email to {otp.email}: {welcome_msg}")
            
            flash('Registration successful! Welcome email sent. Please login.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(message, 'error')
            return render_template('auth/verify_otp.html', email=email)
    
    return render_template('auth/verify_otp.html', email=email)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        if not all([email, password]):
            flash('All fields are required', 'error')
            return render_template('auth/login.html')
        
        # Find user
        user = User.query.filter_by(email=email).first()
        
        if user and user.is_verified and user.check_password(password):
            # Set session
            session.clear()
            session['user_id'] = user.id
            session['user_type'] = 'user'
            session['user_name'] = user.name
            session['user_email'] = user.email
            session['theme'] = user.theme_preference or 'light'  # Load theme preference
            session.permanent = True
            
            # Update last login
            user.update_last_login()
            
            logger.info(f"User logged in: {user.email}")
            flash(f'Welcome back, {user.name}!', 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash('Invalid email or password', 'error')
            logger.warning(f"Failed login attempt for: {email}")
            return render_template('auth/login.html')
    
    return render_template('auth/login.html')


@auth_bp.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        if not all([email, password]):
            flash('All fields are required', 'error')
            return render_template('auth/admin_login.html')
        
        # Find admin
        admin = Admin.query.filter_by(email=email).first()
        
        if admin and admin.check_password(password):
            # Set session
            session.clear()
            session['user_id'] = admin.id
            session['user_type'] = 'admin'
            session['user_name'] = admin.name
            session['user_email'] = admin.email
            session['theme'] = 'light'  # Default admin theme
            session.permanent = True
            
            # Update last login
            admin.update_last_login()
            
            logger.info(f"Admin logged in: {admin.email}")
            flash(f'Welcome, Admin {admin.name}!', 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash('Invalid admin credentials', 'error')
            logger.warning(f"Failed admin login attempt for: {email}")
            return render_template('auth/admin_login.html')
    
    return render_template('auth/admin_login.html')


@auth_bp.route('/logout')
def logout():
    """Logout user"""
    user_type = session.get('user_type', 'user')
    user_email = session.get('user_email', 'unknown')
    
    logger.info(f"User logged out: {user_email}")
    session.clear()
    flash('You have been logged out successfully', 'success')
    
    if user_type == 'admin':
        return redirect(url_for('auth.admin_login'))
    return redirect(url_for('auth.login'))


@auth_bp.route('/resend-otp', methods=['POST'])
def resend_otp():
    """Resend OTP"""
    email = request.form.get('email')
    
    if not email:
        flash('Invalid request', 'error')
        return redirect(url_for('auth.register'))
    
    # Find existing OTP
    old_otp = OTP.query.filter_by(email=email, is_used=False).first()
    
    if not old_otp:
        flash('No pending verification found', 'error')
        return redirect(url_for('auth.register'))
    
    # Create new OTP
    from flask import current_app
    otp_expiry = current_app.config['OTP_EXPIRY_MINUTES']
    otp = OTP.create_otp(email, old_otp.temp_name, old_otp.temp_password, otp_expiry)
    
    # Send OTP email
    success, message = EmailService.send_otp_email(email, otp.otp_code, old_otp.temp_name)
    
    if success:
        flash('New OTP sent to your email', 'success')
        logger.info(f"OTP resent to {email}")
    else:
        flash(f'Failed to send OTP: {message}', 'error')
        logger.error(f"Failed to resend OTP to {email}: {message}")
    
    return redirect(url_for('auth.verify_otp', email=email))


@auth_bp.route('/api/toggle-theme', methods=['POST'])
def toggle_theme():
    """Toggle theme preference (API endpoint)"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    data = request.get_json()
    theme = data.get('theme', 'light')
    
    if theme not in ['light', 'dark']:
        return jsonify({'success': False, 'message': 'Invalid theme'}), 400
    
    # Update session
    session['theme'] = theme
    session.modified = True
    
    # Update database if user (not admin)
    if session.get('user_type') == 'user':
        user = User.query.get(session['user_id'])
        if user:
            user.theme_preference = theme
            db.session.commit()
            logger.info(f"Theme updated for user {user.email}: {theme}")
    
    return jsonify({'success': True, 'theme': theme})
          