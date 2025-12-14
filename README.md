# Real-Time Object Detection (RTOD) 🚀

A powerful, premium web-based object detection application powered by YOLOv8 and Flask.

![Object Detection Demo](https://images.unsplash.com/photo-1555949963-aa79dcee981c?auto=format&fit=crop&q=80&w=2070&ixlib=rb-4.0.3)

## ✨ Features

- **Real-Time Detection**: Live object detection via webcam.
- **Media Upload**: Support for detecting objects in images (JPG, PNG) and videos (MP4, AVI).
- **Premium UI**: Modern Glassmorphism design with smooth animations.
- **Dark/Light Mode**: Seamless theme switching with persistent user preference.
- **Start-of-the-Art Model**: Utilizes YOLOv8 Nano for fast and accurate detection.
- **Responsive Dashboard**: View detection statistics and history.

## 🛠️ Tech Stack

- **Backend**: Python, Flask
- **AI Model**: Ultralytics YOLOv8
- **Frontend**: HTML5, Bootstrap 5.3, Custom CSS (Glassmorphism)
- **Image Processing**: OpenCV

## 🚀 Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/RTOD.git
    cd RTOD
    ```

2.  **Create a virtual environment** (Recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    *Ensure `ultralytics`, `flask`, `opencv-python`, and `werkzeug` are installed.*

4.  **Download Model**:
    Ensure `yolov8n.pt` is present in the root directory. It will be automatically downloaded by Ultralytics if missing, or you can place your custom trained model there.

## 💻 Usage

1.  **Run the application**:
    ```bash
    python app.py
    ```

2.  **Access the Dashboard**:
    Open your browser and navigate to: [http://127.0.0.1:5000](http://127.0.0.1:5000)

3.  **Explore**:
    - **Dashboard**: Overview of your detection history.
    - **Upload**: Drop images or videos to detect objects.
    - **Real-Time**: Enable your webcam for live inference.
    - **Theme**: Click the moon/sun icon in the navbar to toggle themes.

## 📁 Project Structure

```
RTOD/
├── app.py              # Main Flask application
├── verify_model.py     # Script to verify YOLO model independently
├── yolov8n.pt          # YOLOv8 Model weights
├── static/
│   ├── css/
│   │   └── style.css   # Custom Premium Styles
│   └── js/
│       └── script.js   # Client-side logic
├── templates/
│   ├── base.html       # Base layout
│   ├── dashboard.html  # Main dashboard
│   ├── upload.html     # File upload page
│   └── realtime.html   # Webcam page
└── uploads/            # Directory for uploaded and processed files
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open-source and available under the MIT License.
