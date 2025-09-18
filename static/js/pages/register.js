// Register page JavaScript
document.addEventListener('DOMContentLoaded', function() {
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirm_password');
    const toggleButton1 = document.getElementById('togglePassword1');
    const toggleButton2 = document.getElementById('togglePassword2');
    const toggleIcon1 = document.getElementById('toggleIcon1');
    const toggleIcon2 = document.getElementById('toggleIcon2');
    const registerForm = document.getElementById('registerForm');
    const passwordMatchDiv = document.getElementById('passwordMatch');
    const submitBtn = document.getElementById('submitBtn');
    
    // Password toggle functionality
    if (toggleButton1 && passwordInput) {
        toggleButton1.addEventListener('click', function() {
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                toggleIcon1.textContent = '🙈';
            } else {
                passwordInput.type = 'password';
                toggleIcon1.textContent = '👁️';
            }
        });
    }
    
    if (toggleButton2 && confirmPasswordInput) {
        toggleButton2.addEventListener('click', function() {
            if (confirmPasswordInput.type === 'password') {
                confirmPasswordInput.type = 'text';
                toggleIcon2.textContent = '🙈';
            } else {
                confirmPasswordInput.type = 'password';
                toggleIcon2.textContent = '👁️';
            }
        });
    }
    
    // Password matching validation
    function checkPasswordMatch() {
        if (confirmPasswordInput.value && passwordInput.value) {
            if (confirmPasswordInput.value === passwordInput.value) {
                passwordMatchDiv.textContent = '✅ Passwords match';
                passwordMatchDiv.className = 'form-text match';
                return true;
            } else {
                passwordMatchDiv.textContent = '❌ Passwords do not match';
                passwordMatchDiv.className = 'form-text no-match';
                return false;
            }
        } else {
            passwordMatchDiv.textContent = '';
            passwordMatchDiv.className = 'form-text';
            return false;
        }
    }
    
    // Real-time password matching
    if (confirmPasswordInput && passwordInput) {
        confirmPasswordInput.addEventListener('input', checkPasswordMatch);
        passwordInput.addEventListener('input', checkPasswordMatch);
    }
    
    // Form validation and submission
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            const firstName = document.getElementById('first_name').value.trim();
            const lastName = document.getElementById('last_name').value.trim();
            const email = document.getElementById('email').value.trim();
            const password = passwordInput.value;
            const confirmPassword = confirmPasswordInput.value;
            
            // Basic validation
            if (!firstName || !lastName || !email || !password || !confirmPassword) {
                e.preventDefault();
                showAlert('Please fill in all fields.', 'warning');
                return;
            }
            
            if (!isValidEmail(email)) {
                e.preventDefault();
                showAlert('Please enter a valid email address.', 'warning');
                return;
            }
            
            if (password.length < 6) {
                e.preventDefault();
                showAlert('Password must be at least 6 characters long.', 'warning');
                return;
            }
            
            if (!checkPasswordMatch()) {
                e.preventDefault();
                showAlert('Passwords do not match.', 'warning');
                return;
            }
            
            // Show loading state
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.classList.add('loading');
                submitBtn.innerHTML = '<span class="me-2">⏳</span>Creating Account...';
            }
        });
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
        
        // Insert at the top of the form
        registerForm.insertBefore(alertDiv, registerForm.firstChild);
        
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