(function() {
  'use strict';

  var COOKIE_NAME = 'sp_dismissed';
  var DISMISS_LIMIT = 3;
  var COOKIE_HOURS = 24;
  var DISPLAY_DURATION = 5000;
  var MIN_INTERVAL = 15000;
  var MAX_INTERVAL = 30000;

  var NAMES = [
    'Carlos', 'Maria', 'Jose', 'Ana', 'Luis', 'Sofia', 'Diego', 'Valentina',
    'Miguel', 'Isabella', 'James', 'Sarah', 'Brandon', 'Ashley', 'Kevin',
    'Nicole', 'Omar', 'Daniela', 'Pedro', 'Camila', 'Marcus', 'Priya',
    'Hiroshi', 'Fatima', 'Andres', 'Rachel', 'Mateo', 'Leila', 'Ryan',
    'Carmen', 'David', 'Lucia', 'Alex', 'Maya', 'Gabriel', 'Nina',
    'Sebastian', 'Jade', 'Emilio', 'Zara'
  ];

  var CITIES = [
    'San Juan, PR', 'Ponce, PR', 'Mayaguez, PR', 'Carolina, PR',
    'Miami, FL', 'New York, NY', 'Houston, TX', 'Los Angeles, CA',
    'Chicago, IL', 'Austin, TX', 'Atlanta, GA', 'Denver, CO',
    'Mexico City, MX', 'Bogota, CO', 'Medellin, CO', 'Madrid, ES',
    'Barcelona, ES', 'Sao Paulo, BR', 'Toronto, CA', 'London, UK',
    'Berlin, DE', 'Buenos Aires, AR', 'Lima, PE', 'Santiago, CL',
    'Portland, OR', 'Nashville, TN', 'Seattle, WA', 'Phoenix, AZ',
    'San Diego, CA', 'Orlando, FL'
  ];

  var PRODUCTS = [
    'Behike Operating System', 'E-Commerce Blueprint',
    'Freelancer to Agency Blueprint', 'Content Creator Blueprint',
    'AI Agency Blueprint', 'Dropshipping Blueprint',
    'Micro-SaaS Blueprint', 'YouTube Channel Blueprint',
    'Newsletter Blueprint', 'Coaching Blueprint',
    'Crypto Investor Blueprint', 'Etsy Digital Products Blueprint',
    'Consulting Blueprint', 'Podcast Blueprint',
    'Starter Pack Bundle',
    'AI Tools Mastery Guide', 'The AI Copywriting Playbook',
    'Behike Operating System', 'The Recurring Revenue Blueprint'
  ];

  function getCookie(name) {
    var match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
    return match ? match[2] : null;
  }

  function setCookie(name, value, hours) {
    var d = new Date();
    d.setTime(d.getTime() + hours * 3600000);
    document.cookie = name + '=' + value + ';expires=' + d.toUTCString() + ';path=/';
  }

  function pick(arr) {
    return arr[Math.floor(Math.random() * arr.length)];
  }

  function randomMinutes() {
    return Math.floor(Math.random() * 12) + 1;
  }

  function randomInterval() {
    return MIN_INTERVAL + Math.random() * (MAX_INTERVAL - MIN_INTERVAL);
  }

  // Check dismiss cookie
  var dismissCount = parseInt(getCookie(COOKIE_NAME) || '0', 10);
  if (dismissCount >= DISMISS_LIMIT) return;

  // Inject styles
  var style = document.createElement('style');
  style.textContent = [
    '#sp-toast{position:fixed;bottom:20px;left:20px;z-index:99999;max-width:340px;',
    'background:rgba(15,15,20,0.92);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);',
    'border:1px solid rgba(0,212,255,0.3);border-left:3px solid #00D4FF;',
    'border-radius:10px;padding:14px 16px;color:#f0f0f0;font-family:-apple-system,BlinkMacSystemFont,',
    '"Segoe UI",Roboto,sans-serif;font-size:13px;line-height:1.4;cursor:pointer;',
    'transform:translateX(-120%);transition:transform 0.4s cubic-bezier(0.22,1,0.36,1);',
    'box-shadow:0 8px 32px rgba(0,0,0,0.4)}',
    '#sp-toast.sp-show{transform:translateX(0)}',
    '#sp-toast .sp-row{display:flex;align-items:center;gap:12px}',
    '#sp-toast .sp-icon{width:38px;height:38px;border-radius:8px;background:linear-gradient(135deg,#00D4FF,#0099bb);',
    'display:flex;align-items:center;justify-content:center;flex-shrink:0;font-size:18px}',
    '#sp-toast .sp-text{flex:1}',
    '#sp-toast .sp-name{font-weight:600;color:#00D4FF}',
    '#sp-toast .sp-product{font-weight:600;color:#fff}',
    '#sp-toast .sp-time{color:#999;font-size:11px;margin-top:2px}',
    '#sp-toast .sp-badge{display:inline-flex;align-items:center;gap:4px;margin-top:6px;',
    'font-size:10px;color:#6fcf97;text-transform:uppercase;letter-spacing:0.5px;font-weight:600}',
    '#sp-toast .sp-badge::before{content:"";width:6px;height:6px;background:#6fcf97;border-radius:50%}',
    '@media(max-width:480px){#sp-toast{left:10px;right:10px;bottom:10px;max-width:none}}'
  ].join('');
  document.head.appendChild(style);

  // Create toast element
  var toast = document.createElement('div');
  toast.id = 'sp-toast';
  toast.innerHTML = [
    '<div class="sp-row">',
    '<div class="sp-icon">&#128230;</div>',
    '<div class="sp-text">',
    '<div><span class="sp-name"></span> from <span class="sp-city"></span></div>',
    '<div>just bought <span class="sp-product"></span></div>',
    '<div class="sp-time"></div>',
    '<div class="sp-badge">Verified Purchase</div>',
    '</div></div>'
  ].join('');
  document.body.appendChild(toast);

  var hideTimer = null;
  var cycleTimer = null;

  function dismiss() {
    toast.classList.remove('sp-show');
    clearTimeout(hideTimer);
    dismissCount++;
    setCookie(COOKIE_NAME, dismissCount, COOKIE_HOURS);
    if (dismissCount >= DISMISS_LIMIT) {
      clearTimeout(cycleTimer);
    }
  }

  toast.addEventListener('click', dismiss);

  function showNotification(sale) {
    toast.querySelector('.sp-name').textContent = sale.name;
    toast.querySelector('.sp-city').textContent = sale.city;
    toast.querySelector('.sp-product').textContent = sale.product;
    toast.querySelector('.sp-time').textContent = sale.minutes + ' minute' + (sale.minutes === 1 ? '' : 's') + ' ago';
    toast.classList.add('sp-show');
    hideTimer = setTimeout(function() {
      toast.classList.remove('sp-show');
    }, DISPLAY_DURATION);
  }

  function generateFakeSale() {
    return { name: pick(NAMES), city: pick(CITIES), product: pick(PRODUCTS), minutes: randomMinutes() };
  }

  function loadSales(callback) {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/bios/analytics/data/sales.json', true);
    xhr.onload = function() {
      try {
        var data = JSON.parse(xhr.responseText);
        callback(Array.isArray(data) && data.length > 0 ? data : null);
      } catch(e) { callback(null); }
    };
    xhr.onerror = function() { callback(null); };
    xhr.send();
  }

  function cycle(realSales) {
    if (dismissCount >= DISMISS_LIMIT) return;
    var sale;
    if (realSales && realSales.length) {
      var s = pick(realSales);
      sale = {
        name: s.name || pick(NAMES),
        city: s.city || pick(CITIES),
        product: s.product || pick(PRODUCTS),
        minutes: randomMinutes()
      };
    } else {
      sale = generateFakeSale();
    }
    showNotification(sale);
    cycleTimer = setTimeout(function() { cycle(realSales); }, randomInterval());
  }

  // Start after short delay
  loadSales(function(realSales) {
    cycleTimer = setTimeout(function() { cycle(realSales); }, 3000);
  });
})();
