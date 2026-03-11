/**
 * NØ&Co Premium Toast System
 */
const showToast = (message, type = 'error') => {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast-pill ${type}`;

    const icon = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" class="mr-4">
        <circle cx="12" cy="12" r="10"></circle>
        <line x1="12" y1="8" x2="12" y2="12"></line>
        <line x1="12" y1="16" x2="12.01" y2="16"></line>
    </svg>`;

    toast.innerHTML = `
        <span class="text-black">${icon}</span>
        <span class="toast-text">${message}</span>
    `;

    container.appendChild(toast);

    requestAnimationFrame(() => {
        toast.classList.add('show');
    });

    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 700);
    }, 4000);
};


/**
 * Page Initialization
 */
document.addEventListener('DOMContentLoaded', () => {

    /* Django Backend Messages */
    const dataElement = document.getElementById('django-messages');
    if (dataElement) {
        try {
            const messages = JSON.parse(dataElement.textContent);

            messages.forEach(msg => {
                showToast(
                    msg.message,
                    msg.tags.includes('error') ? 'error' : 'success'
                );
            });

        } catch (e) {
            console.error("Failed to parse Django messages");
        }
    }


    /* Form Loader */
    const signupForm = document.getElementById('signupForm');
    const submitBtn = document.getElementById('submitBtn');
    const btnText = document.getElementById('btnText');
    const btnSpinner = document.getElementById('btnSpinner');

    if (signupForm) {
        signupForm.addEventListener('submit', () => {

            btnText.innerText = "Sending OTP...";
            btnSpinner.classList.remove('hidden');

            submitBtn.disabled = true;
            submitBtn.classList.add('opacity-70', 'cursor-not-allowed');
        });
    }


    /* Tooltip Initialization */
    if (typeof tippy !== 'undefined') {

        tippy('.info-icon', {
            content: (ref) => ref.getAttribute('data-tippy-content'),
            theme: 'minimal-dark',
            animation: 'shift-away',
            duration: 200,
            arrow: false,
            offset: [0, 8],
            appendTo: document.body
        });

    }

});


/**
 * Toggle Password Visibility
 */
function togglePassword(inputId, button) {

    const input = document.getElementById(inputId);
    if (!input) return;

    const isPassword = input.type === 'password';

    input.type = isPassword ? 'text' : 'password';

    button.style.opacity = isPassword ? '1' : '0.4';
}

window.addEventListener("pageshow", function () {

    const submitBtn = document.getElementById("submitBtn");
    const btnText = document.getElementById("btnText");
    const btnSpinner = document.getElementById("btnSpinner");

    if (submitBtn && btnText && btnSpinner) {

        btnText.innerText = "Register";
        btnSpinner.classList.add("hidden");

        submitBtn.disabled = false;
        submitBtn.classList.remove("opacity-70", "cursor-not-allowed");
    }

});
