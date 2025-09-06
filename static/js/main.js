/* ========================================
   RENTZ - MAIN JAVASCRIPT FILE
   Modern Interactive Features & Animations
   ======================================== */

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

/* ========================================
   INITIALIZATION
   ======================================== */
function initializeApp() {
    initNavigation();
    initAnimations();
    initFormEnhancements();
    initNotifications();
    initUtilities();
    
    console.log('🏠 Rentz App Initialized Successfully!');
}

/* ========================================
   NAVIGATION FUNCTIONALITY
   ======================================== */
function initNavigation() {
    const navToggle = document.getElementById('navToggle');
    const navMenu = document.getElementById('navMenu');
    
    // Mobile menu toggle
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
            
            // Animate hamburger icon
            const icon = this.querySelector('i');
            if (navMenu.classList.contains('active')) {
                icon.classList.remove('fa-bars');
                icon.classList.add('fa-times');
            } else {
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
            }
        });
    }
    
    // Close mobile menu when clicking outside
    document.addEventListener('click', function(e) {
        if (!navToggle?.contains(e.target) && !navMenu?.contains(e.target)) {
            navMenu?.classList.remove('active');
            const icon = navToggle?.querySelector('i');
            if (icon) {
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
            }
        }
    });
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Active navigation highlighting
    highlightActiveNavigation();
}

function highlightActiveNavigation() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href && (currentPath === href || (href !== '/' && currentPath.includes(href)))) {
            link.classList.add('active');
        }
    });
}

/* ========================================
   ANIMATIONS & VISUAL EFFECTS
   ======================================== */
function initAnimations() {
    // Scroll-triggered animations
    initScrollAnimations();
    
    // Glassmorphism hover effects
    initGlassEffects();
    
    // Loading animations
    initLoadingAnimations();
    
    // Particle background (for auth pages)
    initParticleBackground();
}

function initScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
                
                // Staggered animation for grid items
                if (entry.target.classList.contains('products-grid') || 
                    entry.target.classList.contains('categories-grid')) {
                    const items = entry.target.children;
                    Array.from(items).forEach((item, index) => {
                        setTimeout(() => {
                            item.style.opacity = '1';
                            item.style.transform = 'translateY(0)';
                        }, index * 100);
                    });
                }
            }
        });
    }, observerOptions);
    
    // Observe elements for animation
    document.querySelectorAll('.animate-on-scroll, section, .product-card, .category-card, .stat-card').forEach(el => {
        observer.observe(el);
    });
}

function initGlassEffects() {
    // Enhanced hover effects for glass cards
    document.querySelectorAll('.glass-card, .product-card, .category-card').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px) scale(1.02)';
            this.style.boxShadow = '0 20px 40px rgba(0, 0, 0, 0.15)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
            this.style.boxShadow = '';
        });
    });
    
    // Button hover effects
    document.querySelectorAll('.btn').forEach(btn => {
        btn.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
            this.style.boxShadow = '0 8px 15px rgba(0, 0, 0, 0.2)';
        });
        
        btn.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '';
        });
    });
}

function initLoadingAnimations() {
    // Page load animation
    const body = document.body;
    body.style.opacity = '0';
    
    window.addEventListener('load', function() {
        setTimeout(() => {
            body.style.transition = 'opacity 0.5s ease';
            body.style.opacity = '1';
        }, 100);
    });
    
    // Loading spinner for AJAX requests
    window.showLoading = function(element) {
        const spinner = document.createElement('div');
        spinner.className = 'loading-spinner';
        spinner.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        element.appendChild(spinner);
    };
    
    window.hideLoading = function(element) {
        const spinner = element.querySelector('.loading-spinner');
        if (spinner) {
            spinner.remove();
        }
    };
}

function initParticleBackground() {
    const authBackground = document.querySelector('.auth-background');
    if (!authBackground) return;
    
    // Create floating shapes
    const shapes = authBackground.querySelector('.floating-shapes');
    if (shapes) {
        // Animate existing shapes
        const shapeElements = shapes.querySelectorAll('.shape');
        shapeElements.forEach((shape, index) => {
            // Random animation delays and durations
            const delay = Math.random() * 2;
            const duration = 10 + Math.random() * 10;
            
            shape.style.animationDelay = `${delay}s`;
            shape.style.animationDuration = `${duration}s`;
        });
    }
}

