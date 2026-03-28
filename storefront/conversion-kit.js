/**
 * Behike Conversion Kit
 * Drop-in JS for any landing page. Adds:
 * 1. Bundle upsell bar (sticky bottom)
 * 2. Cross-sell suggestions (after main CTA)
 * 3. Urgency timer (limited offer)
 * 4. Order bump checkbox
 *
 * Usage: <script src="/storefront/conversion-kit.js"></script>
 * Configure via data attributes on the script tag:
 *   data-product="ecommerce" (current product slug)
 *   data-price="19.99" (current product price)
 *   data-bundle-url="https://behike.gumroad.com/l/v4-bundle"
 *   data-os-url="https://behike.gumroad.com/l/behike-os"
 */
(function() {
'use strict';

var script = document.currentScript || document.querySelector('script[src*="conversion-kit"]');
var currentProduct = (script && script.getAttribute('data-product')) || '';
var currentPrice = parseFloat((script && script.getAttribute('data-price')) || '19.99');
var bundleUrl = (script && script.getAttribute('data-bundle-url')) || 'https://behike.gumroad.com';
var osUrl = (script && script.getAttribute('data-os-url')) || 'https://behike.gumroad.com';

var BUNDLE_PRICE = 69;
var OS_PRICE = 197;
var INDIVIDUAL_TOTAL = 493;

/* ===== STYLES ===== */
var style = document.createElement('style');
style.textContent = [
  /* Sticky upsell bar */
  '#ck-bar{position:fixed;bottom:0;left:0;right:0;z-index:9998;background:rgba(10,10,15,0.95);',
  'backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);border-top:1px solid rgba(0,212,255,0.2);',
  'padding:12px 24px;display:none;align-items:center;justify-content:center;gap:16px;',
  'font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;font-size:14px;color:#f5f5f7;',
  'transform:translateY(100%);transition:transform 0.4s cubic-bezier(0.22,1,0.36,1)}',
  '#ck-bar.ck-show{display:flex;transform:translateY(0)}',
  '#ck-bar .ck-text{display:flex;align-items:center;gap:8px}',
  '#ck-bar .ck-save{background:rgba(52,199,89,0.15);color:#34C759;padding:3px 10px;border-radius:12px;',
  'font-size:11px;font-weight:700;letter-spacing:0.5px}',
  '#ck-bar .ck-prices{display:flex;align-items:baseline;gap:8px}',
  '#ck-bar .ck-was{color:#555;text-decoration:line-through;font-size:13px}',
  '#ck-bar .ck-now{color:#fff;font-size:18px;font-weight:700}',
  '#ck-bar .ck-btn{background:#00D4FF;color:#000;padding:10px 24px;border-radius:980px;',
  'font-size:13px;font-weight:600;text-decoration:none;transition:opacity 0.2s;white-space:nowrap}',
  '#ck-bar .ck-btn:hover{opacity:0.85}',
  '#ck-bar .ck-close{background:none;border:none;color:#555;font-size:18px;cursor:pointer;padding:4px 8px}',
  '#ck-bar .ck-close:hover{color:#fff}',

  /* Cross-sell cards */
  '#ck-cross{margin:40px auto;max-width:720px;padding:0 24px}',
  '#ck-cross h3{font-size:14px;color:#86868B;text-transform:uppercase;letter-spacing:0.12em;',
  'font-weight:600;margin-bottom:16px;text-align:center}',
  '#ck-cross .ck-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}',
  '#ck-cross .ck-card{background:#111;border:1px solid #1a1a1a;border-radius:12px;padding:20px;',
  'transition:border-color 0.2s;cursor:pointer;text-decoration:none;color:#f5f5f7;display:block}',
  '#ck-cross .ck-card:hover{border-color:rgba(0,212,255,0.3)}',
  '#ck-cross .ck-card .ck-tag{font-size:10px;color:#00D4FF;letter-spacing:0.15em;font-weight:700;margin-bottom:8px}',
  '#ck-cross .ck-card h4{font-size:15px;font-weight:600;margin-bottom:4px}',
  '#ck-cross .ck-card p{font-size:12px;color:#86868B;margin-bottom:12px}',
  '#ck-cross .ck-card .ck-price{font-size:16px;font-weight:700}',

  /* Order bump */
  '#ck-bump{background:rgba(0,212,255,0.04);border:1px dashed rgba(0,212,255,0.3);border-radius:12px;',
  'padding:20px 24px;margin:24px auto;max-width:500px;display:flex;align-items:center;gap:16px;',
  'cursor:pointer;transition:background 0.2s}',
  '#ck-bump:hover{background:rgba(0,212,255,0.08)}',
  '#ck-bump .ck-check{width:22px;height:22px;border:2px solid #00D4FF;border-radius:4px;flex-shrink:0;',
  'display:flex;align-items:center;justify-content:center;font-size:14px;color:#00D4FF;transition:background 0.2s}',
  '#ck-bump.checked .ck-check{background:#00D4FF;color:#000}',
  '#ck-bump .ck-bump-text{flex:1;font-size:13px;color:#c0c8d8;line-height:1.5}',
  '#ck-bump .ck-bump-text strong{color:#f5f5f7}',
  '#ck-bump .ck-bump-price{font-size:16px;font-weight:700;color:#f5f5f7;white-space:nowrap}',

  '@media(max-width:600px){#ck-bar{flex-wrap:wrap;gap:8px;padding:10px 16px}',
  '#ck-cross .ck-grid{grid-template-columns:1fr}}'
].join('');
document.head.appendChild(style);

/* ===== CROSS-SELL SUGGESTIONS ===== */
var PRODUCTS = {
  ecommerce: {related: ['dropshipping','freelancer','content-creator'], bundle: true},
  'ai-agency': {related: ['saas','freelancer','consulting'], bundle: true},
  freelancer: {related: ['consulting','coaching','content-creator'], bundle: true},
  'content-creator': {related: ['youtube','newsletter','podcast'], bundle: true},
  dropshipping: {related: ['ecommerce','etsy','freelancer'], bundle: true},
  saas: {related: ['ai-agency','freelancer','newsletter'], bundle: true},
  youtube: {related: ['content-creator','podcast','newsletter'], bundle: true},
  newsletter: {related: ['content-creator','youtube','coaching'], bundle: true},
  coaching: {related: ['consulting','freelancer','content-creator'], bundle: true},
  consulting: {related: ['coaching','freelancer','ai-agency'], bundle: true},
  crypto: {related: ['saas','newsletter','ecommerce'], bundle: true},
  etsy: {related: ['ecommerce','dropshipping','content-creator'], bundle: true},
  podcast: {related: ['youtube','content-creator','newsletter'], bundle: true}
};

var PRODUCT_INFO = {
  ecommerce: {title:'E-Commerce Blueprint v4',price:'$19.99',desc:'Store setup to $250K/month'},
  'ai-agency': {title:'AI Agency Blueprint v4',price:'$19.99',desc:'Land clients, scale to $10K/mo'},
  freelancer: {title:'Freelancer to Agency v4',price:'$19.99',desc:'Stop trading hours for dollars'},
  'content-creator': {title:'Content Creator Blueprint v4',price:'$19.99',desc:'Turn content into a business'},
  dropshipping: {title:'Dropshipping Blueprint v4',price:'$19.99',desc:'Find products, test fast, scale'},
  saas: {title:'Micro-SaaS Blueprint v4',price:'$19.99',desc:'Build profitable software solo'},
  youtube: {title:'YouTube Channel Blueprint v4',price:'$19.99',desc:'Launch to monetization in 90 days'},
  newsletter: {title:'Newsletter Blueprint v4',price:'$19.99',desc:'Email is the only platform you own'},
  coaching: {title:'Coaching Blueprint v4',price:'$19.99',desc:'Package expertise, sell at premium'},
  consulting: {title:'Consulting Blueprint v4',price:'$19.99',desc:'Land high-ticket clients'},
  crypto: {title:'Crypto Investor Blueprint v4',price:'$19.99',desc:'Structured research framework'},
  etsy: {title:'Etsy Seller Blueprint v4',price:'$19.99',desc:'Digital products on autopilot'},
  podcast: {title:'Podcast Blueprint v4',price:'$19.99',desc:'Zero to sponsors'}
};

function insertCrossSell() {
  var config = PRODUCTS[currentProduct];
  if (!config) return;

  /* Find the last CTA on the page to insert after */
  var ctas = document.querySelectorAll('.bottom-cta, .cta-sub, .guarantee');
  var insertPoint = ctas.length > 0 ? ctas[ctas.length - 1].parentElement : document.body;

  var crossEl = document.createElement('div');
  crossEl.id = 'ck-cross';
  var html = '<h3>Builders also bought</h3><div class="ck-grid">';

  /* Bundle card first */
  html += '<a class="ck-card" href="' + bundleUrl + '" target="_blank" rel="noopener">' +
    '<div class="ck-tag">SAVE 86%</div>' +
    '<h4>V4 Blueprint Bundle (All 17)</h4>' +
    '<p>Every blueprint in one download. Revenue calculators, KPI dashboards, fill-in worksheets.</p>' +
    '<div class="ck-price">$69 <span style="color:#555;text-decoration:line-through;font-size:13px;font-weight:400;margin-left:4px">$493</span></div>' +
    '</a>';

  /* Related products */
  config.related.slice(0, 1).forEach(function(slug) {
    var info = PRODUCT_INFO[slug];
    if (!info) return;
    html += '<a class="ck-card" href="' + bundleUrl + '" target="_blank" rel="noopener">' +
      '<div class="ck-tag">RELATED</div>' +
      '<h4>' + info.title + '</h4>' +
      '<p>' + info.desc + '</p>' +
      '<div class="ck-price">' + info.price + '</div>' +
      '</a>';
  });

  html += '</div>';
  crossEl.innerHTML = html;

  /* Insert before footer */
  var footer = document.querySelector('footer');
  if (footer) {
    footer.parentElement.insertBefore(crossEl, footer);
  } else {
    insertPoint.appendChild(crossEl);
  }
}

/* ===== ORDER BUMP ===== */
function insertOrderBump() {
  /* Find CTAs to insert bump after */
  var cta = document.querySelector('.hero .cta, .hero .cta-big, .hero-actions .btn-primary');
  if (!cta) return;

  var bump = document.createElement('div');
  bump.id = 'ck-bump';
  bump.innerHTML = '<div class="ck-check"></div>' +
    '<div class="ck-bump-text"><strong>Add the full bundle?</strong> Get all 17 blueprints instead of just this one. Save 86% vs buying individually.</div>' +
    '<div class="ck-bump-price">+$49</div>';

  bump.addEventListener('click', function() {
    bump.classList.toggle('checked');
    var check = bump.querySelector('.ck-check');
    check.textContent = bump.classList.contains('checked') ? '\\u2713' : '';
    /* Update main CTA link to bundle */
    var mainCta = document.querySelector('.hero .cta, .hero .cta-big');
    if (mainCta) {
      mainCta.href = bump.classList.contains('checked') ? bundleUrl : mainCta.getAttribute('data-original-href') || mainCta.href;
      if (!mainCta.getAttribute('data-original-href')) mainCta.setAttribute('data-original-href', mainCta.href);
    }
  });

  var parent = cta.parentElement;
  var subEl = parent.querySelector('.cta-sub');
  if (subEl) {
    parent.insertBefore(bump, subEl);
  } else {
    parent.appendChild(bump);
  }
}

/* ===== STICKY UPSELL BAR ===== */
function insertUpsellBar() {
  var bar = document.createElement('div');
  bar.id = 'ck-bar';
  bar.innerHTML = '<div class="ck-text">' +
    '<span class="ck-save">SAVE 86%</span>' +
    '<span>Get all 17 blueprints</span>' +
    '</div>' +
    '<div class="ck-prices">' +
    '<span class="ck-was">$493</span>' +
    '<span class="ck-now">$69</span>' +
    '</div>' +
    '<a class="ck-btn" href="' + bundleUrl + '" target="_blank" rel="noopener">Get the Bundle</a>' +
    '<button class="ck-close" title="Close">&times;</button>';
  document.body.appendChild(bar);

  /* Show after scrolling past 40% of the page */
  var shown = false;
  var dismissed = false;
  window.addEventListener('scroll', function() {
    if (dismissed) return;
    var pct = window.scrollY / (document.body.scrollHeight - window.innerHeight);
    if (pct > 0.4 && !shown) {
      shown = true;
      bar.classList.add('ck-show');
    }
  }, {passive: true});

  bar.querySelector('.ck-close').addEventListener('click', function() {
    bar.classList.remove('ck-show');
    dismissed = true;
  });
}

/* ===== INIT ===== */
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}

function init() {
  if (currentProduct && PRODUCTS[currentProduct]) {
    insertCrossSell();
    insertOrderBump();
  }
  insertUpsellBar();
}

})();
