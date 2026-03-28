# Build a Self-Hosted Product Store for $0/Month

**By Behike** | $4.99

---

> Copyright 2026 Behike. All rights reserved.
> This guide was written with AI assistance. The code, architecture, and editorial direction are original work by the author.
> You may use and modify the code for personal or commercial projects. You may not redistribute this guide.

---

## Why Self-Host

Shopify costs $39/month. That is $468/year before you sell a single product. Squarespace costs $16/month. Wix starts at $17/month. Even "free" platforms like Gumroad take 10% of every sale.

If you are selling digital products, templates, guides, or courses, you do not need a platform. You need a webpage and a payment link.

A self-hosted store is:

- **$0/month in hosting costs.** GitHub Pages is free. Cloudflare tunnels are free. Old laptops are free.
- **No platform lock-in.** Your pages are HTML files on your computer. You own them completely.
- **No monthly subscription bleeding your margins.** The only cost is Gumroad's transaction fee (10% on the free plan, or 5% on the $10/month plan when you scale).
- **Full design control.** Every pixel is yours. No template limitations, no "upgrade to customize" walls.
- **Fast.** Static HTML loads in milliseconds. No server-side rendering, no database queries, no bloat.

The tradeoff: you write some HTML and CSS. This guide shows you exactly what to write.

---

## The Stack

Three components. Nothing else.

### 1. HTML/CSS landing pages

Each product gets its own landing page. One HTML file, self-contained, no build tools, no frameworks. The page handles the pitch: what the product is, why someone should buy it, what they get, and a button to purchase.

### 2. Gumroad for payments

Gumroad handles checkout, payment processing, file delivery, and refunds. You upload your digital product to Gumroad, get a product link, and embed that link as the "Buy Now" button on your landing page.

Why Gumroad instead of Stripe directly: Gumroad gives you file hosting, delivery emails, license keys, refund handling, and a checkout page. Building all of that yourself would take weeks. The 10% fee is worth it until you are making enough to justify a custom Stripe integration.

### 3. Any computer for hosting

Your landing pages are static HTML. You can host them from:

- A GitHub repository (free, global CDN)
- An old laptop running in a closet
- Your main computer with a Cloudflare tunnel
- Any cheap VPS ($0-5/month)

The deployment section covers all three options step by step.

---

## Building Your Product Page

Every product page follows the same structure. This is not arbitrary. It is the anatomy of a page that converts visitors into buyers.

### The structure

1. **Navigation bar** with your brand name and a CTA button
2. **Hero section** with the product name, a one-line description, the price, and a buy button
3. **Problem-Agitation-Solution section** that explains why the product exists
4. **Value stack** listing everything included
5. **FAQ section** answering objections before they become reasons not to buy
6. **Final CTA** repeating the buy button

### The CSS variables

Every page uses CSS custom properties so you can change the entire look by editing 6 values:

```css
:root {
    --black: #000000;
    --blue: #0A84FF;
    --light: #F5F5F7;
    --secondary-bg: #1D1D1F;
    --gray: #86868B;
    --font: -apple-system, 'Helvetica Neue', Helvetica, Arial, sans-serif;
}
```

- `--black` is your primary background color
- `--blue` is your accent/CTA color (buttons, highlights, badges)
- `--light` is your primary text color
- `--secondary-bg` is for cards, sections, and alternating backgrounds
- `--gray` is for secondary text, labels, and muted content
- `--font` is your font stack

To make a light-themed page, swap `--black` and `--light`:

```css
:root {
    --black: #FFFFFF;
    --light: #1D1D1F;
    --secondary-bg: #F5F5F7;
    --blue: #0066CC;
    --gray: #6E6E73;
}
```

That one change flips the entire page from dark to light mode. Every element inherits from these variables.

### The hero section

