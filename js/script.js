document.addEventListener('DOMContentLoaded', function() {
    // Upload form handling
    const uploadForm = document.getElementById('uploadForm');
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const fileInput = document.getElementById('fileInput');
            if (!fileInput.files || fileInput.files.length === 0) {
                showError('Please select a file first');
                return;
            }
            
            const file = fileInput.files[0];
            const fileSizeMB = file.size / (1024 * 1024);
            const maxSizeMB = 16;
            
            if (fileSizeMB > maxSizeMB) {
                showError(`File size exceeds ${maxSizeMB}MB limit`);
                return;
            }
            
            const formData = new FormData();
            formData.append('file', file);
            
            // Show loading state
            const submitBtn = uploadForm.querySelector('button[type="submit"]');
            const originalBtnText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
            
            // Clear previous results and errors
            document.getElementById('results').style.display = 'none';
            const errorAlert = document.getElementById('errorAlert');
            if (errorAlert) errorAlert.style.display = 'none';
            
            fetch('/detect_objects', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => Promise.reject(err));
                }
                return response.json();
            })
            .then(data => {
                if (data.error) {
                    throw new Error(data.error);
                }
                
                // Display results
                const resultsDiv = document.getElementById('results');
                resultsDiv.style.display = 'block';
                
                document.getElementById('processingTime').textContent = data.processing_time;
                document.getElementById('objectCount').textContent = data.object_count;
                
                // Display preview
                const originalPreview = document.getElementById('originalPreview');
                const resultPreview = document.getElementById('resultPreview');
                
                if (data.is_video) {
                    originalPreview.src = '';
                    resultPreview.src = '';
                    
                    const originalVideo = document.createElement('video');
                    originalVideo.src = `/results/${data.original}`;
                    originalVideo.controls = true;
                    originalVideo.className = 'img-fluid rounded';
                    originalVideo.style.maxHeight = '300px';
                    
                    const resultVideo = document.createElement('video');
                    resultVideo.src = `/results/${data.result}`;
                    resultVideo.controls = true;
                    resultVideo.className = 'img-fluid rounded';
                    resultVideo.style.maxHeight = '300px';
                    
                    originalPreview.parentNode.replaceChild(originalVideo, originalPreview);
                    resultPreview.parentNode.replaceChild(resultVideo, resultPreview);
                } else {
                    originalPreview.src = `/results/${data.original}`;
                    resultPreview.src = `/results/${data.result}`;
                }
                
                // List detected objects
                const detectedObjectsList = document.getElementById('detectedObjects');
                detectedObjectsList.innerHTML = '';
                
                const objectCounts = {};
                data.detected_objects.forEach(obj => {
                    objectCounts[obj] = (objectCounts[obj] || 0) + 1;
                });
                
                for (const [obj, count] of Object.entries(objectCounts)) {
                    const li = document.createElement('li');
                    li.className = 'list-group-item d-flex justify-content-between align-items-center';
                    li.textContent = obj;
                    
                    const span = document.createElement('span');
                    span.className = 'badge bg-primary rounded-pill';
                    span.textContent = count;
                    
                    li.appendChild(span);
                    detectedObjectsList.appendChild(li);
                }
            })
            .catch(error => {
                showError(error.message || 'An error occurred during processing');
            })
            .finally(() => {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalBtnText;
            });
        });
    }
    
    // Real-time detection handling
    const startWebcamBtn = document.getElementById('startWebcam');
    const stopWebcamBtn = document.getElementById('stopWebcam');
    const webcamContainer = document.getElementById('webcamContainer');
    const webcamFeed = document.getElementById('webcamFeed');
    const webcamAlert = document.getElementById('webcamAlert');
    const errorAlert = document.getElementById('errorAlert');
    
    if (startWebcamBtn) {
        let isStreaming = false;
        
        function showError(message) {
            if (errorAlert) {
                errorAlert.textContent = message;
                errorAlert.style.display = 'block';
            } else {
                alert(message);
            }
        }
        
        startWebcamBtn.addEventListener('click', async function() {
            try {
                // Check if browser supports mediaDevices
                if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                    throw new Error('Browser does not support camera access');
                }
                
                // Request camera access to ensure permissions are granted
                const stream = await navigator.mediaDevices.getUserMedia({ video: true });
                stream.getTracks().forEach(track => track.stop());
                
                // Start the detection feed
                webcamFeed.src = '/video_feed';
                
                // Update UI
                startWebcamBtn.disabled = true;
                stopWebcamBtn.disabled = false;
                webcamContainer.style.display = 'block';
                webcamAlert.style.display = 'none';
                if (errorAlert) errorAlert.style.display = 'none';
                
                isStreaming = true;
                
                // Check if feed is working
                webcamFeed.onerror = () => {
                    showError('Failed to start video feed. Please try again.');
                    stopWebcam();
                };
                
                webcamFeed.onload = () => {
                    // Feed is working
                };
                
            } catch (err) {
                showError(err.message);
            }
        });
        
        stopWebcamBtn.addEventListener('click', stopWebcam);
        
        function stopWebcam() {
            fetch('/stop_camera')
                .then(response => response.json())
                .then(data => {
                    webcamFeed.src = '';
                    startWebcamBtn.disabled = false;
                    stopWebcamBtn.disabled = true;
                    webcamContainer.style.display = 'none';
                    webcamAlert.style.display = 'block';
                    isStreaming = false;
                })
                .catch(err => {
                    showError('Error stopping camera: ' + err.message);
                });
        }
        
        // Clean up on page leave
        window.addEventListener('beforeunload', function() {
            if (isStreaming) {
                fetch('/stop_camera').catch(() => {});
            }
        });
    }
});