/* ========================================
   FORM ENHANCEMENTS
   ======================================== */
function initFormEnhancements() {
    // Enhanced form validation
    initFormValidation();
    
    // Input field animations
    initInputAnimations();
    
    // File upload enhancements
    initFileUpload();
    
    // Auto-save functionality
    initAutoSave();
}

function initFormValidation() {
    document.querySelectorAll('form').forEach(form => {
        const inputs = form.querySelectorAll('input, textarea, select');
        
        inputs.forEach(input => {
            // Real-time validation
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
                showNotification('Please fix the errors in the form', 'error');
            }
        });
    });
}

function validateField(field) {
    const value = field.value.trim();
    const fieldName = field.name || field.id;
    let isValid = true;
    let errorMessage = '';
    
    // Required field validation
    if (field.hasAttribute('required') && !value) {
        errorMessage = `${fieldName.replace('_', ' ')} is required`;
        isValid = false;
    }
    
    // Email validation
    if (field.type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            errorMessage = 'Please enter a valid email address';
            isValid = false;
        }
    }
    
    // Phone validation (Indian format)
    if (field.name === 'phone_number' && value) {
        const phoneRegex = /^[6-9]\d{9}$/;
        if (!phoneRegex.test(value)) {
            errorMessage = 'Please enter a valid 10-digit mobile number';
            isValid = false;
        }
    }
    
    // Password validation
    if (field.name === 'password1' && value) {
        if (value.length < 8) {
            errorMessage = 'Password must be at least 8 characters long';
            isValid = false;
        }
    }
    
    // Password confirmation
    if (field.name === 'password2' && value) {
        const password1 = document.querySelector('[name="password1"]');
        if (password1 && value !== password1.value) {
            errorMessage = 'Passwords do not match';
            isValid = false;
        }
    }
    
    // Price validation
    if (field.name === 'price_per_day' && value) {
        const price = parseFloat(value);
        if (isNaN(price) || price <= 0) {
            errorMessage = 'Please enter a valid price';
            isValid = false;
        }
    }
    
    if (!isValid) {
        showFieldError(field, errorMessage);
    } else {
        clearFieldError(field);
    }
    
    return isValid;
}

function showFieldError(field, message) {
    clearFieldError(field);
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error';
    errorDiv.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
    
    field.classList.add('error');
    field.parentElement.appendChild(errorDiv);
}

function clearFieldError(field) {
    field.classList.remove('error');
    const errorDiv = field.parentElement.querySelector('.field-error');
    if (errorDiv) {
        errorDiv.remove();
    }
}

function initInputAnimations() {
    // Floating label effect
    document.querySelectorAll('.form-input').forEach(input => {
        const wrapper = input.closest('.input-wrapper');
        if (!wrapper) return;
        
        // Check if input has value on load
        if (input.value.trim()) {
            wrapper.classList.add('has-value');
        }
        
        input.addEventListener('focus', function() {
            wrapper.classList.add('focused');
        });
        
        input.addEventListener('blur', function() {
            wrapper.classList.remove('focused');
            if (this.value.trim()) {
                wrapper.classList.add('has-value');
            } else {
                wrapper.classList.remove('has-value');
            }
        });
        
        input.addEventListener('input', function() {
            if (this.value.trim()) {
                wrapper.classList.add('has-value');
            } else {
                wrapper.classList.remove('has-value');
            }
        });
    });
}

function initFileUpload() {
    document.querySelectorAll('input[type="file"]').forEach(input => {
        const wrapper = input.closest('.image-upload-wrapper');
        if (!wrapper) return;
        
        const uploadArea = wrapper.querySelector('.image-upload-area');
        const preview = wrapper.querySelector('.image-preview');
        
        // Drag and drop functionality
        if (uploadArea) {
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                uploadArea.addEventListener(eventName, preventDefaults, false);
            });
            
            ['dragenter', 'dragover'].forEach(eventName => {
                uploadArea.addEventListener(eventName, () => {
                    uploadArea.classList.add('drag-over');
                }, false);
            });
            
            ['dragleave', 'drop'].forEach(eventName => {
                uploadArea.addEventListener(eventName, () => {
                    uploadArea.classList.remove('drag-over');
                }, false);
            });
            
            uploadArea.addEventListener('drop', function(e) {
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    input.files = files;
                    handleFileSelect(input);
                }
            });
            
            uploadArea.addEventListener('click', () => input.click());
        }
        
        input.addEventListener('change', function() {
            handleFileSelect(this);
        });
    });
}

