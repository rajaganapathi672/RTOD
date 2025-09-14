/**
 * Wildlife Detection System - Enhanced Main JavaScript
 * Includes theme toggle, notifications, and utility functions
 */

// Theme Toggle Functionality
document.addEventListener('DOMContentLoaded', function() {
    const html = document.documentElement;
    const themeToggle = document.getElementById('themeToggle');
    
    // Load saved theme
    const savedTheme = localStorage.getItem('theme') || 'light';
    html.setAttribute('data-theme', savedTheme);
    
    // Theme toggle event
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const currentTheme = html.getAttribute('data-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            
            // Update UI
            html.setAttribute('data-theme', newTheme);
            
            // Save to localStorage
            localStorage.setItem('theme', newTheme);
            
            // Save to backend
            fetch('/auth/api/toggle-theme', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({theme: newTheme})
            }).catch(err => console.error('Theme save error:', err));
        });
    }
    
    // Flash message auto-dismiss
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s ease';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });
    
    // Notification bell toggle
    const notificationBell = document.getElementById('notificationBell');
    const notificationDropdown = document.getElementById('notificationDropdown');
    
    if (notificationBell && notificationDropdown) {
        notificationBell.addEventListener('click', function(e) {
            e.stopPropagation();
            notificationDropdown.classList.toggle('show');
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', function() {
            notificationDropdown.classList.remove('show');
        });
    }
    
    // Load notifications
    loadNotifications();
});

// Load user notifications
function loadNotifications() {
    fetch('/detection/api/notifications?limit=5')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.notifications.length > 0) {
                updateNotificationBadge(data.count);
            }
        })
        .catch(err => console.error('Load notifications error:', err));
}

// Update notification badge
function updateNotificationBadge(count) {
    const badge = document.querySelector('.notification-bell .badge');
    if (badge && count > 0) {
        badge.textContent = count;
        badge.style.display = 'block';
    }
}

// View Detection Modal
function viewDetection(detectionId) {
    fetch(`/detection/api/view/${detectionId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showDetectionModal(data.detection);
            }
        })
        .catch(err => console.error('View detection error:', err));
}

function showDetectionModal(detection) {
    const modal = document.getElementById('detectionModal');
    if (!modal) return;
    
    // Set modal content
    document.getElementById('modalTimestamp').textContent = detection.timestamp;
    document.getElementById('modalType').textContent = detection.detection_type;
    document.getElementById('modalHumans').textContent = detection.human_count;
    document.getElementById('modalAnimals').textContent = detection.animal_count;
    document.getElementById('modalSpecies').textContent = detection.detected_animals || 'None';
    
    // Load media
    const modalMedia = document.getElementById('modalMedia');
    if (detection.processed_url) {
        if (detection.file_type === 'image') {
            modalMedia.innerHTML = `<img src="${detection.processed_url}" alt="Detection Result">`;
        } else if (detection.file_type === 'video') {
            modalMedia.innerHTML = `<video controls src="${detection.processed_url}"></video>`;
        }
    } else {
        modalMedia.innerHTML = '<p>No processed media available</p>';
    }
    
    // Show modal
    modal.style.display = 'block';
}

function closeModal() {
    const modal = document.getElementById('detectionModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('detectionModal');
    if (event.target == modal) {
        modal.style.display = 'none';
    }
}

// Form validation helper
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Show loading spinner
function showLoading(button) {
    button.disabled = true;
    button.innerHTML = '<span class="spin">⏳</span> Processing...';
}

// Hide loading spinner
function hideLoading(button, text) {
    button.disabled = false;
    button.innerHTML = text;
}
        