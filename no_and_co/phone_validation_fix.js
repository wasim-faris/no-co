function applyPhoneValidation(phoneInputId, submitBtnId) {
    const phoneInput = document.getElementById(phoneInputId);
    const submitBtn = document.getElementById(submitBtnId);
    if (!phoneInput || !submitBtn) return;
    
    // Check initial state
    validatePhoneRealTime();

    phoneInput.addEventListener('input', function() {
        // Allow only numbers
        this.value = this.value.replace(/\D/g, '');
        // Restrict to 10 digits
        if (this.value.length > 10) {
            this.value = this.value.slice(0, 10);
        }
        validatePhoneRealTime();
    });

    function validatePhoneRealTime() {
        const val = phoneInput.value.trim();
        const isValid = /^\d{10}$/.test(val);
        submitBtn.disabled = !isValid;
        if (!isValid) {
            submitBtn.style.opacity = '0.5';
            submitBtn.style.cursor = 'not-allowed';
        } else {
            submitBtn.style.opacity = '1';
            submitBtn.style.cursor = 'pointer';
        }
    }
}
