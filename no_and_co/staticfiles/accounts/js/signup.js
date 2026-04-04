
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
