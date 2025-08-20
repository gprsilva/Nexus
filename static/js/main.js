// Ultra-Modern JavaScript for Nexus
document.addEventListener('DOMContentLoaded', function() {
    
    // Enhanced Navbar Scroll Effect
    const navbar = document.querySelector('.navbar');
    let lastScrollTop = 0;
    
    window.addEventListener('scroll', function() {
        let scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        if (scrollTop > 100) {
            navbar.style.background = 'rgba(255, 255, 255, 0.98)';
            navbar.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.1)';
        } else {
            navbar.style.background = 'rgba(255, 255, 255, 0.95)';
            navbar.style.boxShadow = '0 1px 2px rgba(0, 0, 0, 0.05)';
        }
        
        // Hide/show navbar on scroll
        if (scrollTop > lastScrollTop && scrollTop > 100) {
            navbar.style.transform = 'translateY(-100%)';
        } else {
            navbar.style.transform = 'translateY(0)';
        }
        lastScrollTop = scrollTop;
    });
    
    // Advanced Search Enhancement
    const searchInput = document.querySelector('.search-input');
    if (searchInput) {
        searchInput.addEventListener('focus', function() {
            this.parentElement.style.transform = 'scale(1.02)';
        });
        
        searchInput.addEventListener('blur', function() {
            this.parentElement.style.transform = 'scale(1)';
        });
    }
    
    // Project Card Hover Effects
    const projectCards = document.querySelectorAll('.project-card');
    projectCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.willChange = 'transform';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.willChange = 'auto';
        });
    });
    
    // Enhanced Like Button Functionality
    function setupLikeButtons() {
        const likeButtons = document.querySelectorAll('.like-btn');
        likeButtons.forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                
                const projectId = this.dataset.projectId;
                const heartIcon = this.querySelector('i');
                const countSpan = this.querySelector('.like-count');
                
                // Add loading state
                heartIcon.classList.add('fa-spin');
                
                fetch(`/project/${projectId}/like`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCSRFToken()
                    }
                })
                .then(response => response.json())
                .then(data => {
                    heartIcon.classList.remove('fa-spin');
                    
                    if (data.liked) {
                        heartIcon.classList.remove('far');
                        heartIcon.classList.add('fas');
                        this.classList.add('liked');
                        
                        // Heart animation
                        heartIcon.style.transform = 'scale(1.3)';
                        setTimeout(() => {
                            heartIcon.style.transform = 'scale(1)';
                        }, 200);
                    } else {
                        heartIcon.classList.remove('fas');
                        heartIcon.classList.add('far');
                        this.classList.remove('liked');
                    }
                    
                    countSpan.textContent = data.like_count;
                    
                    // Success animation
                    this.style.transform = 'scale(1.1)';
                    setTimeout(() => {
                        this.style.transform = 'scale(1)';
                    }, 150);
                })
                .catch(error => {
                    heartIcon.classList.remove('fa-spin');
                    console.error('Error:', error);
                    showNotification('Erro ao curtir projeto', 'error');
                });
            });
        });
    }
    
    // Follow Button Enhancement
    function setupFollowButtons() {
        const followButtons = document.querySelectorAll('.follow-btn');
        followButtons.forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                
                const username = this.dataset.username;
                const originalText = this.innerHTML;
                
                // Loading state
                this.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Processando...';
                this.disabled = true;
                
                fetch(`/follow/${username}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCSRFToken()
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.following) {
                        this.innerHTML = '<i class="fas fa-user-minus me-1"></i>Deixar de Seguir';
                        this.classList.remove('btn-primary');
                        this.classList.add('btn-outline-primary');
                    } else {
                        this.innerHTML = '<i class="fas fa-user-plus me-1"></i>Seguir';
                        this.classList.remove('btn-outline-primary');
                        this.classList.add('btn-primary');
                    }
                    this.disabled = false;
                    
                    showNotification(data.message, 'success');
                })
                .catch(error => {
                    this.innerHTML = originalText;
                    this.disabled = false;
                    console.error('Error:', error);
                    showNotification('Erro ao seguir usuário', 'error');
                });
            });
        });
    }
    
    // Enhanced Image Preview
    function setupImagePreviews() {
        const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
        imageInputs.forEach(input => {
            input.addEventListener('change', function(e) {
                const file = e.target.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        let preview = document.getElementById('image-preview');
                        if (!preview) {
                            preview = document.createElement('div');
                            preview.id = 'image-preview';
                            preview.className = 'mt-3';
                            input.parentNode.appendChild(preview);
                        }
                        
                        preview.innerHTML = `
                            <div class="position-relative d-inline-block">
                                <img src="${e.target.result}" 
                                     class="img-thumbnail" 
                                     style="max-width: 200px; max-height: 200px; border-radius: var(--radius-lg);">
                                <button type="button" class="btn btn-sm btn-danger position-absolute top-0 end-0 rounded-circle" 
                                        onclick="removeImagePreview()" style="transform: translate(50%, -50%);">
                                    <i class="fas fa-times"></i>
                                </button>
                            </div>
                        `;
                    };
                    reader.readAsDataURL(file);
                }
            });
        });
    }
    
    // Enhanced Form Validation
    function setupFormValidation() {
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            const inputs = form.querySelectorAll('input, textarea, select');
            
            inputs.forEach(input => {
                input.addEventListener('blur', function() {
                    validateField(this);
                });
                
                input.addEventListener('input', function() {
                    if (this.classList.contains('is-invalid')) {
                        validateField(this);
                    }
                });
            });
            
            form.addEventListener('submit', function(e) {
                let isValid = true;
                inputs.forEach(input => {
                    if (!validateField(input)) {
                        isValid = false;
                    }
                });
                
                if (!isValid) {
                    e.preventDefault();
                    showNotification('Por favor, corrija os erros no formulário', 'error');
                }
            });
        });
    }
    
    // Advanced Notification System
    function showNotification(message, type = 'info', duration = 5000) {
        const container = getNotificationContainer();
        
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show notification-toast`;
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Enhanced styling
        notification.style.cssText = `
            position: fixed;
            top: 100px;
            right: 20px;
            z-index: 1060;
            min-width: 300px;
            box-shadow: var(--shadow-xl);
            border-radius: var(--radius-lg);
            border: none;
            backdrop-filter: blur(20px);
        `;
        
        container.appendChild(notification);
        
        // Auto remove
        setTimeout(() => {
            if (notification.parentNode) {
                notification.classList.remove('show');
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.remove();
                    }
                }, 150);
            }
        }, duration);
    }
    
    // Utility Functions
    function getCSRFToken() {
        const token = document.querySelector('meta[name="csrf-token"]');
        return token ? token.getAttribute('content') : '';
    }
    
    function getNotificationContainer() {
        let container = document.getElementById('notification-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'notification-container';
            document.body.appendChild(container);
        }
        return container;
    }
    
    function validateField(field) {
        const value = field.value.trim();
        let isValid = true;
        
        // Remove existing feedback
        const existingFeedback = field.parentNode.querySelector('.invalid-feedback');
        if (existingFeedback) {
            existingFeedback.remove();
        }
        field.classList.remove('is-invalid', 'is-valid');
        
        // Required field validation
        if (field.hasAttribute('required') && !value) {
            showFieldError(field, 'Este campo é obrigatório');
            isValid = false;
        }
        
        // Email validation
        if (field.type === 'email' && value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                showFieldError(field, 'Email inválido');
                isValid = false;
            }
        }
        
        // Password validation
        if (field.type === 'password' && value && value.length < 6) {
            showFieldError(field, 'A senha deve ter pelo menos 6 caracteres');
            isValid = false;
        }
        
        // Show success state
        if (isValid && value) {
            field.classList.add('is-valid');
        }
        
        return isValid;
    }
    
    function showFieldError(field, message) {
        field.classList.add('is-invalid');
        const feedback = document.createElement('div');
        feedback.className = 'invalid-feedback';
        feedback.textContent = message;
        field.parentNode.appendChild(feedback);
    }
    
    // Global Functions (for onclick handlers)
    window.removeImagePreview = function() {
        const preview = document.getElementById('image-preview');
        if (preview) {
            preview.remove();
        }
        const input = document.querySelector('input[type="file"][accept*="image"]');
        if (input) {
            input.value = '';
        }
    };
    
    window.showNotification = showNotification;
    
    // Initialize all features
    setupLikeButtons();
    setupFollowButtons();
    setupImagePreviews();
    setupFormValidation();
    
    // Progressive Enhancement for dynamic content
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes.length) {
                setupLikeButtons();
                setupFollowButtons();
            }
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
    
    console.log('🚀 Nexus enhanced UI loaded successfully!');
});

// Advanced Loading States
function showLoading(element, text = 'Carregando...') {
    const originalContent = element.innerHTML;
    element.dataset.originalContent = originalContent;
    element.innerHTML = `<i class="fas fa-spinner fa-spin me-1"></i>${text}`;
    element.disabled = true;
}

function hideLoading(element) {
    if (element.dataset.originalContent) {
        element.innerHTML = element.dataset.originalContent;
        delete element.dataset.originalContent;
    }
    element.disabled = false;
}