/**
 * Testimonial Carousel Widget
 * Embeddable social proof component for Behike landing pages.
 * Reads from testimonials.json. Rotates every 5 seconds.
 * Copyright 2026 Behike.
 *
 * Usage:
 *   <div id="testimonial-carousel"></div>
 *   <script src="testimonial_widget.js"></script>
 *   <script>TestimonialCarousel.init({ container: '#testimonial-carousel' });</script>
 */

const TestimonialCarousel = (() => {
  // Default placeholder testimonials (replace with real ones from beta readers)
  const PLACEHOLDER_TESTIMONIALS = [
    {
      name: "[Beta reader feedback pending]",
      rating: 5,
      quote: "Review coming soon from our beta reader program.",
      product: "AI Automation Blueprint",
      date: "2026-03",
      verified: false
    },
    {
      name: "[Beta reader feedback pending]",
      rating: 5,
      quote: "Review coming soon from our beta reader program.",
      product: "Solopreneur Starter Pack",
      date: "2026-03",
      verified: false
    },
    {
      name: "[Beta reader feedback pending]",
      rating: 5,
      quote: "Review coming soon from our beta reader program.",
      product: "Content Empire Kit",
      date: "2026-03",
      verified: false
    }
  ];

  let testimonials = [];
  let currentIndex = 0;
  let intervalId = null;
  let containerEl = null;

  function renderStars(rating) {
    let stars = '';
    for (let i = 1; i <= 5; i++) {
      stars += i <= rating
        ? '<span class="bk-star bk-star--filled">&#9733;</span>'
        : '<span class="bk-star">&#9734;</span>';
    }
    return stars;
  }

  function renderTestimonial(t, index, total) {
    const verifiedBadge = t.verified
      ? '<span class="bk-verified">Verified Reader</span>'
      : '';

    return `
      <div class="bk-testimonial-card">
        <div class="bk-testimonial-stars">${renderStars(t.rating)}</div>
        <blockquote class="bk-testimonial-quote">"${t.quote}"</blockquote>
        <div class="bk-testimonial-meta">
          <span class="bk-testimonial-name">${t.name}</span>
          ${verifiedBadge}
        </div>
        <div class="bk-testimonial-product">${t.product}</div>
        <div class="bk-testimonial-dots">
          ${Array.from({ length: total }, (_, i) =>
            `<span class="bk-dot ${i === index ? 'bk-dot--active' : ''}" data-index="${i}"></span>`
          ).join('')}
        </div>
      </div>
    `;
  }

  function injectStyles() {
    if (document.getElementById('bk-testimonial-styles')) return;

    const style = document.createElement('style');
    style.id = 'bk-testimonial-styles';
    style.textContent = `
      .bk-testimonial-carousel {
        max-width: 520px;
        margin: 2rem auto;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      }

      .bk-testimonial-card {
        background: #1a1a1a;
        border: 1px solid #2a2a2a;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        transition: opacity 0.4s ease;
      }

      .bk-testimonial-stars {
        margin-bottom: 1rem;
      }

      .bk-star {
        font-size: 1.25rem;
        color: #444;
        margin: 0 2px;
      }

      .bk-star--filled {
        color: #f5c542;
      }

      .bk-testimonial-quote {
        color: #e0e0e0;
        font-size: 1.05rem;
        line-height: 1.6;
        margin: 0 0 1.25rem 0;
        padding: 0;
        border: none;
        font-style: normal;
      }

      .bk-testimonial-meta {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.75rem;
        margin-bottom: 0.5rem;
      }

      .bk-testimonial-name {
        color: #fff;
        font-weight: 600;
        font-size: 0.95rem;
      }

      .bk-verified {
        background: #1a3a1a;
        color: #4ade80;
        font-size: 0.7rem;
        padding: 2px 8px;
        border-radius: 4px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
      }

      .bk-testimonial-product {
        color: #888;
        font-size: 0.8rem;
        margin-bottom: 1.25rem;
      }

      .bk-testimonial-dots {
        display: flex;
        justify-content: center;
        gap: 8px;
      }

      .bk-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #333;
        cursor: pointer;
        transition: background 0.3s ease;
      }

      .bk-dot--active {
        background: #f5c542;
      }

      .bk-dot:hover {
        background: #555;
      }
    `;
    document.head.appendChild(style);
  }

  function render() {
    if (!containerEl || testimonials.length === 0) return;
    containerEl.innerHTML = renderTestimonial(
      testimonials[currentIndex],
      currentIndex,
      testimonials.length
    );

    // Bind dot clicks
    containerEl.querySelectorAll('.bk-dot').forEach(dot => {
      dot.addEventListener('click', () => {
        currentIndex = parseInt(dot.dataset.index);
        render();
        resetInterval();
      });
    });
  }

  function next() {
    currentIndex = (currentIndex + 1) % testimonials.length;
    render();
  }

  function resetInterval() {
    if (intervalId) clearInterval(intervalId);
    intervalId = setInterval(next, 5000);
  }

  async function loadTestimonials(jsonPath) {
    try {
      const response = await fetch(jsonPath);
      if (response.ok) {
        const data = await response.json();
        if (Array.isArray(data) && data.length > 0) {
          return data;
        }
      }
    } catch (e) {
      // Silently fall back to placeholders
    }
    return null;
  }

  async function init(options = {}) {
    const selector = options.container || '#testimonial-carousel';
    const jsonPath = options.jsonPath || 'testimonials.json';
    const autoRotate = options.autoRotate !== false;

    containerEl = document.querySelector(selector);
    if (!containerEl) {
      console.warn(`Testimonial carousel: container "${selector}" not found.`);
      return;
    }

    containerEl.classList.add('bk-testimonial-carousel');
    injectStyles();

    // Try loading real testimonials, fall back to placeholders
    const loaded = await loadTestimonials(jsonPath);
    testimonials = loaded || PLACEHOLDER_TESTIMONIALS;

    currentIndex = 0;
    render();

    if (autoRotate && testimonials.length > 1) {
      resetInterval();
    }
  }

  function destroy() {
    if (intervalId) clearInterval(intervalId);
    if (containerEl) containerEl.innerHTML = '';
    testimonials = [];
    currentIndex = 0;
  }

  return { init, destroy, next };
})();

// Auto-init if data attribute is present
document.addEventListener('DOMContentLoaded', () => {
  const autoContainer = document.querySelector('[data-testimonials]');
  if (autoContainer) {
    const jsonPath = autoContainer.dataset.testimonials || 'testimonials.json';
    autoContainer.id = autoContainer.id || 'testimonial-carousel-auto';
    TestimonialCarousel.init({
      container: `#${autoContainer.id}`,
      jsonPath
    });
  }
});
