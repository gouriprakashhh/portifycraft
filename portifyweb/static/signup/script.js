// scripts.js
function togglePassword(id) {
    const input = document.getElementById(id);
    input.type = input.type === "password" ? "text" : "password";
  }
  
  document.getElementById("signupForm").addEventListener("submit", function (e) {
    e.preventDefault();
  
    const name = document.getElementById("name").value.trim();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();
    const confirmPassword = document.getElementById("confirm_password").value.trim();
  
    let isValid = true;
    document.querySelectorAll(".error").forEach(el => el.textContent = "");
  
    if (name.length < 2) {
      document.getElementById("nameError").textContent = "Enter your full name.";
      isValid = false;
    }
  
    const emailPattern = /^[^ ]+@[^ ]+\.[a-z]{2,}$/;
    if (!emailPattern.test(email)) {
      document.getElementById("emailError").textContent = "Enter a valid email address.";
      isValid = false;
    }
  
    if (password.length < 6) {
      document.getElementById("passwordError").textContent = "Password must be at least 6 characters.";
      isValid = false;
    }
  
    if (password !== confirmPassword) {
      document.getElementById("confirmPasswordError").textContent = "Passwords do not match.";
      isValid = false;
    }
  
    if (isValid) {
      this.submit(); // Let Django handle form processing
    }
  });
  