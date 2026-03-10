 function moveNext(current, index) {
            if (current.value.length >= 1) {
                const next = current.parentElement.children[index];
                if (next) next.focus();
            }
        }
