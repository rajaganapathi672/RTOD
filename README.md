# RTOD (Real-Time Object Detection)

## Overview
RTOD is a web-based application built with **Flask** and **YOLOv8** that provides real-time object detection capabilities. It processes images, videos, and live webcam feeds to identify objects with high accuracy.

## Features
- **Image Detection**: Upload images (JPG, PNG) to detect objects.
- **Video Detection**: Upload video files (MP4, AVI) for frame-by-frame object detection.
- **Real-Time Webcam**: Live object detection using your computer's webcam.
- **Dashboard**: View a history of processed files and results

## Technologies Used
- **Backend**: Flask (Python)
- **Object Detection**: ultralytics (YOLOv8)
- **Image Processing**: OpenCV
- **Frontend**: HTML, CSS, JavaScript.

## Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/rajaganapathi672/RTOD.git
    cd RTOD
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

    *Note: Ensure you have `yolov8n.pt` model file in the project root or update the path in `app.py`.*

## Usage

1.  **Run the application**:
    ```bash
    python app.py
    ```

2.  **Access the web interface**:
    Open your browser and navigate to `http://127.0.0.1:5000`.

3.  **Navigate**:
    - Use the **Upload** page to process files.
    - Use the **Realtime** page for webcam detection.
    - Check the **Dashboard** for past results.

## Project Structure
- `app.py`: Main Flask application file.
- `templates/`: HTML templates for the web interface.
- `static/`: Static assets (CSS, JS).
- `uploads/`: Directory for uploaded and processed files.
