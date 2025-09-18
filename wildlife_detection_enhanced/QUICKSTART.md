# 🚀 QUICK START GUIDE

## Wildlife Animal Detection & Alert System

### ⚡ Fast Installation (5 Minutes)

#### Windows:
```
1. Double-click install.bat
2. Edit .env file (add your Gmail credentials)
3. Run: venv\Scripts\activate.bat
4. Run: python run.py
5. Open browser: http://localhost:5000
```

#### Linux/Mac:
```
1. Run: bash install.sh
2. Edit .env file (add your Gmail credentials)
3. Run: source venv/bin/activate
4. Run: python run.py
5. Open browser: http://localhost:5000
```

### 📧 Gmail Setup (Required)

1. Go to: https://myaccount.google.com/security
2. Enable 2-Step Verification
3. Click "App Passwords"
4. Generate new password for "Mail"
5. Copy password to .env file:
   ```
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=xxxx-xxxx-xxxx-xxxx
   ALERT_EMAIL=recipient@example.com
   ```

### 🔑 Default Login

**Admin Account:**
- Email: `admin@wildlife.com`
- Password: `admin123`

**⚠️ CHANGE PASSWORD AFTER FIRST LOGIN!**

### 📱 First Time User Flow

1. **Register New User**
   - Go to registration page
   - Enter name, email, password
   - Check email for OTP code
   - Verify OTP to activate account

2. **Login**
   - Use registered credentials
   - Access dashboard

3. **Start Detection**
   - Real-time: Allow camera access
   - Upload: Select image/video file
   - View results and history

### 🎯 Key Features

✅ Real-time webcam detection  
✅ Image & video upload analysis  
✅ Email alerts on detection  
✅ Detection history tracking  
✅ Admin user management  
✅ Professional UI/UX  

### 🐛 Troubleshooting

**Camera not working?**
- Allow camera permissions in browser
- Use Chrome/Firefox
- Check if other apps are using camera

**Email not sending?**
- Verify Gmail app password (not regular password)
- Check SMTP settings in .env
- Ensure 2FA is enabled on Gmail

**Database error?**
- Delete instance/wildlife_detection.db
- Restart application

**Model not loading?**
- Ensure internet connection (first run downloads model)
- Check disk space (~100MB needed)

### 📊 Supported File Types

**Images:** JPG, PNG, JPEG, GIF  
**Videos:** MP4, AVI, MOV, MKV  

**Max size:** 100MB per file

### 🎨 What Gets Detected?

**Humans:** Person detection

**Animals:** 
- Dog, Cat, Bird
- Horse, Cow, Sheep
- Elephant, Bear, Zebra
- Giraffe, and more...

### 📞 Support

For issues:
1. Check README.md for detailed docs
2. Review .env configuration
3. Check logs/ directory for errors

### 🎓 Perfect For:

- Final year projects
- Hackathons
- Portfolio showcase
- Wildlife monitoring
- Security applications
- AI/ML demonstrations

---

**Enjoy your Wildlife Detection System! 🐾**
      