function handleFileSelect(input) {
    const file = input.files[0];
    if (!file) return;
    
    // File size validation (5MB)
    if (file.size > 5 * 1024 * 1024) {
        showNotification('File size must be less than 5MB', 'error');
        input.value = '';
        return;
    }
    
    // File type validation
    const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
    if (!validTypes.includes(file.type)) {
        showNotification('Please select a valid image file', 'error');
        input.value = '';
        return;
    }
    
    // Show preview
    const reader = new FileReader();
    reader.onload = function(e) {
        const wrapper = input.closest('.image-upload-wrapper');
        const uploadArea = wrapper.querySelector('.image-upload-area');
        const preview = wrapper.querySelector('.image-preview');
        const previewImg = wrapper.querySelector('#previewImage, .preview-image');
        
        if (previewImg) {
            previewImg.src = e.target.result;
            uploadArea.style.display = 'none';
            preview.style.display = 'block';
        }
    };
    reader.readAsDataURL(file);
}

function initAutoSave() {
    const forms = document.querySelectorAll('form[data-autosave]');
    
    forms.forEach(form => {
        const formId = form.dataset.autosave;
        
        // Load saved data
        loadFormData(form, formId);
        
        // Save data on input
        form.addEventListener('input', debounce(() => {
            saveFormData(form, formId);
        }, 1000));
        
        // Clear saved data on successful submit
        form.addEventListener('submit', () => {
            clearFormData(formId);
        });
    });
}

function saveFormData(form, formId) {
    const formData = new FormData(form);
    const data = {};
    
    for (let [key, value] of formData.entries()) {
        if (form.querySelector(`[name="${key}"]`).type !== 'file') {
            data[key] = value;
        }
    }
    
    localStorage.setItem(`form_${formId}`, JSON.stringify(data));
    console.log(`📝 Form data saved: ${formId}`);
}

function loadFormData(form, formId) {
    const savedData = localStorage.getItem(`form_${formId}`);
    if (!savedData) return;
    
    try {
        const data = JSON.parse(savedData);
        
        Object.entries(data).forEach(([key, value]) => {
            const field = form.querySelector(`[name="${key}"]`);
            if (field && value) {
                field.value = value;
                
                // Trigger input event for animations
                field.dispatchEvent(new Event('input', { bubbles: true }));
            }
        });
        
        console.log(`📋 Form data loaded: ${formId}`);
    } catch (e) {
        console.error('Error loading form data:', e);
    }
}

function clearFormData(formId) {
    localStorage.removeItem(`form_${formId}`);
    console.log(`🗑️ Form data cleared: ${formId}`);
}

/* ========================================
   NOTIFICATIONS SYSTEM
   ======================================== */
function initNotifications() {
    // Auto-hide Django messages
    setTimeout(() => {
        document.querySelectorAll('.alert').forEach(alert => {
            if (!alert.classList.contains('permanent')) {
                hideNotification(alert);
            }
        });
    }, 5000);
    
    // Close button functionality
    document.querySelectorAll('.alert-close').forEach(btn => {
        btn.addEventListener('click', function() {
            hideNotification(this.closest('.alert'));
        });
    });
}

function showNotification(message, type = 'info', duration = 5000) {
    const container = getNotificationContainer();
    
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} notification-slide-in`;
    
    const icon = getNotificationIcon(type);
    notification.innerHTML = `
        <i class="${icon}"></i>
        ${message}
        <button class="alert-close">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    container.appendChild(notification);
    
    // Close button functionality
    notification.querySelector('.alert-close').addEventListener('click', () => {
        hideNotification(notification);
    });
    
    // Auto-hide
    if (duration > 0) {
        setTimeout(() => {
            hideNotification(notification);
        }, duration);
    }
    
    return notification;
}

function hideNotification(notification) {
    notification.style.animation = 'slideOut 0.3s ease forwards';
    setTimeout(() => {
        if (notification.parentElement) {
            notification.parentElement.removeChild(notification);
        }
    }, 300);
}

function getNotificationContainer() {
    let container = document.querySelector('.notifications-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'notifications-container';
        document.body.appendChild(container);
    }
    return container;
}

