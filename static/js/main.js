/* ShareMeal Core Client Utilities */

document.addEventListener("DOMContentLoaded", () => {
  // 1. Auto-dismiss flash alerts after 6 seconds
  const alerts = document.querySelectorAll(".alert");
  alerts.forEach((alert) => {
    const closeBtn = alert.querySelector(".alert-close");
    if (closeBtn) {
      closeBtn.addEventListener("click", () => {
        alert.style.display = "none";
      });
    }
    // Auto-dismiss success and info alerts
    if (alert.classList.contains("alert-success") || alert.classList.contains("alert-info")) {
      setTimeout(() => {
        alert.style.opacity = "0";
        alert.style.transition = "opacity 0.4s ease";
        setTimeout(() => alert.style.display = "none", 400);
      }, 6000);
    }
  });

  // 2. Mobile navbar toggle
  const navToggle = document.querySelector(".navbar-toggle");
  const navMenu = document.querySelector(".navbar-nav");
  if (navToggle && navMenu) {
    navToggle.addEventListener("click", () => {
      const isVisible = navMenu.style.display === "flex";
      navMenu.style.display = isVisible ? "none" : "flex";
      navMenu.style.flexDirection = "column";
      navMenu.style.position = "absolute";
      navMenu.style.top = "var(--navbar-height)";
      navMenu.style.left = "0";
      navMenu.style.right = "0";
      navMenu.style.backgroundColor = "#FFFFFF";
      navMenu.style.padding = "1rem";
      navMenu.style.borderBottom = "1px solid var(--color-border)";
    });
  }

  // 3. Modal helper functions
  window.openModal = function(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.add("show");
      document.body.style.overflow = "hidden";
    }
  };

  window.closeModal = function(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.remove("show");
      document.body.style.overflow = "auto";
    }
  };

  // Close modals when clicking backdrop
  document.querySelectorAll(".modal-backdrop").forEach((backdrop) => {
    backdrop.addEventListener("click", (e) => {
      if (e.target === backdrop) {
        backdrop.classList.remove("show");
        document.body.style.overflow = "auto";
      }
    });
  });

  // 4. Quick confirmation prompts for destructive actions
  document.querySelectorAll("[data-confirm]").forEach((el) => {
    el.addEventListener("click", (e) => {
      const msg = el.getAttribute("data-confirm") || "Are you sure you want to proceed?";
      if (!confirm(msg)) {
        e.preventDefault();
      }
    });
  });
});
