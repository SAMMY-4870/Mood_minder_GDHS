// Upload page JavaScript
document.addEventListener('DOMContentLoaded', function() {
    const imageForm = document.getElementById('imageForm');
    const imageFileInput = imageForm ? imageForm.querySelector('input[type="file"]') : null;
    const imagePreview = document.getElementById('imagePreview');
    const previewImg = document.getElementById('previewImg');
    
    // Image preview functionality
    if (imageFileInput && imagePreview && previewImg) {
        imageFileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                // Validate file type
                const validTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp'];
                if (!validTypes.includes(file.type)) {
                    showAlert('Please select a valid image file (PNG, JPG, JPEG, GIF, WebP).', 'warning');
                    this.value = '';
                    imagePreview.style.display = 'none';
                    return;
                }
                
                // Validate file size (max 10MB)
                if (file.size > 10 * 1024 * 1024) {
                    showAlert('Image file is too large. Please select a file smaller than 10MB.', 'warning');
                    this.value = '';
                    imagePreview.style.display = 'none';
                    return;
                }
                
                // Show preview
                const reader = new FileReader();
                reader.onload = function(e) {
                    previewImg.src = e.target.result;
                    imagePreview.style.display = 'block';
                };
                reader.readAsDataURL(file);
            } else {
                imagePreview.style.display = 'none';
            }
        });
    }
    
    // Form submission handling
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            const formName = this.querySelector('input[name="form_name"]').value;
            
            // Show loading state
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.classList.add('loading');
                
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<span class="me-2">⏳</span>Uploading...';
                
                // Reset button after 10 seconds (fallback)
                setTimeout(() => {
                    submitBtn.disabled = false;
                    submitBtn.classList.remove('loading');
                    submitBtn.innerHTML = originalText;
                }, 10000);
            }
            
            // Validate form based on type
            if (formName === 'quote') {
                const quote = this.querySelector('textarea[name="quote"]').value.trim();
                if (!quote) {
                    e.preventDefault();
                    showAlert('Please enter a quote.', 'warning');
                    resetButton(submitBtn);
                    return;
                }
            } else if (formName === 'image') {
                const fileInput = this.querySelector('input[type="file"]');
                if (!fileInput.files[0]) {
                    e.preventDefault();
                    showAlert('Please select an image file.', 'warning');
                    resetButton(submitBtn);
                    return;
                }
            } else if (formName === 'song') {
                const title = this.querySelector('input[name="title"]').value.trim();
                const artist = this.querySelector('input[name="artist"]').value.trim();
                const fileInput = this.querySelector('input[type="file"]');
                
                if (!title || !artist || !fileInput.files[0]) {
                    e.preventDefault();
                    showAlert('Please fill in all song details and select a file.', 'warning');
                    resetButton(submitBtn);
                    return;
                }
                
                // Validate audio file type
                const validTypes = ['audio/mpeg', 'audio/wav', 'audio/ogg', 'audio/mp4'];
                if (!validTypes.includes(fileInput.files[0].type)) {
                    e.preventDefault();
                    showAlert('Please select a valid audio file (MP3, WAV, OGG, M4A).', 'warning');
                    resetButton(submitBtn);
                    return;
                }
            }
        });
    });
    
    // Drag and drop functionality for file inputs
    document.querySelectorAll('input[type="file"]').forEach(input => {
        const card = input.closest('.card');
        
        if (card) {
            card.addEventListener('dragover', function(e) {
                e.preventDefault();
                this.classList.add('drag-over');
            });
            
            card.addEventListener('dragleave', function(e) {
                e.preventDefault();
                this.classList.remove('drag-over');
            });
            
            card.addEventListener('drop', function(e) {
                e.preventDefault();
                this.classList.remove('drag-over');
                
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    input.files = files;
                    input.dispatchEvent(new Event('change'));
                }
            });
        }
    });
    
    // Auto-resize textarea
    const textarea = document.querySelector('textarea[name="quote"]');
    if (textarea) {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
    }
    
    // Show alert function
    function showAlert(message, type) {
        // Remove existing alerts
        const existingAlerts = document.querySelectorAll('.alert');
        existingAlerts.forEach(alert => alert.remove());
        
        // Create new alert
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Insert at the top of the page
        const pageTitle = document.querySelector('.upload-page h2');
        if (pageTitle) {
            pageTitle.parentNode.insertBefore(alertDiv, pageTitle.nextSibling);
        }
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
    
    // Reset button function
    function resetButton(button) {
        if (button) {
            button.disabled = false;
            button.classList.remove('loading');
            // Restore original text based on button type
            const formName = button.closest('form').querySelector('input[name="form_name"]').value;
            if (formName === 'quote') {
                button.innerHTML = '<span class="me-2">💾</span>Save Quote';
            } else if (formName === 'image') {
                button.innerHTML = '<span class="me-2">📤</span>Upload Image';
            } else if (formName === 'song') {
                button.innerHTML = '<span class="me-2">🎵</span>Upload Song';
            }
        }
    }
    
    // Add ripple effect to buttons
    document.querySelectorAll('.btn').forEach(button => {
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.classList.add('ripple');
            
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
    
    // Form field animations
    document.querySelectorAll('.form-control').forEach(input => {
        input.addEventListener('focus', function() {
            this.parentNode.classList.add('focused');
        });
        
        input.addEventListener('blur', function() {
            if (!this.value) {
                this.parentNode.classList.remove('focused');
            }
        });
    });
});