function getNotificationIcon(type) {
    const icons = {
        success: 'fas fa-check-circle',
        error: 'fas fa-exclamation-circle',
        warning: 'fas fa-exclamation-triangle',
        info: 'fas fa-info-circle'
    };
    return icons[type] || icons.info;
}

/* ========================================
   UTILITY FUNCTIONS
   ======================================== */
function initUtilities() {
    // Price formatting
    formatPrices();
    
    // Copy to clipboard functionality
    initCopyToClipboard();
    
    // Confirmation dialogs
    initConfirmationDialogs();
    
    // Search functionality
    initSearch();
}

function formatPrices() {
    document.querySelectorAll('.price-amount').forEach(element => {
        const price = parseFloat(element.textContent.replace(/[₹,]/g, ''));
        if (!isNaN(price)) {
            element.textContent = `₹${price.toLocaleString('en-IN')}`;
        }
    });
}

function initCopyToClipboard() {
    document.querySelectorAll('[data-copy]').forEach(element => {
        element.addEventListener('click', function() {
            const text = this.dataset.copy;
            
            if (navigator.clipboard && window.isSecureContext) {
                navigator.clipboard.writeText(text).then(() => {
                    showNotification('Copied to clipboard!', 'success', 2000);
                });
            } else {
                // Fallback for older browsers
                const textArea = document.createElement('textarea');
                textArea.value = text;
                textArea.style.position = 'fixed';
                textArea.style.opacity = '0';
                document.body.appendChild(textArea);
                textArea.focus();
                textArea.select();
                
                try {
                    document.execCommand('copy');
                    showNotification('Copied to clipboard!', 'success', 2000);
                } catch (err) {
                    showNotification('Failed to copy', 'error', 2000);
                }
                
                document.body.removeChild(textArea);
            }
        });
    });
}

function initConfirmationDialogs() {
    document.querySelectorAll('[data-confirm]').forEach(element => {
        element.addEventListener('click', function(e) {
            const message = this.dataset.confirm;
            if (!confirm(message)) {
                e.preventDefault();
                return false;
            }
        });
    });
}

function initSearch() {
    const searchInputs = document.querySelectorAll('.search-input');
    
    searchInputs.forEach(input => {
        let searchTimeout;
        
        input.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();
            
            if (query.length >= 3) {
                searchTimeout = setTimeout(() => {
                    performSearch(query);
                }, 500);
            }
        });
    });
}

function performSearch(query) {
    // This would typically make an AJAX request to search
    console.log(`🔍 Searching for: ${query}`);
    
    // For now, just log the search
    // In a real app, you'd implement live search here
}

/* ========================================
   HELPER FUNCTIONS
   ======================================== */

// Prevent default behavior
function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

// Debounce function for performance
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Throttle function for scroll events
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Format currency
function formatCurrency(amount, currency = '₹') {
    return `${currency}${parseFloat(amount).toLocaleString('en-IN')}`;
}

// Generate random ID
function generateId(prefix = 'id') {
    return `${prefix}_${Math.random().toString(36).substr(2, 9)}`;
}

/* ========================================
   GLOBAL EVENT HANDLERS
   ======================================== */

// Handle back button
window.addEventListener('popstate', function(event) {
    // Handle browser back button if needed
    console.log('🔙 Browser back button pressed');
});

// Handle online/offline status
window.addEventListener('online', function() {
    showNotification('You are back online!', 'success', 3000);
});

window.addEventListener('offline', function() {
    showNotification('You are now offline', 'warning', 0);
});

// Handle visibility change (tab switching)
document.addEventListener('visibilitychange', function() {
    if (document.visibilityState === 'visible') {
        console.log('👁️ User returned to tab');
        // Refresh data if needed
    } else {
        console.log('👁️ User left tab');
        // Pause animations or save data
    }
});

// Global error handler
window.addEventListener('error', function(event) {
    console.error('🚨 Global error:', event.error);
    // In production, you might want to report errors to a service
});

// Console welcome message
console.log(`
🏠 Welcome to Rentz!
📅 Loaded: ${new Date().toLocaleString()}
🚀 App ready for rentals!

Built with ❤️ using Django + Modern JavaScript
`);

/* ========================================
   EXPORT FUNCTIONS FOR GLOBAL USE
   ======================================== */
window.RentzApp = {
    showNotification,
    hideNotification,
    formatCurrency,
    generateId,
    validateField,
    showFieldError,
    clearFieldError
};
