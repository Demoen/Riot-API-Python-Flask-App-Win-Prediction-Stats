/**
 * LoL Win Predictor - Interactive Features
 * Enhanced user experience with smooth animations and interactions
 */

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initAnimations();
    initTooltips();
    initChartAnimations();
    initScrollEffects();
});

/**
 * Initialize entrance animations
 */
function initAnimations() {
    // Add fade-in animation to all cards
    const cards = document.querySelectorAll('.card, .feature-card, .match-card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

/**
 * Initialize tooltips for stats
 */
function initTooltips() {
    const statCards = document.querySelectorAll('.stat-card');
    
    statCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transition = 'all 0.3s ease';
            this.style.transform = 'translateY(-5px) scale(1.02)';
            this.style.boxShadow = '0 10px 25px rgba(56, 189, 248, 0.3)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
            this.style.boxShadow = '';
        });
    });
}

/**
 * Animate charts when they come into view
 */
function initChartAnimations() {
    const charts = document.querySelectorAll('canvas');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '0';
                entry.target.style.transform = 'scale(0.95)';
                
                setTimeout(() => {
                    entry.target.style.transition = 'all 0.8s cubic-bezier(0.4, 0, 0.2, 1)';
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'scale(1)';
                }, 200);
                
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.2 });
    
    charts.forEach(chart => observer.observe(chart));
}

/**
 * Scroll-based reveal effects
 */
function initScrollEffects() {
    const revealElements = document.querySelectorAll('.card, .feature-card');
    
    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('reveal-active');
            }
        });
    }, {
        threshold: 0.15,
        rootMargin: '0px 0px -50px 0px'
    });
    
    revealElements.forEach(el => revealObserver.observe(el));
}

/**
 * Format numbers with commas
 */
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

/**
 * Copy text to clipboard
 */
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showNotification('Copied to clipboard!', 'success');
        });
    }
}

/**
 * Show notification
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#22c55e' : '#38bdf8'};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
        z-index: 1000;
        animation: slideInRight 0.3s ease-out;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

/**
 * Add keyboard shortcuts
 */
document.addEventListener('keydown', function(e) {
    // Escape key to go back
    if (e.key === 'Escape') {
        const backBtn = document.querySelector('.back-btn');
        if (backBtn) backBtn.click();
    }
    
    // Ctrl/Cmd + K to focus search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('#riot_id');
        if (searchInput) searchInput.focus();
    }
});

/**
 * Smooth scroll to element
 */
function smoothScrollTo(element) {
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

/**
 * Add loading spinner to buttons
 */
function addButtonLoader(button) {
    const originalHTML = button.innerHTML;
    button.disabled = true;
    button.style.opacity = '0.7';
    button.innerHTML = `
        <span style="display: flex; align-items: center; justify-content: center; gap: 0.5rem;">
            <i class="fas fa-spinner fa-spin"></i>
            <span>Loading...</span>
        </span>
    `;
    
    return {
        remove: () => {
            button.disabled = false;
            button.style.opacity = '1';
            button.innerHTML = originalHTML;
        }
    };
}

// Export functions for use in HTML
window.LoLPredictor = {
    copyToClipboard,
    showNotification,
    smoothScrollTo,
    formatNumber,
    addButtonLoader
};

