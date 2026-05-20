/**
 * Global Validation Utilities
 */

const ValidationUtils = {
    /**
     * Validates that the input is not just special characters or empty.
     * @param {string} value 
     * @returns {boolean}
     */
    isMeaningful: function(value) {
        if (!value) return false;
        const trimmed = value.trim();
        if (!trimmed) return false;

        // Reject if it contains ONLY symbols, underscores, dashes, dots, spaces
        const onlySpecial = /^[\s._\-!@#$%^&*()=+\[\]{};':",.<>/?|\\`~]+$/;
        if (onlySpecial.test(trimmed)) return false;

        // Must contain at least one alphanumeric character
        const hasAlphanumeric = /[a-zA-Z0-9]/;
        if (!hasAlphanumeric.test(trimmed)) return false;

        // Prevent consecutive unnecessary special characters (3 or more)
        const excessiveSpecial = /([._\-!@#$%^&*()=+\[\]{};':",.<>/?|\\`~])\1{2,}/;
        if (excessiveSpecial.test(trimmed)) return false;

        return true;
    },

    /**
     * Validates a phone number based on strict production rules.
     * @param {string} value 
     * @returns {{valid: boolean, message: string}}
     */
    validatePhone: function(value) {
        if (!value) return { valid: false, message: "Phone number is required" };
        const phone = value.trim();
        
        if (!/^\d+$/.test(phone)) return { valid: false, message: "Phone number must contain only digits" };
        if (phone.length !== 10) return { valid: false, message: "Phone number must be exactly 10 digits" };
        if (!/^[6-9]/.test(phone)) return { valid: false, message: "Phone number must start with 6, 7, 8, or 9" };
        
        // Reject repeated digits (e.g., 0000000000)
        if (new Set(phone).size === 1) return { valid: false, message: "Invalid phone number (repeated digits)" };
        
        // Reject obvious fake sequences
        const fakeSequences = ["0123456789", "1234567890", "9876543210"];
        if (fakeSequences.includes(phone)) return { valid: false, message: "Please enter a realistic phone number" };
        
        return { valid: true, message: "" };
    },

    /**
     * Shows an inline error message near the element.
     * @param {HTMLElement} element 
     * @param {string} message 
     */
    showError: function(element, message) {
        this.clearError(element);
        
        let errorEl = null;
        if (element.id) {
            // Check for new UX patterns like id="editPhone_error" or "err-edit-phone"
            errorEl = document.getElementById(element.id + '_error') || document.getElementById('err-' + element.id);
        }
        
        if (errorEl) {
            errorEl.textContent = message;
            errorEl.classList.remove('hidden');
            if (errorEl.style.display === 'none') errorEl.style.display = '';
            
            element.style.borderColor = '#dc2626';
            if (element.classList.contains('border-gray-200')) {
                element.classList.remove('border-gray-200');
                element.classList.add('border-red-500');
            }
            errorEl.dataset.vuSet = "true";
        } else {
            const errorDiv = document.createElement('div');
            errorDiv.className = 'validation-error-message';
            errorDiv.style.color = '#dc2626';
            errorDiv.style.fontSize = '11px';
            errorDiv.style.marginTop = '4px';
            errorDiv.style.fontFamily = 'Inter, sans-serif';
            errorDiv.textContent = message;
            
            const targetParent = element.classList.contains('input-field') ? element.parentNode : element.parentNode;
            targetParent.appendChild(errorDiv);
            element.style.borderColor = '#dc2626';
        }
    },

    /**
     * Clears inline error message.
     * @param {HTMLElement} element 
     */
    clearError: function(element) {
        let errorEl = null;
        if (element.id) {
            errorEl = document.getElementById(element.id + '_error') || document.getElementById('err-' + element.id);
        }
        
        if (errorEl && errorEl.dataset.vuSet === "true") {
            errorEl.textContent = '';
            errorEl.classList.add('hidden');
            if (errorEl.style.display === '') errorEl.style.display = 'none';
            delete errorEl.dataset.vuSet;
        }

        const parent = element.parentNode;
        const existingError = parent.querySelector('.validation-error-message');
        if (existingError) {
            existingError.remove();
        }
        
        element.style.borderColor = '';
        if (element.classList.contains('border-red-500')) {
            element.classList.remove('border-red-500');
            element.classList.add('border-gray-200');
        }
    },

    /**
     * Attaches real-time strict phone validation to an input.
     */
    attachPhoneValidation: function(inputSelector, submitBtnSelector, ajaxUrl) {
        const input = document.querySelector(inputSelector);
        const submitBtn = submitBtnSelector ? document.querySelector(submitBtnSelector) : null;
        if (!input) return;

        let debounceTimer = null;
        let abortController = null;

        // Force digits only in real-time
        input.addEventListener('input', (e) => {
            const originalValue = e.target.value;
            const cleanedValue = originalValue.replace(/\D/g, '').slice(0, 10);
            if (originalValue !== cleanedValue) {
                e.target.value = cleanedValue;
            }
        });

        const setSubmitState = (enabled) => {
            // This is now handled by the form state watcher if attached, 
            // but we keep this for backwards compatibility or standalone inputs.
            if (submitBtn && !input.form) { 
                submitBtn.disabled = !enabled;
                submitBtn.style.opacity = enabled ? '1' : '0.6';
            }
            input.dataset.isValid = enabled ? "true" : "false";
            // Trigger a custom event for the form watcher
            input.dispatchEvent(new CustomEvent('validation-update', { detail: { valid: enabled } }));
        };

        const showChecking = () => {
            this.clearError(input);
            const existing = input.parentNode.querySelector('.phone-checking-msg');
            if (!existing) {
                const div = document.createElement('div');
                div.className = 'phone-checking-msg';
                div.style.cssText = 'color:#888;font-size:11px;margin-top:4px;font-family:Inter,sans-serif;display:flex;align-items:center;gap:6px;';
                div.innerHTML = '<span class="checking-dot" style="width:6px;height:6px;background:#C9A96E;border-radius:50%;animation:pulse 1s infinite;"></span> Checking phone number…';
                input.parentNode.appendChild(div);
            }
            input.style.borderColor = '#C9A96E';
            input.dataset.pending = "true";
            setSubmitState(false);
        };

        const clearChecking = () => {
            const el = input.parentNode.querySelector('.phone-checking-msg');
            if (el) el.remove();
            input.style.borderColor = '';
            delete input.dataset.pending;
        };

        const validate = async (silent = false) => {
            const value = input.value.trim();
            
            if (!value && !input.required) {
                clearChecking();
                this.clearError(input);
                setSubmitState(true);
                return;
            }

            const localResult = this.validatePhone(value);
            if (!localResult.valid) {
                if (abortController) abortController.abort();
                clearChecking();
                this.showError(input, localResult.message);
                setSubmitState(false);
                return;
            }

            if (!ajaxUrl) {
                clearChecking();
                this.clearError(input);
                setSubmitState(true);
                return;
            }

            if (abortController) abortController.abort();
            abortController = new AbortController();

            if (!silent) showChecking();

            try {
                const timeoutId = setTimeout(() => abortController.abort(), 8000);
                const res = await fetch(`${ajaxUrl}?phone=${encodeURIComponent(value)}&region=IN`, {
                    headers: { 'X-Requested-With': 'XMLHttpRequest' },
                    signal: abortController.signal
                });
                clearTimeout(timeoutId);
                
                const data = await res.json();
                clearChecking();
                
                if (data.valid) {
                    this.clearError(input);
                    setSubmitState(true);
                } else {
                    this.showError(input, data.message || 'Invalid mobile number');
                    setSubmitState(false);
                }
            } catch (err) {
                if (err.name === 'AbortError') return;
                clearChecking();
                this.clearError(input);
                setSubmitState(true); // Fallback to local
            }
        };

        input.addEventListener('input', () => {
            clearTimeout(debounceTimer);
            this.clearError(input);
            
            const value = input.value.trim();
            const localResult = this.validatePhone(value);
            
            if (localResult.valid) {
                if (ajaxUrl) {
                    input.dataset.pending = "true";
                    setSubmitState(false);
                    debounceTimer = setTimeout(() => validate(true), 400); // Silent AJAX check
                } else {
                    input.dataset.isValid = "true";
                    setSubmitState(true);
                }
            } else {
                input.dataset.isValid = "false";
                setSubmitState(false);
                if (value.length > 0) {
                    this.showError(input, localResult.message);
                } else if (input.required) {
                    this.showError(input, "Phone number is required");
                }
            }
        });

        input.addEventListener('blur', () => {
            if (input.dataset.pending !== "true" && input.dataset.isValid !== "true") {
                validate(false);
            }
        });
    },

    /**
     * Watches a form and keeps the submit button synchronized with overall validity.
     * @param {string} formSelector 
     * @param {string} submitBtnSelector 
     * @param {Object} validationMap { fieldSelector: validationFn }
     */
    watchForm: function(formSelector, submitBtnSelector, validationMap) {
        const form = document.querySelector(formSelector);
        const submitBtn = document.querySelector(submitBtnSelector);
        if (!form || !submitBtn) return;

        const checkFormValidity = () => {
            let isFormValid = true;

            for (const [selector, validateFn] of Object.entries(validationMap)) {
                const input = form.querySelector(selector);
                if (!input) continue;
                
                let fieldValid = true;

                // Check if field is required and empty
                if (input.required && !input.value.trim()) {
                    fieldValid = false;
                }
                // Check pending AJAX states
                else if (input.dataset.pending === "true") {
                    fieldValid = false;
                }
                // Check explicit validity markers (set by real-time listeners)
                else if (input.dataset.isValid === "false") {
                    fieldValid = false;
                }
                // Run custom validation function if provided
                else if (validateFn && !validateFn(input.value)) {
                    fieldValid = false;
                }
                
                if (!fieldValid) {
                    isFormValid = false;
                }
            }

            submitBtn.disabled = !isFormValid;
            if (isFormValid) {
                submitBtn.classList.remove('opacity-50', 'cursor-not-allowed', 'pointer-events-none');
                submitBtn.style.opacity = '1';
                submitBtn.style.cursor = 'pointer';
            } else {
                submitBtn.classList.add('opacity-50', 'cursor-not-allowed', 'pointer-events-none');
                submitBtn.style.opacity = '0.5';
                submitBtn.style.cursor = 'not-allowed';
            }
            
            // If invalid, ensure loader is hidden
            if (!isFormValid) {
                const spinner = submitBtn.querySelector('.inline-spinner, .btn-loader');
                if (spinner) {
                    spinner.remove();
                    submitBtn.style.color = '';
                    if (submitBtn.dataset.originalText) {
                        submitBtn.innerHTML = submitBtn.dataset.originalText;
                    }
                }
                delete form.dataset.submitting;
            }
            return isFormValid;
        };

        // Attach listeners to all fields in the map
        Object.keys(validationMap).forEach(selector => {
            const input = form.querySelector(selector);
            if (!input) return;

            ['input', 'change', 'blur', 'validation-update'].forEach(evtType => {
                input.addEventListener(evtType, checkFormValidity);
            });
            
            // Initial check
            input.dataset.isValid = "true"; // Assume valid initially if not empty, or let listeners handle it
        });

        // Run once on init
        setTimeout(checkFormValidity, 100);
        
        return checkFormValidity; // Return for manual triggers
    }
};

// Add CSS for checking pulse
const style = document.createElement('style');
style.textContent = `
    @keyframes pulse {
        0% { opacity: 0.4; transform: scale(0.8); }
        50% { opacity: 1; transform: scale(1.1); }
        100% { opacity: 0.4; transform: scale(0.8); }
    }
`;
document.head.appendChild(style);

// Auto-trim inputs on blur
document.addEventListener('blur', function(e) {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
        if (e.target.type !== 'file' && e.target.type !== 'password') {
            e.target.value = e.target.value.trim();
        }
    }
}, true);
