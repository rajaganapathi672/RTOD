/**
 * Upload Detection JavaScript
 */

const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const filePreview = document.getElementById('filePreview');
const previewContent = document.getElementById('previewContent');
const fileName = document.getElementById('fileName');

if (uploadArea && fileInput) {
    uploadArea.addEventListener('click', function() {
        fileInput.click();
    });

    uploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        uploadArea.style.borderColor = '#667eea';
        uploadArea.style.background = 'rgba(102, 126, 234, 0.1)';
    });

    uploadArea.addEventListener('dragleave', function(e) {
        e.preventDefault();
        uploadArea.style.borderColor = 'var(--border-color)';
        uploadArea.style.background = 'var(--bg-secondary)';
    });

    uploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        uploadArea.style.borderColor = 'var(--border-color)';
        uploadArea.style.background = 'var(--bg-secondary)';
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            fileInput.files = files;
            handleFileSelect();
        }
    });

    fileInput.addEventListener('change', handleFileSelect);
}

function handleFileSelect() {
    const file = fileInput.files[0];
    if (!file) return;
    
    fileName.textContent = `Selected: ${file.name}`;
    
    const fileType = file.type;
    const reader = new FileReader();
    
    reader.onload = function(e) {
        previewContent.innerHTML = '';
        
        if (fileType.startsWith('image/')) {
            const img = document.createElement('img');
            img.src = e.target.result;
            previewContent.appendChild(img);
        } else if (fileType.startsWith('video/')) {
            const video = document.createElement('video');
            video.src = e.target.result;
            video.controls = true;
            previewContent.appendChild(video);
        }
        
        filePreview.style.display = 'block';
    };
    
    reader.readAsDataURL(file);
}
            