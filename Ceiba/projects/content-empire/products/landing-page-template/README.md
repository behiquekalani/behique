# Product Landing Page Template

A clean, dark-mode landing page template you can customize for any digital product, course, or service. Built with pure HTML and CSS. No frameworks, no dependencies, no build tools.

Open the file. Change the text. Upload it. Done.

---

## How to Use This Template

### Step 1: Open index.html in a text editor

Any text editor works. VS Code, Sublime Text, Notepad, TextEdit. Even Notepad on Windows.

### Step 2: Search for [BRACKETS] and replace with your content

Every piece of placeholder content is wrapped in square brackets like `[Your Product Name]`. Use your editor's Find & Replace feature (Ctrl+H or Cmd+H) to locate each one and swap in your real content.

Here is the full list of placeholders:

| Placeholder | What to put there |
|---|---|
| `[Your Brand]` | Your brand or company name |
| `[Your Product Name]` | The name of your product |
| `[Your tagline here]` | A short, punchy subtitle |
| `[Price]` | Your price (e.g. $29, $49, Free) |
| `[PAYMENT_LINK]` | Your Gumroad, Stripe, or PayPal checkout URL |
| `[Describe your customer's problem]` | The main pain point your product solves |
| `[Explain why this problem matters]` | Why the reader should care |
| `[How your product solves it]` | Your solution in one sentence |
| `[Feature Title 1-6]` | Name of each feature |
| `[Feature description 1-6]` | One sentence explaining each feature |
| `[Pricing headline]` | e.g. "Simple pricing. No subscriptions." |
| `[Pricing subtitle]` | e.g. "One payment. Lifetime access." |
| `[What's included item 1-5]` | Each line item the buyer gets |
| `[FAQ Question 1-5]` | Common questions about your product |
| `[FAQ Answer 1-5]` | Answers to those questions |
| `[your-email@example.com]` | Your contact email |
| `[Your Brand or Name]` | Footer copyright name |

### Step 3: Customize colors by editing the CSS variables

At the top of the HTML file, inside the `<style>` tag, you will find a `:root` block with CSS variables. These control the entire color scheme.

```css
:root {
    --black: #000000;        /* Background color */
    --blue: #0A84FF;         /* Accent color (buttons, links, highlights) */
    --light: #F5F5F7;        /* Main text color */
    --secondary-bg: #1D1D1F; /* Card and section backgrounds */
    --gray: #86868B;         /* Muted text (subtitles, descriptions) */
}
```

**To change the accent color**, replace `#0A84FF` with any hex color. Examples:
- Green: `#34C759`
- Purple: `#AF52DE`
- Red: `#FF3B30`
- Orange: `#FF9F0A`
- Teal: `#00C7BE`

**To make it light mode**, swap the background and text colors:
```css
:root {
    --black: #FFFFFF;
    --blue: #0066CC;
    --light: #1D1D1F;
    --secondary-bg: #F5F5F7;
    --gray: #6E6E73;
}
```

### Step 4: Upload to any web host

This is a static HTML file. It works anywhere.

- **Netlify**: Drag and drop the folder at netlify.com/drop
- **Vercel**: Import the folder from the Vercel dashboard
- **GitHub Pages**: Push to a repo and enable Pages in settings
- **Your own server**: Upload index.html and settings-widget.js to any web directory

Make sure `settings-widget.js` is in the same folder as `index.html`.

---

## How to Add Your Own Sections

Copy any existing `<section>` block in the HTML and paste it where you want the new section. Each section follows this pattern:

```html
<section class="your-section reveal">
    <h2>Your Section Title</h2>
    <p>Your content here.</p>
</section>
```

Add the `reveal` class for scroll-triggered fade-in animation.

---

## How to Connect a Payment Link

Replace `[PAYMENT_LINK]` with your checkout URL. The template has three buy buttons (nav, hero, pricing card) that all use this link.

**Gumroad**: Go to your product page, copy the URL (e.g. `https://yourusername.gumroad.com/l/product`)

**Stripe Payment Links**: Create a payment link in your Stripe dashboard, copy the URL

**PayPal**: Create a PayPal.me link or a hosted button, use that URL

---

## Included Files

| File | Purpose |
|---|---|
| `index.html` | The landing page template |
| `settings-widget.js` | Theme switcher with 8 color themes and 4 font sizes |
| `README.md` | This setup guide |
| `LICENSE` | MIT License, use it however you want |

---

## FAQ

**Do I need to know how to code?**
No. You only need to open the file in a text editor, find the bracketed placeholders, and type your own content.

**Can I use this for multiple products?**
Yes. The MIT license lets you use, modify, and reuse this template for as many products as you want.

**What about mobile?**
The template is fully responsive out of the box. It looks good on phones, tablets, and desktops.

**Can I remove the settings widget?**
Yes. Delete the `<script src="settings-widget.js"></script>` line at the bottom of the HTML file, and remove the settings-widget.js file.

**Can I add images?**
Yes. Add `<img>` tags anywhere in the HTML. Place your image files in the same folder and reference them like `<img src="your-image.jpg" alt="description">`.

---

Built by Behike.
