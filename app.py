import os
from flask import Flask, render_template, request, redirect, send_from_directory, Response, jsonify
from werkzeug.utils import secure_filename
from ultralytics import YOLO
import cv2
import time
from datetime import datetime
import threading

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'mp4', 'avi'}
STATIC_FOLDER = 'static'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['STATIC_FOLDER'] = STATIC_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit

# Load YOLO model
model = YOLO("C:/Users/RAJAGANAPATHY/Desktop/RTOD/yolov8n.pt")


# Camera control variables
camera_active = False
camera_lock = threading.Lock()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_frames():
    global camera_active
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    with camera_lock:
        camera_active = True
    
    try:
        while camera_active:
            success, frame = cap.read()
            if not success:
                break
            
            # Perform object detection
            results = model(frame, verbose=False)
            annotated_frame = results[0].plot()
            
            # Convert the frame to JPEG
            ret, buffer = cv2.imencode('.jpg', annotated_frame)
            frame = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    finally:
        cap.release()
        with camera_lock:
            camera_active = False

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), 
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start_camera')
def start_camera():
    global camera_active
    with camera_lock:
        if not camera_active:
            # This will trigger the camera when the first client connects to /video_feed
            return jsonify({'status': 'starting'})
        return jsonify({'status': 'already running'})

@app.route('/stop_camera')
def stop_camera():
    global camera_active
    with camera_lock:
        camera_active = False
    return jsonify({'status': 'stopped'})

@app.route('/detect_objects', methods=['POST'])
def detect_objects():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed. Only JPG, JPEG, PNG, MP4, AVI are supported.'}), 400
    
    try:
        filename = secure_filename(file.filename)
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Run detection
        start_time = time.time()
        
        # Check if file is image or video
        is_video = filename.lower().endswith(('.mp4', '.avi'))
        
        if is_video:
            # Video processing
            cap = cv2.VideoCapture(filepath)
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Prepare video writer for output
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            result_filename = f"result_{timestamp}_{filename}"
            result_path = os.path.join(app.config['UPLOAD_FOLDER'], result_filename)
            
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(result_path, fourcc, fps, (width, height))
            
            frame_count = 0
            detected_objects = []
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                results = model(frame, verbose=False)
                annotated_frame = results[0].plot()
                out.write(annotated_frame)
                
                # Collect detected objects from this frame
                if hasattr(results[0], 'names'):
                    for obj in results[0].boxes.cls:
                        detected_objects.append(results[0].names[int(obj)])
                
                frame_count += 1
            
            cap.release()
            out.release()
            processing_time = round(time.time() - start_time, 2)
            
        else:
            # Image processing
            print(f"Processing image: {filepath}")
            results = model(filepath, conf=0.25, verbose=False)
            
            # Debug: Print detection info
            print(f"Detection results: {len(results)} items")
            if len(results) > 0:
                print(f"Boxes detected: {len(results[0].boxes)}")
                print(f"Classes: {results[0].boxes.cls}")
                print(f"Confidences: {results[0].boxes.conf}")
            
            # Generate result image with boxes
            annotated_frame = results[0].plot()
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            result_filename = f"result_{timestamp}_{filename}"
            result_path = os.path.join(app.config['UPLOAD_FOLDER'], result_filename)
            
            # Save using cv2
            cv2.imwrite(result_path, annotated_frame)
            
            # Get detection stats
            detected_objects = []
            if hasattr(results[0], 'names'):
                for obj in results[0].boxes.cls:
                    detected_objects.append(results[0].names[int(obj)])
            
            processing_time = round(time.time() - start_time, 2)
        
        return jsonify({
            'success': True,
            'original': filename,
            'result': result_filename,
            'processing_time': processing_time,
            'detected_objects': detected_objects,
            'object_count': len(detected_objects),
            'is_video': is_video
        })
        
    except Exception as e:
        app.logger.error(f"Error processing file: {str(e)}")
        return jsonify({
            'error': f'An error occurred during processing: {str(e)}'
        }), 500

@app.route('/')
def dashboard():
    # Get list of processed files
    processed_files = []
    if os.path.exists(UPLOAD_FOLDER):
        for f in os.listdir(UPLOAD_FOLDER):
            if f.startswith('result_'):
                original = f.split('_', 2)[-1]
                processed_files.append({
                    'original': original,
                    'result': f,
                    'timestamp': time.ctime(os.path.getmtime(os.path.join(UPLOAD_FOLDER, f)))
                })
    
    return render_template('dashboard.html', processed_files=processed_files)

@app.route('/upload')
def upload():
    return render_template('upload.html')

@app.route('/realtime')
def realtime():
    return render_template('realtime.html')

@app.route('/results/<filename>')
def results(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)