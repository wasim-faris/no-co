 function togglePassword(inputId, el) {
            const input = document.getElementById(inputId);
            if (input.type === "password") {
                input.type = "text";
                el.classList.remove('hidden-pass');
                el.classList.add('visible-pass');
            } else {
                input.type = "password";
                el.classList.remove('visible-pass');
                el.classList.add('hidden-pass');
            }
        }
   function togglePassword(id, btn) {
        const input = document.getElementById(id);
        input.type = input.type === 'password' ? 'text' : 'password';
    }

/**
 * NØ&Co Premium Toast System
 */
 /**
         * Toast Logic Implementation
         */
        const showToast = (message, type = 'error') => {
            const container = document.getElementById('toast-container');
            if (!container) return;

            const toast = document.createElement('div');
            toast.className = `toast-pill ${type}`;

            // Minimal Icon SVG
            const icon = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" class="mr-4"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>`;

            toast.innerHTML = `
                <span class="text-black">${icon}</span>
                <span class="toast-text">${message}</span>
            `;

            container.appendChild(toast);

            // Reflow and animate
            requestAnimationFrame(() => {
                toast.classList.add('show');
            });

            // Remove automatically after 4 seconds
            setTimeout(() => {
                toast.classList.remove('show');
                setTimeout(() => toast.remove(), 700);
            }, 4000);
        };

        // Listen for Django backend messages on load
        document.addEventListener('DOMContentLoaded', () => {
            const dataElement = document.getElementById('django-messages');
            if (dataElement) {
                try {
                    const messages = JSON.parse(dataElement.textContent);
                    messages.forEach(msg => {
                        showToast(msg.message, msg.tags.includes('error') ? 'error' : 'success');
                    });
                } catch (e) {
                    console.error("Failed to parse backend messages");
                }
            }
        });

        // Function for Password Visibility (as used in the HTML)
        function togglePassword(inputId, button) {
            const input = document.getElementById(inputId);
            const isPassword = input.type === 'password';
            input.type = isPassword ? 'text' : 'password';
            button.style.opacity = isPassword ? '1' : '0.4';
        }
