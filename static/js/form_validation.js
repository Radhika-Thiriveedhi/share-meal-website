/* ShareMeal Real-Time Client Form Validation */

document.addEventListener("DOMContentLoaded", () => {
  // Password strength meter
  const passwordInputs = document.querySelectorAll("input[type='password'][data-validate-strength]");
  passwordInputs.forEach((input) => {
    input.addEventListener("input", () => {
      const val = input.value;
      const feedback = document.getElementById(input.getAttribute("data-feedback-id"));
      if (!feedback) return;

      const hasMinLength = val.length >= 8;
      const hasUpper = /[A-Z]/.test(val);
      const hasLower = /[a-z]/.test(val);
      const hasDigit = /[0-9]/.test(val);

      if (hasMinLength && hasUpper && hasLower && hasDigit) {
        feedback.textContent = "Strong password";
        feedback.style.color = "var(--color-primary)";
      } else {
        feedback.textContent = "Requires 8+ characters, uppercase, lowercase, and number.";
        feedback.style.color = "var(--color-text-muted)";
      }
    });
  });

  // Food donation deadline validation helper
  const prepInput = document.querySelector("input[name='preparation_datetime']");
  const deadlineInput = document.querySelector("input[name='collection_deadline']");
  if (prepInput && deadlineInput) {
    const validateDates = () => {
      if (!prepInput.value || !deadlineInput.value) return;
      const prepDate = new Date(prepInput.value);
      const deadlineDate = new Date(deadlineInput.value);
      const now = new Date();

      const warningEl = document.getElementById("date-validation-warning");
      if (!warningEl) return;

      if (deadlineDate <= prepDate) {
        warningEl.textContent = "Collection deadline must be after preparation time.";
        warningEl.style.display = "block";
      } else if (deadlineDate <= now) {
        warningEl.textContent = "Collection deadline cannot be in the past.";
        warningEl.style.display = "block";
      } else {
        warningEl.style.display = "none";
      }
    };
    prepInput.addEventListener("change", validateDates);
    deadlineInput.addEventListener("change", validateDates);
  }
});
