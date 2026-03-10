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