```html
<section class="hero">
    <div class="container">
        <span class="hero-badge">NEW RELEASE</span>
        <h1>The Product Name<br><span>In Accent Color</span></h1>
        <p class="hero-sub">One sentence that explains what this product does
        and who it is for.</p>
        <div class="hero-cta-group">
            <a href="https://behike.gumroad.com/l/your-product" class="hero-cta">
                Get It Now - $4.99
            </a>
        </div>
    </div>
</section>
```

The corresponding CSS:

```css
.hero {
    padding: 120px 0 80px;
    text-align: center;
}

.hero h1 {
    font-size: clamp(36px, 5vw, 56px);
    font-weight: 800;
    line-height: 1.1;
    margin-bottom: 20px;
    color: var(--light);
}

.hero h1 span {
    color: var(--blue);
}

.hero-badge {
    display: inline-block;
    padding: 6px 16px;
    border: 1px solid rgba(10, 132, 255, 0.3);
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.1em;
    color: var(--blue);
    margin-bottom: 24px;
}

.hero-cta {
    display: inline-block;
    padding: 16px 40px;
    background: var(--blue);
    color: #fff;
    text-decoration: none;
    border-radius: 12px;
    font-weight: 700;
    font-size: 18px;
    transition: transform 0.2s, box-shadow 0.2s;
}

.hero-cta:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(10, 132, 255, 0.3);
}
```

The `clamp()` function makes the headline responsive. It scales between 36px on mobile and 56px on desktop without media queries.

### The PAS section

Problem, Agitation, Solution. This is the persuasion engine of the page.

```html
<section class="pain-section">
    <div class="container">
        <h2>The Problem</h2>
        <p>Describe the pain your buyer is feeling. Be specific.
        "You're spending 2 hours a day writing social media posts by hand"
        is better than "Content creation is hard."</p>

        <h2>Why It Gets Worse</h2>
        <p>Agitate. What happens if they do not solve this?
        "While you're writing captions, your competitors are shipping.
        Every day without a system is a day you fall behind."</p>

        <h2>The Solution</h2>
        <p>Present your product as the fix. Connect it directly to the
        pain you just described. "This pipeline generates 5 posts in 5
        minutes. Same quality. A fraction of the time."</p>
    </div>
</section>
```

### The value stack

List everything included. Make it feel like a lot.

```html
<section class="features">
    <div class="container">
        <h2>What You Get</h2>
        <div class="feature-grid">
            <div class="feature-card">
                <h3>The Complete Script</h3>
                <p>400+ lines of production Python code, fully commented.</p>
            </div>
            <div class="feature-card">
                <h3>18 RSS Feed Sources</h3>
                <p>Pre-configured feeds from every major AI news outlet.</p>
            </div>
            <div class="feature-card">
                <h3>Impact Scoring System</h3>
                <p>Keyword-based scoring that surfaces what matters.</p>
            </div>
            <div class="feature-card">
                <h3>HTML Digest Generator</h3>
                <p>Dark-themed, styled digest you can read in a browser.</p>
            </div>
        </div>
    </div>
</section>
```

```css
.feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 20px;
    margin-top: 40px;
}

.feature-card {
    background: var(--secondary-bg);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 32px;
}

.feature-card h3 {
    font-size: 20px;
    font-weight: 700;
    color: var(--light);
    margin-bottom: 8px;
}

.feature-card p {
    font-size: 15px;
    color: var(--gray);
    line-height: 1.6;
}
```

### The FAQ

Handle objections proactively:

```html
<section class="faq">
    <div class="container">
        <h2>Common Questions</h2>
        <div class="faq-item">
            <h3>Do I need to know Python?</h3>
            <p>Basic familiarity helps, but the guide walks through every
            step. If you can copy-paste into a terminal, you can follow along.</p>
        </div>
        <div class="faq-item">
            <h3>What if I want a refund?</h3>
            <p>Full refund within 30 days, no questions asked.</p>
        </div>
    </div>
</section>
```

---

## The Settings Widget

This is a JavaScript widget that adds theme switching and font size controls to any landing page. Drop it in, and your visitors can customize their reading experience.

