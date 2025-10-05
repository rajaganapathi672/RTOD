# Wildlife Animal Detection & Alert System

A production-grade AI-powered web application for detecting humans and animals in images, videos, and real-time camera feeds using YOLOv8n deep learning model.

## 🎯 Features

### Core Functionality
- **Real-time Detection**: Live webcam monitoring with instant AI detection
- **Upload Detection**: Process images and videos for animal/human detection
- **Email Alerts**: Automatic email notifications when detections occur
- **Detection History**: Complete tracking of all detection events
- **User Management**: Admin panel for managing user accounts

### Security & Authentication
- OTP-based email verification for registration
- Secure password hashing (PBKDF2-SHA256)
- Role-based access control (Admin & User)
- Session-based authentication with secure cookies

### AI/ML Capabilities
- YOLOv8n object detection model
- Real-time inference on video frames
- Multi-class detection (humans + 20 animal species)
- Confidence-based filtering
- Bounding box visualization

## 🏗️ Architecture

### Technology Stack
```
Backend:
- Python 3.10+
- Flask (modular blueprint architecture)
- SQLAlchemy ORM
- Ultralytics YOLOv8n

Frontend:
- HTML5
- CSS3 (modern responsive design)
- Vanilla JavaScript

AI/ML:
- PyTorch
- OpenCV
- YOLO v8n model

Database:
- SQLite (development)
```

### Project Structure
```
wildlife_detection_system/
├── app/
│   ├── blueprints/
│   │   ├── auth/          # Authentication routes
│   │   ├── admin/         # Admin management
│   │   ├── dashboard/     # Dashboard views
│   │   └── detection/     # Detection modules
│   ├── models/
│   │   ├── user.py        # User & Admin models
│   │   └── detection.py   # Detection history model
│   ├── utils/
│   │   ├── detector.py    # YOLO detection service
│   │   └── email_service.py  # Email handling
│   ├── static/
│   │   ├── css/           # Stylesheets
│   │   ├── js/            # JavaScript files
│   │   ├── uploads/       # Uploaded files
│   │   └── processed/     # Processed outputs
│   ├── templates/
│   │   ├── auth/          # Auth pages
│   │   ├── dashboard/     # Dashboard pages
│   │   ├── detection/     # Detection pages
│   │   └── admin/         # Admin pages
│   └── __init__.py        # App factory
├── instance/              # SQLite database
├── logs/                  # Application logs
├── config.py              # Configuration
├── run.py                 # Application entry point
├── requirements.txt       # Dependencies
└── README.md
```

## 🚀 Installation

### Prerequisites
- Python 3.10 or higher
- pip package manager
- Webcam (for real-time detection)
- Gmail account (for email features)

### Step 1: Clone/Extract Project
```bash
# Extract the ZIP file or navigate to project directory
cd wildlife_detection_system
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

**Note**: The first run will automatically download the YOLOv8n model (~6MB).

### Step 4: Configure Environment Variables
```bash
# Copy example env file
cp .env.example .env

# Edit .env file with your settings
```

**Required Configuration** (`.env`):
```env
# Flask
SECRET_KEY=your-secret-key-here

# Email (Gmail)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
ALERT_EMAIL=recipient@example.com

# Admin Account
ADMIN_EMAIL=admin@wildlife.com
ADMIN_PASSWORD=admin123
```

**Gmail App Password Setup**:
1. Go to Google Account Settings
2. Security > 2-Step Verification
3. App Passwords > Generate new app password
4. Use generated password in `.env`

### Step 5: Initialize Database
```bash
# Database will be created automatically on first run
python run.py
```

## 🎮 Usage

### Starting the Application
```bash
python run.py
```

The application will be available at: `http://localhost:5000`

### Default Admin Credentials
```
Email: admin@wildlife.com
Password: admin123
```

**⚠️ IMPORTANT**: Change these credentials after first login!

### User Workflow

#### 1. Registration
1. Navigate to registration page
2. Enter name, email, and password
3. Receive OTP via email
4. Verify OTP to activate account
5. Login with credentials

#### 2. Dashboard
- View detection statistics
- Access detection modules
- See recent detection history

#### 3. Real-time Detection
1. Click "Real-time Detection"
2. Allow camera access
3. Click "Start Detection"
4. System detects and alerts automatically
5. View live stats and detected species

