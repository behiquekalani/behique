/**
 * Cart Abandonment Tracker
 * Detects when someone clicks "Buy" but doesn't complete purchase.
 * Fires POST to /cart/abandon with email from any form on page.
 * Drop this script on any product page.
 */
(function () {
  const API = window.CART_RECOVERY_API || "/cart/abandon";
  let buyClicked = false;
  let purchaseComplete = false;

  function getEmail() {
    const inputs = document.querySelectorAll('input[type="email"], input[name*="email"]');
    for (const input of inputs) {
      if (input.value && input.value.includes("@")) return input.value.trim();
    }
    return null;
  }

  function getProductSlug() {
    const meta = document.querySelector('meta[name="product-slug"]');
    if (meta) return meta.content;
    const path = window.location.pathname.split("/").filter(Boolean);
    return path[path.length - 1] || "unknown";
  }

  function sendAbandon() {
    if (!buyClicked || purchaseComplete) return;
    const email = getEmail();
    if (!email) return;
    const payload = JSON.stringify({
      email: email,
      product_slug: getProductSlug(),
      timestamp: new Date().toISOString(),
    });
    if (navigator.sendBeacon) {
      navigator.sendBeacon(API, new Blob([payload], { type: "application/json" }));
    } else {
      fetch(API, { method: "POST", body: payload, headers: { "Content-Type": "application/json" }, keepalive: true });
    }
  }

  document.addEventListener("click", function (e) {
    const btn = e.target.closest('button, a, [role="button"]');
    if (!btn) return;
    const text = (btn.textContent || "").toLowerCase();
    if (text.includes("buy") || text.includes("checkout") || text.includes("add to cart")) {
      buyClicked = true;
    }
  });

  window.addEventListener("beforeunload", sendAbandon);

  window.markPurchaseComplete = function () {
    purchaseComplete = true;
  };
})();