### What it does

- 8 color themes: Midnight, Snow, Ocean, Sunset, Forest, Royal, Ember, Candy
- 4 font sizes: S, M, L, XL
- Saves preferences to localStorage (persists between visits)
- Floating gear button in the bottom-right corner
- Panel slides up with theme dots and size buttons

### Adding it to your page

One script tag at the bottom of your HTML, before `</body>`:

```html
<script src="settings-widget.js"></script>
```

That is it. The widget creates its own HTML, injects its own CSS, and attaches its own event listeners. It is completely self-contained.

### How the themes work

Each theme is a JavaScript object with color values:

```javascript
const themes = {
    midnight: {
        name: 'Midnight',
        black: '#000000',
        accent: '#0A84FF',
        light: '#F5F5F7',
        secondaryBg: '#1D1D1F',
        gray: '#86868B',
        navBg: 'rgba(0,0,0,0.8)',
        cardBg: 'rgba(29,29,31,0.6)',
        border: 'rgba(245,245,247,0.08)',
    },
    snow: {
        name: 'Snow',
        black: '#FFFFFF',
        accent: '#0066CC',
        light: '#1D1D1F',
        secondaryBg: '#F5F5F7',
        gray: '#6E6E73',
        navBg: 'rgba(255,255,255,0.85)',
        cardBg: 'rgba(245,245,247,0.8)',
        border: 'rgba(0,0,0,0.08)',
    },
    // ... 6 more themes
};
```

When a visitor clicks a theme dot, the `applyTheme` function updates CSS custom properties on the document root:

```javascript
function applyTheme(key) {
    const t = themes[key];
    const r = document.documentElement.style;
    r.setProperty('--black', t.black);
    r.setProperty('--blue', t.accent);
    r.setProperty('--light', t.light);
    r.setProperty('--secondary-bg', t.secondaryBg);
    r.setProperty('--gray', t.gray);
    localStorage.setItem('behike-theme', key);
}
```

Because your page uses CSS variables for all colors, one function call repaints the entire page instantly. No page reload.

### Font size scaling

The font size system uses a scale multiplier on the root font size:

```javascript
const fontSizes = {
    small:  { label: 'S',  scale: 0.85 },
    medium: { label: 'M',  scale: 1.0 },
    large:  { label: 'L',  scale: 1.15 },
    xl:     { label: 'XL', scale: 1.3 },
};

function applyFontSize(key) {
    const s = fontSizes[key];
    document.documentElement.style.fontSize = (16 * s.scale) + 'px';
    localStorage.setItem('behike-fontsize', key);
}
```

If your page uses `rem` units for font sizes, everything scales proportionally. The base is 16px at "M", 13.6px at "S", 18.4px at "L", and 20.8px at "XL".

### Making your page compatible

For the widget to work correctly with your page, follow two rules:

1. Use CSS custom properties (`--black`, `--blue`, `--light`, `--secondary-bg`, `--gray`) for all colors
2. Use `rem` units for font sizes wherever possible

If your page already follows these conventions, the widget works immediately with zero configuration.

---

## Deploy It

Three options, all free. Pick the one that fits your setup.

### Option A: GitHub Pages (recommended for beginners)

GitHub Pages gives you free hosting with a global CDN. Your site loads fast from anywhere in the world.

**Step 1:** Create a GitHub account at github.com if you do not have one.

**Step 2:** Create a new repository. Name it whatever you want. Make it public.

**Step 3:** Upload your HTML files to the repository. You can drag and drop files directly in the GitHub web interface, or use git from the terminal:

```bash
cd ~/my-store
git init
git add .
git commit -m "Initial store pages"
git remote add origin https://github.com/yourusername/your-repo.git
git push -u origin main
```

**Step 4:** Enable GitHub Pages. Go to your repository Settings, scroll to Pages, and set the source to "Deploy from a branch", branch "main", folder "/ (root)".

