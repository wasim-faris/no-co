 function toggleVisibility(id) {
            const input = document.getElementById(id);
            const btn = input.nextElementSibling;
            if (input.type === "password") {
                input.type = "text";
                btn.textContent = "Hide";
            } else {
                input.type = "password";
                btn.textContent = "Show";
            }
        }
