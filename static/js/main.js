// Nexus - Professional Developer Network JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all interactive features
    initializeLikeButtons();
    initializeImagePreview();
    initializeFormValidation();
    initializeTooltips();
    initializeScrollAnimations();
    initializeSearchEnhancements();
    initializeLoadingStates();
});

// Like Button Functionality
function initializeLikeButtons() {
    const likeButtons = document.querySelectorAll('.like-btn');
    
    likeButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const projectId = this.dataset.projectId;
            const isLiked = this.dataset.liked === 'true';
            
            // Add loading state
            const originalContent = this.innerHTML;
            this.innerHTML = '<span class="loading"></span> Loading...';
            this.disabled = true;
            
            // Send AJAX request
            fetch(`/like_project/${projectId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                }
            })
            .then(response => response.json())
            .then(data => {
                // Update button state
                const heartIcon = this.querySelector('.fas.fa-heart');
                const likeCount = this.querySelector('.like-count');
                const likeText = this.querySelector('.like-text');
                
                if (data.liked) {
                    heartIcon.classList.add('text-danger');
                    this.classList.add('liked');
                    if (likeText) likeText.textContent = 'Liked';
                    
                    // Trigger heart beat animation
                    this.style.animation = 'none';
                    setTimeout(() => {
                        this.style.animation = 'heartBeat 0.5s ease-in-out';
                    }, 10);
                } else {
                    heartIcon.classList.remove('text-danger');
                    this.classList.remove('liked');
                    if (likeText) likeText.textContent = 'Like';
                }
                
                // Update like count
                if (likeCount) {
                    likeCount.textContent = data.like_count;
                }
                
                // Update dataset
                this.dataset.liked = data.liked.toString();
                
                // Show success feedback
                showToast(data.liked ? 'Project liked!' : 'Like removed', 'success');
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('Error updating like. Please try again.', 'error');
            })
            .finally(() => {
                // Restore button state
                this.innerHTML = originalContent;
                this.disabled = false;
            });
        });
    });
}

// Image Preview for File Uploads
function initializeImagePreview() {
    const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
    
    imageInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    // Find or create preview element
                    let preview = input.parentNode.querySelector('.image-preview');
                    if (!preview) {
                        preview = document.createElement('img');
                        preview.className = 'image-preview img-thumbnail mt-2';
                        preview.style.maxWidth = '200px';
                        preview.style.maxHeight = '200px';
                        input.parentNode.appendChild(preview);
                    }
                    preview.src = e.target.result;
                };
                reader.readAsDataURL(file);
            }
        });
    });
}

// Enhanced Form Validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        // Real-time validation
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(this);
            });
            
            input.addEventListener('input', function() {
                clearFieldError(this);
            });
        });
        
        // Form submission validation
        form.addEventListener('submit', function(e) {
            let isValid = true;
            
            inputs.forEach(input => {
                if (!validateField(input)) {
                    isValid = false;
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                showToast('Please fix the form errors before submitting.', 'error');
            } else {
                // Show loading state
                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn) {
                    const originalText = submitBtn.innerHTML;
                    submitBtn.innerHTML = '<span class="loading"></span> Submitting...';
                    submitBtn.disabled = true;
                    
                    // Re-enable after timeout (in case of errors)
                    setTimeout(() => {
                        submitBtn.innerHTML = originalText;
                        submitBtn.disabled = false;
                    }, 10000);
                }
            }
        });
    });
}

// Field Validation
function validateField(field) {
    const value = field.value.trim();
    let isValid = true;
    let message = '';
    
    // Check required fields
    if (field.hasAttribute('required') && !value) {
        isValid = false;
        message = 'This field is required.';
    }
    
    // Email validation
    else if (field.type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            isValid = false;
            message = 'Please enter a valid email address.';
        }
    }
    
    // URL validation
    else if (field.type === 'url' && value) {
        try {
            new URL(value);
        } catch {
            isValid = false;
            message = 'Please enter a valid URL.';
        }
    }
    
    // Password validation
    else if (field.type === 'password' && value) {
        if (value.length < 6) {
            isValid = false;
            message = 'Password must be at least 6 characters long.';
        }
    }
    
    // Username validation
    else if (field.name === 'username' && value) {
        if (value.length < 3) {
            isValid = false;
            message = 'Username must be at least 3 characters long.';
        } else if (!/^[a-zA-Z0-9_]+$/.test(value)) {
            isValid = false;
            message = 'Username can only contain letters, numbers, and underscores.';
        }
    }
    
    // Show/hide validation feedback
    if (!isValid) {
        showFieldError(field, message);
    } else {
        clearFieldError(field);
    }
    
    return isValid;
}

function showFieldError(field, message) {
    field.classList.add('is-invalid');
    
    let feedback = field.parentNode.querySelector('.invalid-feedback');
    if (!feedback) {
        feedback = document.createElement('div');
        feedback.className = 'invalid-feedback';
        field.parentNode.appendChild(feedback);
    }
    feedback.textContent = message;
}

function clearFieldError(field) {
    field.classList.remove('is-invalid');
    const feedback = field.parentNode.querySelector('.invalid-feedback');
    if (feedback) {
        feedback.remove();
    }
}

// Initialize Bootstrap Tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Scroll Animations
function initializeScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'fadeInUp 0.6s ease-out forwards';
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observe cards and project elements
    const elements = document.querySelectorAll('.card, .project-card, .user-card, .feed-card');
    elements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        observer.observe(el);
    });
}

// Search Enhancements
function initializeSearchEnhancements() {
    const searchInput = document.querySelector('input[name="q"]');
    if (searchInput) {
        let searchTimeout;
        
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();
            
            if (query.length >= 2) {
                searchTimeout = setTimeout(() => {
                    // You could implement live search suggestions here
                    console.log('Searching for:', query);
                }, 300);
            }
        });
        
        // Add search suggestions (placeholder)
        searchInput.addEventListener('focus', function() {
            // Show recent searches or popular tags
            console.log('Search input focused');
        });
    }
}

// Loading States
function initializeLoadingStates() {
    // Add loading states to navigation links
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            if (this.href && !this.href.includes('#')) {
                this.style.opacity = '0.7';
                this.style.pointerEvents = 'none';
            }
        });
    });
}

// Utility Functions
function getCSRFToken() {
    // Try to get CSRF token from meta tag
    const metaToken = document.querySelector('meta[name="csrf-token"]');
    if (metaToken) {
        return metaToken.getAttribute('content');
    }
    
    // Try to get from form
    const csrfInput = document.querySelector('input[name="csrf_token"]');
    if (csrfInput) {
        return csrfInput.value;
    }
    
    return '';
}

function showToast(message, type = 'info') {
    // Create toast container if it doesn't exist
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = '9999';
        document.body.appendChild(toastContainer);
    }
    
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type === 'success' ? 'success' : 'primary'} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Initialize and show toast
    const bsToast = new bootstrap.Toast(toast, {
        autohide: true,
        delay: 5000
    });
    bsToast.show();
    
    // Remove toast element after it's hidden
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

// Smooth scrolling for anchor links
document.addEventListener('click', function(e) {
    if (e.target.matches('a[href^="#"]')) {
        e.preventDefault();
        const target = document.querySelector(e.target.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    }
});

// Add fade-in animation keyframes
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
`;
document.head.appendChild(style);

// Auto-resize textareas
document.addEventListener('input', function(e) {
    if (e.target.tagName.toLowerCase() === 'textarea') {
        e.target.style.height = 'auto';
        e.target.style.height = e.target.scrollHeight + 'px';
    }
});

// Character count for textareas with maxlength
document.querySelectorAll('textarea[maxlength]').forEach(textarea => {
    const maxLength = textarea.getAttribute('maxlength');
    const counter = document.createElement('small');
    counter.className = 'form-text text-muted char-counter';
    counter.style.float = 'right';
    textarea.parentNode.appendChild(counter);
    
    function updateCounter() {
        const remaining = maxLength - textarea.value.length;
        counter.textContent = `${remaining} characters remaining`;
        counter.style.color = remaining < 50 ? 'var(--warning-color)' : 'var(--muted-text)';
    }
    
    textarea.addEventListener('input', updateCounter);
    updateCounter();
});

// Handle file size validation
document.querySelectorAll('input[type="file"]').forEach(input => {
    input.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            const maxSize = 16 * 1024 * 1024; // 16MB
            if (file.size > maxSize) {
                showToast('File size must be less than 16MB', 'error');
                this.value = '';
                return;
            }
            
            // Show file name
            const fileName = document.createElement('small');
            fileName.className = 'form-text text-muted';
            fileName.textContent = `Selected: ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`;
            
            // Remove existing file name display
            const existing = this.parentNode.querySelector('.file-name');
            if (existing) existing.remove();
            
            fileName.classList.add('file-name');
            this.parentNode.appendChild(fileName);
        }
    });
});

console.log('Nexus JavaScript initialized successfully');
