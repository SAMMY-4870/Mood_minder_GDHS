// Login page JavaScript
document.addEventListener('DOMContentLoaded', function() {
    const passwordInput = document.getElementById('password');
    const toggleButton = document.getElementById('togglePassword');
    const toggleIcon = document.getElementById('toggleIcon');
    const loginForm = document.getElementById('loginForm');
    
    // Password toggle functionality
    if (toggleButton && passwordInput) {
        toggleButton.addEventListener('click', function() {
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                toggleIcon.textContent = '🙈';
            } else {
                passwordInput.type = 'password';
                toggleIcon.textContent = '👁️';
            }
        });
    }
    
    // Form validation and submission
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            const email = document.getElementById('email').value.trim();
            const password = passwordInput.value;
            
            // Basic validation
            if (!email || !password) {
                e.preventDefault();
                showAlert('Please fill in all fields.', 'warning');
                return;
            }
            
            if (!isValidEmail(email)) {
                e.preventDefault();
                showAlert('Please enter a valid email address.', 'warning');
                return;
            }
            
            // Show loading state
            const submitBtn = loginForm.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.classList.add('loading');
                submitBtn.innerHTML = '<span class="me-2">⏳</span>Signing In...';
            }
        });
    }
    
    // Auto-fill test credentials
    const testCredentialsBtn = document.createElement('button');
    testCredentialsBtn.type = 'button';
    testCredentialsBtn.className = 'btn btn-sm btn-outline-secondary mt-2';
    testCredentialsBtn.innerHTML = '🔧 Fill Test Credentials';
    testCredentialsBtn.addEventListener('click', function() {
        document.getElementById('email').value = 'test@example.com';
        passwordInput.value = 'password123';
        showAlert('Test credentials filled!', 'info');
    });
    
    const debugSection = document.querySelector('.border-top');
    if (debugSection) {
        debugSection.appendChild(testCredentialsBtn);
    }
    
    // Email validation function
    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
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
        
        // Insert after the test credentials alert
        const testAlert = document.querySelector('.alert-info');
        if (testAlert) {
            testAlert.parentNode.insertBefore(alertDiv, testAlert.nextSibling);
        } else {
            loginForm.insertBefore(alertDiv, loginForm.firstChild);
        }
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
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
});