**Step 5:** Your site is live at `https://yourusername.github.io/your-repo/`. Each HTML file is accessible at its own URL. If your product page is `ai-tracker-guide.html`, the URL is `https://yourusername.github.io/your-repo/ai-tracker-guide.html`.

**Step 6 (optional):** Connect a custom domain. In the Pages settings, enter your domain name. Then add a CNAME record at your DNS provider pointing to `yourusername.github.io`. GitHub handles SSL automatically.

Total time: 10 minutes. Cost: $0.

### Option B: Old laptop as a home server

If you have an old laptop, a Raspberry Pi, or any computer you are not using, it can serve your store 24/7.

**Step 1:** Install a simple web server. Python has one built in:

```bash
cd ~/my-store
python3 -m http.server 8080
```

This serves your HTML files on port 8080. Visit `http://localhost:8080` to see your store.

For something more robust, install Caddy:

```bash
# macOS
brew install caddy

# Linux
sudo apt install caddy
```

Create a `Caddyfile`:

```
:8080 {
    root * /path/to/your/store
    file_server
}
```

Run it:

```bash
caddy run
```

**Step 2:** Keep it running. On macOS, use `caffeinate` to prevent sleep:

```bash
caffeinate -s caddy run
```

On Linux, create a systemd service:

```bash
sudo tee /etc/systemd/system/store.service << 'EOF'
[Unit]
Description=Product Store
After=network.target

[Service]
ExecStart=/usr/bin/caddy run --config /path/to/Caddyfile
WorkingDirectory=/path/to/your/store
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable store
sudo systemctl start store
```

**Step 3:** Make it accessible from the internet using Cloudflare Tunnel (see Option C below).

### Option C: Cloudflare Tunnel to your home computer

Cloudflare Tunnel exposes a local web server to the internet through a secure connection. No port forwarding, no static IP required, no firewall changes.

**Step 1:** Create a free Cloudflare account at cloudflare.com.

**Step 2:** Add your domain to Cloudflare and update your nameservers (Cloudflare walks you through this).

**Step 3:** Install cloudflared:

```bash
# macOS
brew install cloudflare/cloudflare/cloudflared

# Linux
sudo apt install cloudflared
```

**Step 4:** Authenticate:

```bash
cloudflared tunnel login
```

This opens a browser window. Select your domain and authorize.

**Step 5:** Create a tunnel:

```bash
cloudflared tunnel create my-store
```

**Step 6:** Configure the tunnel. Create `~/.cloudflared/config.yml`:

```yaml
tunnel: YOUR_TUNNEL_ID
credentials-file: /path/to/.cloudflared/YOUR_TUNNEL_ID.json

ingress:
  - hostname: store.yourdomain.com
    service: http://localhost:8080
  - service: http_status:404
```

**Step 7:** Add a DNS record:

```bash
cloudflared tunnel route dns my-store store.yourdomain.com
```

**Step 8:** Start the tunnel:

```bash
cloudflared tunnel run my-store
```

Your store is now live at `https://store.yourdomain.com`. Cloudflare handles SSL, DDoS protection, and caching. Free.

To keep it running permanently, set up cloudflared as a system service:

```bash
# macOS
sudo cloudflared service install

# Linux
sudo cloudflared service install
sudo systemctl enable cloudflared
sudo systemctl start cloudflared
```

### Which option to choose

- **GitHub Pages** if you want zero maintenance and do not mind the `github.io` URL (or already have a custom domain)
- **Old laptop + Cloudflare Tunnel** if you have spare hardware and want full control
- **Cloudflare Tunnel on your main computer** if you are just testing and want to go live quickly

All three options cost $0/month. All three serve static HTML fast enough for any traffic level you will see as a solo creator.

---

**The math is simple. Shopify charges $468/year. This setup charges $0/year. If you sell 94 copies of a $4.99 product on Shopify, the first $468 goes to Shopify. With self-hosting, that $468 stays in your pocket. Every sale after that, same story.**

---

*Built by Behike. Own your store. Own your margins.*
