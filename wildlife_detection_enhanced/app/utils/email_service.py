"""
Enhanced Email Service Module
Handles all email communications with improved templates and notification system
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from flask import current_app
import logging
from datetime import datetime
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailService:
    """Enhanced email service for all system notifications"""
    
    @staticmethod
    def send_email(to_email, subject, html_content, attachments=None):
        """
        Send email using SMTP with optional attachments
        
        Args:
            to_email (str): Recipient email address
            subject (str): Email subject
            html_content (str): HTML email content
            attachments (list): Optional list of file paths to attach
        
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            smtp_server = current_app.config['SMTP_SERVER']
            smtp_port = current_app.config['SMTP_PORT']
            smtp_username = current_app.config['SMTP_USERNAME']
            smtp_password = current_app.config['SMTP_PASSWORD']
            
            # Validate SMTP configuration
            if not all([smtp_server, smtp_username, smtp_password]):
                logger.error("SMTP configuration incomplete")
                return False, "Email service not configured"
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = smtp_username
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Attach HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Attach files if provided
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, 'rb') as f:
                            img = MIMEImage(f.read())
                            img.add_header('Content-Disposition', 'attachment', 
                                         filename=os.path.basename(file_path))
                            msg.attach(img)
            
            # Send email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True, "Email sent successfully"
            
        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP authentication failed")
            return False, "Email authentication failed"
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {str(e)}")
            return False, f"Email sending failed: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error sending email: {str(e)}")
            return False, f"Email sending failed: {str(e)}"
    
    @staticmethod
    def send_welcome_email(to_email, user_name):
        """
        Send welcome email to newly registered user
        
        Args:
            to_email (str): User's email
            user_name (str): User's name
        
        Returns:
            tuple: (success: bool, message: str)
        """
        subject = "Welcome to Wildlife Detection System! 🐾"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    max-width: 600px;
                    margin: 30px auto;
                    background-color: #ffffff;
                    border-radius: 10px;
                    overflow: hidden;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 40px 30px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 28px;
                }}
                .logo {{
                    font-size: 64px;
                    margin-bottom: 10px;
                }}
                .content {{
                    padding: 40px 30px;
                }}
                .welcome-box {{
                    background: linear-gradient(135deg, #f093fb 0%, #f5576c 20%, #ffa726 100%);
                    border-radius: 8px;
                    padding: 30px;
                    text-align: center;
                    color: white;
                    margin: 25px 0;
                }}
                .welcome-box h2 {{
                    margin: 0 0 15px 0;
                    font-size: 24px;
                }}
                .features {{
                    background-color: #f8f9fa;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 25px 0;
                }}
                .feature-item {{
                    padding: 10px 0;
                    border-bottom: 1px solid #e0e0e0;
                }}
                .feature-item:last-child {{
                    border-bottom: none;
                }}
                .feature-icon {{
                    font-size: 24px;
                    margin-right: 10px;
                }}
                .cta-button {{
                    display: inline-block;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 15px 40px;
                    text-decoration: none;
                    border-radius: 25px;
                    font-weight: bold;
                    margin: 20px 0;
                }}
                .footer {{
                    background-color: #f8f9fa;
                    padding: 20px;
                    text-align: center;
                    font-size: 12px;
                    color: #6c757d;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">🐾</div>
                    <h1>Wildlife Detection System</h1>
                </div>
                
                <div class="content">
                    <div class="welcome-box">
                        <h2>Welcome Aboard, {user_name}! 🎉</h2>
                        <p style="margin: 0; font-size: 16px;">Your account has been successfully created!</p>
                    </div>
                    
                    <p style="font-size: 16px; line-height: 1.6;">
                        Thank you for joining our Wildlife Detection community. You now have access to 
                        cutting-edge AI-powered animal detection technology.
                    </p>
                    
                    <div class="features">
                        <h3 style="margin-top: 0;">🚀 What You Can Do Now:</h3>
                        
                        <div class="feature-item">
                            <span class="feature-icon">📹</span>
                            <strong>Real-time Detection:</strong> Monitor live camera feeds with instant AI detection
                        </div>
                        
                        <div class="feature-item">
                            <span class="feature-icon">📤</span>
                            <strong>Upload Analysis:</strong> Analyze images and videos for wildlife identification
                        </div>
                        
                        <div class="feature-item">
                            <span class="feature-icon">🔔</span>
                            <strong>Smart Alerts:</strong> Get instant notifications when animals are detected
                        </div>
                        
                        <div class="feature-item">
                            <span class="feature-icon">📊</span>
                            <strong>Detection History:</strong> Track all your detection events and analytics
                        </div>
                        
                        <div class="feature-item">
                            <span class="feature-icon">🎨</span>
                            <strong>Custom Themes:</strong> Personalize your dashboard with dark/light modes
                        </div>
                    </div>
                    
                    <div style="text-align: center;">
                        <a href="http://localhost:5000/auth/login" class="cta-button">
                            Login to Dashboard →
                        </a>
                    </div>
                    
                    <p style="margin-top: 30px; color: #6c757d; font-size: 14px;">
                        <strong>Need Help?</strong><br>
                        Check out our documentation or contact support at any time.
                    </p>
                </div>
                
                <div class="footer">
                    <p><strong>Wildlife Detection & Alert System</strong></p>
                    <p>Advanced AI Technology for Wildlife Monitoring</p>
                    <p style="margin-top: 10px;">
                        This is an automated email, please do not reply directly.<br>
                        © {datetime.now().year} Wildlife Detection System. All rights reserved.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return EmailService.send_email(to_email, subject, html_content)
    
    @staticmethod
    def send_otp_email(to_email, otp_code, user_name):
        """
        Send OTP verification email
        
        Args:
            to_email (str): Recipient email
            otp_code (str): 6-digit OTP code
            user_name (str): User's name
        
        Returns:
            tuple: (success: bool, message: str)
        """
        subject = "Wildlife Detection System - Email Verification"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    max-width: 600px;
                    margin: 30px auto;
                    background-color: #ffffff;
                    border-radius: 10px;
                    overflow: hidden;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                .content {{
                    padding: 40px 30px;
                }}
                .otp-box {{
                    background-color: #f8f9fa;
                    border: 2px dashed #667eea;
                    border-radius: 8px;
                    padding: 20px;
                    text-align: center;
                    margin: 25px 0;
                }}
                .otp-code {{
                    font-size: 36px;
                    font-weight: bold;
                    color: #667eea;
                    letter-spacing: 8px;
                }}
                .footer {{
                    background-color: #f8f9fa;
                    padding: 20px;
                    text-align: center;
                    font-size: 12px;
                    color: #6c757d;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🐾 Wildlife Detection System</h1>
                </div>
                <div class="content">
                    <h2>Hello {user_name}!</h2>
                    <p>Thank you for registering with Wildlife Detection System.</p>
                    <p>Your One-Time Password (OTP) for email verification is:</p>
                    <div class="otp-box">
                        <div class="otp-code">{otp_code}</div>
                    </div>
                    <p><strong>This OTP will expire in 10 minutes.</strong></p>
                    <p>If you didn't request this verification, please ignore this email.</p>
                </div>
                <div class="footer">
                    <p>Wildlife Detection & Alert System</p>
                    <p>This is an automated email, please do not reply.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return EmailService.send_email(to_email, subject, html_content)
    
    @staticmethod
    def send_detection_alert(user_email, admin_email, detection_type, human_count, 
                           animal_count, detected_animals, timestamp=None):
        """
        Send detection alert email to both user and admin
        
        Args:
            user_email (str): User's email
            admin_email (str): Admin alert email
            detection_type (str): Type of detection (realtime/upload)
            human_count (int): Number of humans detected
            animal_count (int): Number of animals detected
            detected_animals (str): Comma-separated list of detected animals
            timestamp (str): Detection timestamp
        
        Returns:
            tuple: (success: bool, message: str)
        """
        if timestamp is None:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        subject = "🚨 Wildlife Detection Alert - New Detection Event"
        
        animal_list = detected_animals if detected_animals else "None"
        detection_mode = "Real-time Camera" if detection_type == "realtime" else "Uploaded File"
        
        # Determine alert level
        if human_count > 0 and animal_count > 0:
            alert_level = "HIGH PRIORITY"
            alert_color = "#dc3545"
        elif human_count > 0:
            alert_level = "MEDIUM PRIORITY"
            alert_color = "#ffc107"
        else:
            alert_level = "NORMAL"
            alert_color = "#28a745"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    max-width: 600px;
                    margin: 30px auto;
                    background-color: #ffffff;
                    border-radius: 10px;
                    overflow: hidden;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                }}
                .header {{
                    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                .alert-icon {{
                    font-size: 48px;
                    margin-bottom: 10px;
                    animation: pulse 2s infinite;
                }}
                @keyframes pulse {{
                    0%, 100% {{ transform: scale(1); }}
                    50% {{ transform: scale(1.1); }}
                }}
                .content {{
                    padding: 40px 30px;
                }}
                .alert-badge {{
                    display: inline-block;
                    background-color: {alert_color};
                    color: white;
                    padding: 8px 20px;
                    border-radius: 20px;
                    font-weight: bold;
                    font-size: 12px;
                    margin-bottom: 20px;
                }}
                .detection-box {{
                    background-color: #fff3cd;
                    border-left: 4px solid #ffc107;
                    padding: 20px;
                    margin: 20px 0;
                    border-radius: 4px;
                }}
                .stat {{
                    display: inline-block;
                    margin: 10px 20px 10px 0;
                    padding: 15px 25px;
                    background-color: #f8f9fa;
                    border-radius: 8px;
                    text-align: center;
                    min-width: 120px;
                }}
                .stat-number {{
                    font-size: 32px;
                    font-weight: bold;
                    color: #f5576c;
                }}
                .stat-label {{
                    font-size: 14px;
                    color: #6c757d;
                    margin-top: 5px;
                }}
                .info-row {{
                    padding: 12px 0;
                    border-bottom: 1px solid #e0e0e0;
                }}
                .info-row:last-child {{
                    border-bottom: none;
                }}
                .info-label {{
                    font-weight: bold;
                    color: #495057;
                    display: inline-block;
                    width: 150px;
                }}
                .footer {{
                    background-color: #f8f9fa;
                    padding: 20px;
                    text-align: center;
                    font-size: 12px;
                    color: #6c757d;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="alert-icon">🚨</div>
                    <h1>Detection Alert!</h1>
                    <div class="alert-badge">{alert_level}</div>
                </div>
                <div class="content">
                    <div class="detection-box">
                        <h3 style="margin-top: 0;">⚠️ New Detection Event</h3>
                        <p>A detection event has been triggered in the Wildlife Detection System.</p>
                    </div>
                    
                    <h3>Detection Statistics:</h3>
                    <div style="margin: 30px 0;">
                        <div class="stat">
                            <div class="stat-number">{human_count}</div>
                            <div class="stat-label">👤 Humans</div>
                        </div>
                        <div class="stat">
                            <div class="stat-number">{animal_count}</div>
                            <div class="stat-label">🦁 Animals</div>
                        </div>
                    </div>
                    
                    <h3>Detection Details:</h3>
                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px;">
                        <div class="info-row">
                            <span class="info-label">🕒 Timestamp:</span>
                            <span>{timestamp}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">📹 Detection Mode:</span>
                            <span>{detection_mode}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">🐾 Detected Species:</span>
                            <span style="color: #667eea; font-weight: bold;">{animal_list}</span>
                        </div>
                    </div>
                    
                    <p style="margin-top: 30px; padding: 15px; background-color: #e7f3ff; border-left: 4px solid #2196f3; border-radius: 4px;">
                        <strong>💡 Note:</strong> This alert was automatically generated by the AI detection system. 
                        Check your dashboard for detailed results and processed media.
                    </p>
                </div>
                <div class="footer">
                    <p><strong>Wildlife Detection & Alert System</strong></p>
                    <p>Advanced AI-Powered Wildlife Monitoring</p>
                    <p style="margin-top: 10px;">
                        This is an automated alert, please do not reply.<br>
                        © {datetime.now().year} Wildlife Detection System
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Send to user
        user_success, user_msg = EmailService.send_email(user_email, subject, html_content)
        logger.info(f"User alert email: {user_msg}")
        
        # Send to admin if configured and different from user
        if admin_email and admin_email != user_email:
            admin_success, admin_msg = EmailService.send_email(admin_email, subject, html_content)
            logger.info(f"Admin alert email: {admin_msg}")
        
        return user_success, user_msg
       