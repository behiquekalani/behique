/* Behike A/B Test Snippet - drop into any sales page */
(function () {
  const API = window.AB_API || "http://localhost:8100";
  const TEST = document.body.dataset.abTest || "default";
  const PRODUCT = document.body.dataset.abProduct || "unknown";
  let variant = null;
  let visitorId = null;

  fetch(`${API}/ab/variant?test=${TEST}&product=${PRODUCT}`, {
    credentials: "include",
  })
    .then((r) => r.json())
    .then((data) => {
      variant = data.variant;
      visitorId = data.visitor_id;
      document.body.classList.add(
        variant === "A" ? "variant-a" : "variant-b"
      );
      document.body.dataset.abVariant = variant;
    })
    .catch(() => {});

  function convert() {
    if (!variant) return;
    fetch(`${API}/ab/convert`, {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        variant: variant,
        product: PRODUCT,
        test: TEST,
        visitor_id: visitorId,
      }),
    }).catch(() => {});
  }

  document.addEventListener("click", function (e) {
    const btn = e.target.closest("[data-ab-convert], .buy-btn, .purchase-btn");
    if (btn) convert();
  });

  window.abConvert = convert;
})();
/* Usage: add to page. CSS: .variant-a .buy-btn { background: #00ffc8; }
   .variant-b .buy-btn { background: #ff6b00; }
   Body attrs: data-ab-test="headline-test" data-ab-product="ebook-1" */
