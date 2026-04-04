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

