document.addEventListener("DOMContentLoaded", function () {
    // Get the values of the form
    const inputs = document.querySelectorAll("#username, #email, #password, #confirm_password");

    inputs.forEach(input => {
        // Clear the validation indicator when the input is focused
        input.addEventListener("focus", function () {
            input.classList.remove("valid", "invalid");
            const validationIndicator = input.nextElementSibling;
            if (validationIndicator) {
                validationIndicator.textContent = "";
            }
        });

        // When the input is blurred, validate the input
        input.addEventListener("blur", function () {
            validateInput(input);
        });

        // When the input value changes, validate the input
        input.addEventListener("input", function () {
            validateInput(input);
        });
    });

    function validateInput(input) {
        // Get the value of the input and trim it
        const value = input.value.trim();
        let isValid = true;

        // Validate the input based on the input id
        if (input.id === "username") {
            if (value.length < 2 || value.length > 20) {
                isValid = false;
            }
        } else if (input.id === "email") {
            const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailPattern.test(value)) {
                isValid = false;
            }
        } else if (input.id === "password") {
            if (value.length < 6 || !/[A-Z]/.test(value) || !/[a-z]/.test(value) || !/[0-9]/.test(value)) {
                isValid = false;
            }
        } else if (input.id === "confirm_password") {
            const passwordValue = document.getElementById("password").value.trim();
            if (value !== passwordValue) {
                isValid = false;
            }
        }

        // Get the validation indicator element
        const validationIndicator = input.nextElementSibling;

        // Update the input style based on the validation result
        if (isValid) {
            input.classList.remove("invalid");
            input.classList.add("valid");
            if (validationIndicator) {
                validationIndicator.textContent = "✓";
                validationIndicator.style.color = "green";
            }
        } else {
            input.classList.remove("valid");
            input.classList.add("invalid");
            if (validationIndicator) {
                validationIndicator.textContent = "✖";
                validationIndicator.style.color = "red";
            }
        }
    }
});