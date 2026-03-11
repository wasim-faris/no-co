 function moveNext(current, index) {
            if (current.value.length >= 1) {
                const next = current.parentElement.children[index];
                if (next) next.focus();
            }
        }

        function moveNext(input) {

    let inputs = document.querySelectorAll(".otp-input");

    if (input.value.length === 1) {
        let next = input.nextElementSibling;
        if (next) {
            next.focus();
        }
    }

    // combine otp
    let otp = "";
    inputs.forEach(function(i){
        otp += i.value;
    });

    document.getElementById("otp").value = otp;
}

  function showToast(message) {
        const toast = document.getElementById('toast');
        const msgSpan = document.getElementById('toast-message');
        msgSpan.innerText = message;
        toast.classList.add('show');
        setTimeout(() => {
            toast.classList.remove('show');
        }, 4000);
    }

       document.addEventListener("DOMContentLoaded", () => {

    const form = document.querySelector("form");
    const verifyBtn = document.getElementById("verifyBtn");
    const verifyText = document.getElementById("verifyText");
    const verifySpinner = document.getElementById("verifySpinner");

    if(form){
        form.addEventListener("submit", () => {

            verifyText.innerText = "Verifying...";
            verifySpinner.classList.remove("hidden");

            verifyBtn.disabled = true;
            verifyBtn.classList.add("opacity-70","cursor-not-allowed");

        });
    }

});

