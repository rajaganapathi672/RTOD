"""
Enhanced User and Admin Database Models
Includes theme preferences and enhanced security
"""

from datetime import datetime, timedelta
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
import secrets


class User(db.Model):
    """
    Enhanced User model with theme preferences
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    theme_preference = db.Column(db.String(10), default='light')  # 'light' or 'dark'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    detections = db.relationship('DetectionHistory', backref='user', lazy=True, 
                                cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def set_password(self, password):
        """Hash and set user password"""
        self.password = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password):
        """Verify password against hash"""
        return check_password_hash(self.password, password)
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def set_theme(self, theme):
        """Set user theme preference"""
        if theme in ['light', 'dark']:
            self.theme_preference = theme
            db.session.commit()
            return True
        return False


class Admin(db.Model):
    """
    Admin model for system administrators
    """
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Admin {self.email}>'
    
    def set_password(self, password):
        """Hash and set admin password"""
        self.password = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password):
        """Verify password against hash"""
        return check_password_hash(self.password, password)
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()
        db.session.commit()


class OTP(db.Model):
    """
    One-Time Password model for email verification
    """
    __tablename__ = 'otps'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, index=True)
    otp_code = db.Column(db.String(6), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    
    # Store temporary user data until verification
    temp_name = db.Column(db.String(100))
    temp_password = db.Column(db.String(255))
    
    def __repr__(self):
        return f'<OTP {self.email}>'
    
    @staticmethod
    def generate_otp():
        """Generate a 6-digit OTP"""
        return ''.join([str(secrets.randbelow(10)) for _ in range(6)])
    
    def is_expired(self):
        """Check if OTP has expired"""
        return datetime.utcnow() > self.expires_at
    
    def verify(self, otp_code):
        """Verify OTP code"""
        if self.is_used:
            return False, "OTP already used"
        if self.is_expired():
            return False, "OTP has expired"
        if self.otp_code != otp_code:
            return False, "Invalid OTP"
        return True, "OTP verified"
    
    @classmethod
    def create_otp(cls, email, name, password, expiry_minutes=10):
        """
        Create a new OTP entry
        
        Args:
            email (str): User email
            name (str): User name
            password (str): Hashed password
            expiry_minutes (int): OTP validity duration
        
        Returns:
            OTP: Created OTP instance
        """
        # Delete any existing OTPs for this email
        cls.query.filter_by(email=email).delete()
        
        otp_code = cls.generate_otp()
        expires_at = datetime.utcnow() + timedelta(minutes=expiry_minutes)
        
        otp = cls(
            email=email,
            otp_code=otp_code,
            expires_at=expires_at,
            temp_name=name,
            temp_password=password
        )
        
        db.session.add(otp)
        db.session.commit()
        
        return otp
               