"""
Admin Blueprint
Handles admin-only features like user management
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from app import db
from app.models.user import User
from werkzeug.security import generate_password_hash
from functools import wraps

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'error')
            return redirect(url_for('auth.admin_login'))
        
        if session.get('user_type') != 'admin':
            flash('Unauthorized access. Admin privileges required.', 'error')
            return redirect(url_for('dashboard.index'))
        
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/users')
@admin_required
def users():
    """User management page"""
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=all_users)


@admin_bp.route('/add-user', methods=['GET', 'POST'])
@admin_required
def add_user():
    """Add new user page"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        # Validation
        if not all([name, email, password]):
            flash('All fields are required', 'error')
            return render_template('admin/add_user.html')
        
        # Check if user exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('User with this email already exists', 'error')
            return render_template('admin/add_user.html')
        
        # Create user
        user = User(
            name=name,
            email=email,
            password=generate_password_hash(password, method='pbkdf2:sha256'),
            is_verified=True  # Admin-created users are auto-verified
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash(f'User {name} added successfully', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/add_user.html')


@admin_bp.route('/delete-user/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    """Delete user"""
    user = User.query.get_or_404(user_id)
    
    # Prevent admin from deleting themselves (if they somehow have a user account)
    if user.email == session.get('user_email'):
        flash('Cannot delete your own account', 'error')
        return redirect(url_for('admin.users'))
    
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User {user.name} deleted successfully', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/api/user/<int:user_id>')
@admin_required
def get_user_api(user_id):
    """Get user details API"""
    user = User.query.get_or_404(user_id)
    
    return jsonify({
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'is_verified': user.is_verified,
        'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'last_login': user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else 'Never'
    })
        