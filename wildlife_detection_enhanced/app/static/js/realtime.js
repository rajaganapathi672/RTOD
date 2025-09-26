/**
 * Real-time Detection JavaScript with Notifications
 */

let video = document.getElementById('webcam');
let canvas = document.getElementById('canvas');
let ctx = canvas.getContext('2d');
let detectionFrame = document.getElementById('detectionFrame');
let startBtn = document.getElementById('startBtn');
let stopBtn = document.getElementById('stopBtn');
let humanCountEl = document.getElementById('humanCount');
let animalCountEl = document.getElementById('animalCount');
let animalsListEl = document.getElementById('animalsList');

let stream = null;
let detectionInterval = null;
let lastDetection = null;

// Start detection
startBtn.addEventListener('click', async function () {
    try {
        stream = await navigator.mediaDevices.getUserMedia({
            video: {
                width: { ideal: 1280 },
                height: { ideal: 720 }
            }
        });

        video.srcObject = stream;
        video.style.display = 'block';
        detectionFrame.style.display = 'none';

        video.onloadedmetadata = () => {
            // Optimize resolution for detection - max 640px width
            const MAX_WIDTH = 640;
            const ratio = video.videoWidth / video.videoHeight;
            canvas.width = Math.min(video.videoWidth, MAX_WIDTH);
            canvas.height = canvas.width / ratio;

            // Start recursive detection loop instead of fixed interval
            detectFrame();

            startBtn.style.display = 'none';
            stopBtn.style.display = 'inline-block';
        };
    } catch (err) {
        alert('Camera access denied or not available: ' + err.message);
    }
});

// Stop detection
stopBtn.addEventListener('click', function () {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
    }

    // Stop recursive loop by setting flag
    isDetecting = false;

    video.style.display = 'none';
    detectionFrame.style.display = 'block';
    detectionFrame.src = '';

    startBtn.style.display = 'inline-block';
    stopBtn.style.display = 'none';

    humanCountEl.textContent = '0';
    animalCountEl.textContent = '0';
    animalsListEl.textContent = 'None';
});

let isDetecting = false;

// Detect frame
async function detectFrame() {
    if (!video.srcObject) return;

    isDetecting = true;

    try {
        // Draw to canvas (resized)
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        const frameData = canvas.toDataURL('image/jpeg', 0.8); // Compress slightly

        const response = await fetch('/detection/api/detect-frame', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ frame: frameData })
        });

        const result = await response.json();

        if (result.success && isDetecting) {
            detectionFrame.src = result.frame;
            detectionFrame.style.display = 'block';
            video.style.display = 'none';

            humanCountEl.textContent = result.human_count;
            animalCountEl.textContent = result.animal_count;

            if (result.detected_animals.length > 0) {
                animalsListEl.textContent = result.detected_animals.join(', ');
            } else {
                animalsListEl.textContent = 'None';
            }

            if (result.has_detection) {
                const detectionSignature = `${result.human_count}-${result.animal_count}`;
                if (lastDetection !== detectionSignature) {
                    lastDetection = detectionSignature;
                    saveDetection(result);
                }
            }
        }
    } catch (err) {
        console.error('Detection error:', err);
    } finally {
        // Continue loop if still detecting
        if (isDetecting) {
            // Adaptive frame rate - wait 500ms before next frame to prevent overload
            setTimeout(detectFrame, 500);
        }
    }
}

// Save detection
async function saveDetection(detectionData) {
    try {
        const response = await fetch('/detection/api/save-detection', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                human_count: detectionData.human_count,
                animal_count: detectionData.animal_count,
                detected_animals: detectionData.detected_animals
            })
        });

        const result = await response.json();

        if (result.success) {
            console.log('Detection saved and notifications sent');
            showNotificationToast(result.notification);
        }
    } catch (err) {
        console.error('Save error:', err);
    }
}

function showNotificationToast(notification) {
    // Simple toast notification
    const toast = document.createElement('div');
    toast.className = 'alert alert-info';
    toast.style.position = 'fixed';
    toast.style.top = '20px';
    toast.style.right = '20px';
    toast.style.zIndex = '10000';
    toast.innerHTML = `<strong>${notification.title}</strong><br>${notification.message}`;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 500);
    }, 5000);
}
       