#### 4. Upload Detection
1. Click "Upload Detection"
2. Drag & drop or select file
3. Supported: JPG, PNG, MP4, AVI, MOV, MKV
4. View processed results
5. Automatic email alert if detection occurs

#### 5. Detection History
- View all past detections
- Filter by type, date, species
- Export detection reports

### Admin Features

#### User Management
1. Login as admin
2. Navigate to "User Management"
3. Add/Delete users
4. View user statistics
5. Monitor system usage

## 📊 Detection Report Format

Each detection generates:
- **Human Count**: Number of humans detected
- **Animal Count**: Number of animals detected
- **Species List**: Detected animal types (e.g., dog, cat, elephant)
- **Timestamp**: When detection occurred
- **Detection Type**: Real-time or Upload
- **Processed Media**: Annotated image/video with bounding boxes

## 🔔 Email Alerts

### OTP Verification Email
- Professional HTML template
- 6-digit code
- 10-minute expiration
- Resend option

### Detection Alert Email
- Instant notification
- Detection statistics
- Species breakdown
- Alert timestamp

## 🛠️ Troubleshooting

### Camera Not Working
- Check browser permissions
- Ensure HTTPS or localhost
- Try different browser (Chrome recommended)

### Email Not Sending
- Verify Gmail app password
- Check SMTP settings
- Ensure 2FA is enabled on Gmail

### Model Loading Issues
- First run downloads YOLOv8n automatically
- Ensure internet connection
- Check disk space (~100MB required)

### Database Errors
- Delete `instance/wildlife_detection.db`
- Restart application to recreate

## 🔒 Security Best Practices

1. **Change Default Credentials**
   - Update admin password immediately
   - Use strong, unique passwords

2. **Environment Variables**
   - Never commit `.env` to version control
   - Use secure SECRET_KEY in production

3. **HTTPS in Production**
   - Enable SSL/TLS certificates
   - Set SESSION_COOKIE_SECURE=True

4. **Email Security**
   - Use app-specific passwords
   - Never share SMTP credentials

## 📈 Performance Optimization

### For Real-time Detection
- Lower camera resolution if laggy
- Adjust detection interval (default: 1 second)
- Use GPU if available (PyTorch CUDA)

### For Video Processing
- Longer videos take more time
- Frame sampling every 10th frame
- Progress indicator recommended

## 🎨 Customization

### Changing UI Colors
Edit `app/static/css/style.css`:
```css
:root {
    --primary: #667eea;      /* Main color */
    --secondary: #764ba2;    /* Accent color */
    --success: #48bb78;      /* Success state */
    --danger: #f56565;       /* Error state */
}
```

### Adding New Animal Classes
Edit `app/utils/detector.py`:
```python
ANIMAL_CLASSES = {
    'bird', 'cat', 'dog', 'horse',
    'your-new-animal-here'
}
```

### Adjusting Confidence Threshold
Edit `config.py`:
```python
CONFIDENCE_THRESHOLD = 0.5  # 0.0 to 1.0
```

## 📝 License & Credits

### YOLOv8
- Ultralytics YOLOv8 (AGPL-3.0)
- https://github.com/ultralytics/ultralytics

### COCO Dataset
- Used for pre-trained model
- https://cocodataset.org/

## 🤝 Support

For issues, questions, or contributions:
1. Check troubleshooting section
2. Review configuration
3. Check application logs in `logs/`

## 🌟 Production Deployment

### Recommended Stack
- **Server**: Gunicorn + Nginx
- **Database**: PostgreSQL
- **Storage**: S3 for media files
- **HTTPS**: Let's Encrypt SSL
- **Monitoring**: Application logging

### Environment Variables for Production
```env
FLASK_ENV=production
SECRET_KEY=<strong-random-key>
DATABASE_URI=postgresql://...
SESSION_COOKIE_SECURE=True
```

## 📊 System Requirements

### Minimum
- CPU: 2 cores
- RAM: 4GB
- Storage: 10GB
- Camera: 720p

### Recommended
- CPU: 4 cores
- RAM: 8GB
- Storage: 20GB
- Camera: 1080p
- GPU: NVIDIA CUDA-compatible (optional)

---

**Built with ❤️ for Wildlife Conservation and Security Applications**
            