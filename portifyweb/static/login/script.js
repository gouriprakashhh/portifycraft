function togglePassword() {
    const passwordInput = document.getElementById("password");
    const toggleBtn = document.querySelector(".toggle-btn");

    if (passwordInput.type === "password") {
        passwordInput.type = "text";
        toggleBtn.textContent = "Hide";
    } else {
        passwordInput.type = "password";
        toggleBtn.textContent = "Show";
    }
}

// Auto-hide error message after 5 seconds
setTimeout(() => {
    const error = document.querySelector(".error-message");
    if (error) {
        error.style.opacity = "0";
    }
}, 3000);

// Form validation
function validateForm() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    
    let isValid = true;

    // Clear previous error messages
    document.querySelectorAll(".error-message").forEach(msg => {
        msg.style.display = "none";
    });

    // Check if email is empty
    if (!email) {
        showError("email", "Email is required.");
        isValid = false;
    }

    // Check if password is empty
    if (!password) {
        showError("password", "Password is required.");
        isValid = false;
    }

    return isValid;
}

// Show error message
function showError(field, message) {
    const inputGroup = document.querySelector(`#${field}`).closest(".input-group");
    const errorDiv = document.createElement("div");
    errorDiv.classList.add("error-message");
    errorDiv.textContent = message;
    inputGroup.appendChild(errorDiv);
}
