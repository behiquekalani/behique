// Behike Theme - Global JavaScript
// (c) 2026 Behike | MIT License

document.addEventListener("DOMContentLoaded", function() {
  // Collapsible content toggle
  var details = document.querySelectorAll(".collapsible-content__item");
  details.forEach(function(detail) {
    detail.addEventListener("toggle", function() {
      if (detail.open) {
        details.forEach(function(other) {
          if (other !== detail && other.open) {
            other.removeAttribute("open");
          }
        });
      }
    });
  });
});
