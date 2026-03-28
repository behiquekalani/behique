# ONI-PUNI STORE REDESIGN SPECIFICATION

**Client:** Randy (Oni-Puni)
**Store:** onipuni.com (Shopify)
**Theme:** Shrine (Shopify Theme Store)
**Date:** March 23, 2026
**Prepared by:** Behike AI Services
**Document type:** Technical specification for store rebuild

---

## TABLE OF CONTENTS

1. Homepage Redesign
2. Product Page Upgrades
3. Bundle Strategy
4. Upsell Flow
5. Funnel Strategy
6. Event Integration
7. Vendor Marketplace
8. SEO Quick Wins
9. Technical Specs for Shrine Theme
10. Implementation Checklist

---

## 1. HOMEPAGE REDESIGN

The homepage needs to do three things: establish trust, showcase products, and capture emails. Every section below serves one of those goals.

### 1.1 Announcement Bar

**Content:** "Free sticker with every order over $25 -- Shop Now"

**Purpose:** Drive average order value above the $25 threshold. Current AOV is estimated at $18. A free sticker costs Randy $0.30-0.50 in materials. If this bumps AOV to $25+, the math works immediately.

**Shrine configuration:**
- Background color: #FFB6C1 (brand pink)
- Text color: #333333 (charcoal)
- Link: points to /collections/all
- Enable rotating messages if Shrine supports it. Second message: "We ship from Milwaukee -- Fast US delivery"

### 1.2 Hero Section (Rotating Banner)

Three slides, auto-rotating every 5 seconds with manual navigation arrows.

**Slide 1 -- New Arrivals:**
- Headline: "Just Dropped"
- Subtext: "Fresh kawaii finds, updated weekly"
- CTA button: "Shop New Arrivals"
- Link: /collections/new-arrivals
- Image: High-quality flat lay of 5-6 newest products on pastel background

**Slide 2 -- Blind Boxes:**
- Headline: "What Will You Get?"
- Subtext: "Blind boxes from Sonny Angel, POP MART, and more"
- CTA button: "Shop Blind Boxes"
- Link: /collections/blind-boxes
- Image: Stack of unopened blind boxes with one revealed figure in front

**Slide 3 -- Bundles:**
- Headline: "More Kawaii, Better Price"
- Subtext: "Curated bundles that save you up to $10"
- CTA button: "Shop Bundles"
- Link: /collections/bundles
- Image: Styled bundle layout showing a plush, charms, and sticker pack together

**Image specs for all slides:**
- Desktop: 1920x800px minimum
- Mobile: 750x900px (separate mobile-optimized images)
- File format: WebP with JPEG fallback
- File size: Under 200KB per image after compression

### 1.3 Featured Collections Grid

Display 5 collections in a visually balanced grid below the hero. Two rows: 3 on top, 2 on bottom (or a 2-3 split depending on Shrine's grid options).

| Collection | Image Style | Badge/Label |
|-----------|------------|-------------|
| Blind Boxes | Stacked boxes with mystery vibe | "Popular" |
| Plushies | Arranged plush characters, soft lighting | None |
| Pokemon TCG | Binders and accessories flat lay | None |
| Bundles | Curated set styled as a gift | "Save $$$" |
| Sale | Red/pink themed clearance shot | "Limited" |

Each collection tile links to its respective collection page. Use Shrine's collection grid section with image overlay text.

### 1.4 "Unbox With Us" Section

**Purpose:** Drive TikTok follows and build social proof through video content.

**Layout:** Full-width section with embedded TikTok feed or 3-4 video thumbnails linking to TikTok.

**Content:**
- Section heading: "Unbox With Us"
- Subheading: "Follow along on TikTok for blind box reveals, new arrivals, and event updates"
- CTA button: "Follow @onipuni on TikTok" (links to TikTok profile)
- If Shrine does not support TikTok embed natively, use a third-party app like Instafeed (which supports TikTok) or manually curate 3-4 thumbnail images linking to specific TikTok videos.

**Fallback option if TikTok account is not yet active:** Replace with a "Behind the Scenes" photo gallery showing event booth setup, packing orders, and product sourcing. This section converts to TikTok content once the account is live.

### 1.5 Newsletter Signup

**Position:** Below the collections grid, above the footer. Full-width section with contrasting background.

**Layout:**
- Background color: #FFF8DC (cream)
- Heading: "Join the Kawaii Club"
- Subtext: "Get a free kawaii phone wallpaper, plus early access to new drops, event schedules, and exclusive deals."
- Input field: Email address
- Button: "Send Me the Wallpaper"
- Button color: #FFB6C1 (brand pink)

**Lead magnet:** Free digital kawaii phone wallpaper (PNG, sized for iPhone and Android). Randy or a freelance artist creates 3-4 wallpaper designs. Delivered via Klaviyo welcome email immediately after signup.

**Technical integration:**
- Form connects to Klaviyo list
- Auto-tag new subscribers as "website-signup"
- Trigger welcome email sequence (see Store Audit document, Section 3)

### 1.6 Testimonials Section

**Current problem:** Only 2 reviews exist across the entire store. This section will feel empty.

**Short-term solution:** Pull the 2 existing reviews and supplement with event customer quotes (Randy collects these at flea markets/cons via a simple "How was your experience?" card).

**Long-term solution:** Once Judge.me automated review requests are active (see Store Audit, Section 4), this section auto-populates with recent 5-star reviews.

**Shrine configuration:**
- Use the testimonial/review section
- Show 3 reviews in a horizontal carousel
- Include star rating, customer first name, and review text
- If photo reviews exist, display the photo

### 1.7 Homepage Section Order (Top to Bottom)

1. Announcement bar (persistent, all pages)
2. Navigation menu
3. Hero rotating banner
4. Featured collections grid (5 collections)
5. "Unbox With Us" TikTok/social section
6. Testimonials carousel
7. Newsletter signup
8. Footer

---

## 2. PRODUCT PAGE UPGRADES

Every product page needs to convert browsers into buyers. The current pages are functional but lack the psychological triggers that drive purchases.

### 2.1 "Complete the Look" Cross-Sell Widget

**Purpose:** Increase items per order by suggesting complementary products.

**Logic:**
- If customer views a plush, suggest: matching charm + sticker pack
- If customer views a blind box, suggest: another blind box series + display shelf/stand
- If customer views Pokemon TCG accessories, suggest: complementary accessories (binder + sleeves + toploaders)
- If customer views stickers, suggest: sticker pack bundle + washi tape

**Implementation:**
- Use Shopify's native "Related Products" section in Shrine, or
- Install a cross-sell app (Frequently Bought Together by Code Black Belt, or Also Bought by Innonic)
- Manually curate cross-sell pairings for the top 10 products. Let the algorithm handle the rest.

**Placement:** Below the main product description, above reviews.

### 2.2 Bundle Builder

**Headline on product page:** "Build Your Own Bundle"

**Primary offer:** "Pick 3 Charms for $25" (individual price: $11 each = $33 value, customer saves $8)

**How it works:**
1. Customer selects the "Pick 3 Charms" product
2. Page displays all available charms as selectable options
3. Customer picks 3
4. Price auto-calculates to $25
5. Add to cart as a single line item

**Implementation options:**
- Shopify app: Bundler or Wide Bundles (both support mix-and-match)
- If app cost is a concern, create a manual product listing with variant selectors for each charm choice

**Additional bundle offers to create as standalone product listings:**
- "Pick 2 Sticker Packs for $5" (normally $3 each)
- "Any Plush + Charm for $30" (saves $3-5 depending on plush)

### 2.3 Gift Wrapping Option

**Product page addition:** Checkbox or dropdown on every product page.

**Copy:** "Add gift wrapping -- $3.99"
**Description:** "We'll wrap your item in kawaii paper with a ribbon and handwritten note. Perfect for birthdays, holidays, or just because."

**Implementation:**
- Use Shopify's native gift wrap product (create a hidden product at $3.99, add via cart attribute)
- Or use an app like Gift Wrap Plus or Wrapped (adds checkbox to product pages)

**Margin:** Gift wrap materials cost approximately $0.50-1.00. At $3.99, this is a 75-87% margin add-on. Randy already handles shipping, so wrapping adds minimal labor.

### 2.4 "Frequently Bought Together" Section

**Display:** 2-3 products shown together with a combined "Add All to Cart" button and a visible savings amount.

**Example pairings:**
- Rilakkuma Plush ($22) + Rilakkuma Charm ($11) + Kawaii Sticker Pack ($3) = "$36 -- Add All for $32 (Save $4)"
- Pokemon Binder ($25) + Card Sleeves ($9) + Toploader Pack ($5) = "$39 -- Add All for $30 (Save $9)"

**Implementation:** Frequently Bought Together app (Code Black Belt). Configure top 10 product pairings manually, allow algorithm to generate the rest based on co-purchase data.

### 2.5 Urgency Indicators

**"Only X left in stock" display:**
- Shrine theme setting: Enable inventory quantity display
- Show exact count when inventory is 5 or fewer units
- Text: "Only 3 left in stock -- order soon"
- Color: Use a warm orange or soft red that fits the kawaii aesthetic (not aggressive red)

**This is legitimate urgency.** Randy has real limited inventory on many items, especially blind boxes and event exclusives. This is not manufactured scarcity.

**Additional urgency elements:**
- "Selling fast" badge on products that moved 3+ units in the past week
- "Event exclusive -- limited restock" label on items sourced from specific cons

### 2.6 Product Description Overhaul

Every product description follows this template:

**Section 1 -- Hook (1-2 sentences):**
Write desire-first. Not what it is, but why the customer wants it.

**Section 2 -- Details (bullet points):**
- Dimensions/size
- Material
- Character/series
- Condition (new, sealed, etc.)
- Any special features

**Section 3 -- Use case (1 sentence):**
Who is this for and when would they use it.

**Section 4 -- Shipping note (1 sentence):**
"Ships from Milwaukee, WI. Orders placed before 2 PM CT ship same day."

**Example rewrite:**

Current: "Rilakkuma Plush"

Rewritten:
"This Rilakkuma just wants to hang out on your desk and make your day better. Officially licensed San-X plush, soft to the touch and perfectly sized for display or cuddling.

- Size: 8 inches tall
- Material: Ultra-soft polyester
- Character: Rilakkuma (San-X)
- Condition: New with tags

Great for Rilakkuma collectors, desk decor, or as a kawaii gift that always lands.

Ships from Milwaukee, WI. Orders placed before 2 PM CT ship same day."

**Keyword optimization:** Every product title and description includes relevant search terms. "Rilakkuma Plush" becomes "Rilakkuma Plush Toy -- San-X Kawaii Stuffed Animal, 8 Inch." This helps Google and Shopify search.

---

## 3. BUNDLE STRATEGY

Bundles solve two problems: they increase AOV and they move slower inventory. Every bundle should feel like a deal, not a clearance dump.

### 3.1 Starter Bundle

**Name:** "Kawaii Starter Pack"
**Contents:** 1 plush + 2 charms + 1 sticker pack
**Price:** $35 (individual value: $45+)
**Savings displayed:** "Save $10"
**Target customer:** First-time buyers, gift shoppers
**Product page copy:** "New to kawaii? Start here. One plush, two charms, and a sticker pack, all picked to match. Everything you need to start your collection."

### 3.2 Collector Bundle

**Name:** "Blind Box Triple"
**Contents:** 3 blind boxes (same series or mixed, customer chooses)
**Price:** $40 (individual value: $45-48)
**Savings displayed:** "Save up to $8"
**Target customer:** Blind box collectors, TikTok-inspired buyers
**Product page copy:** "Triple your chances. Pick 3 blind boxes from any series and save. Will you get the secret figure? Only one way to find out."

### 3.3 Pokemon Bundle

**Name:** "Pokemon TCG Essentials"
**Contents:** 1 binder + 1 pack of sleeves + 1 pack of toploaders
**Price:** $30 (individual value: $35-39)
**Savings displayed:** "Save up to $9"
**Target customer:** Pokemon TCG players, tournament goers
**Product page copy:** "Everything you need to protect your pulls. Binder, sleeves, and toploaders in one set. Tournament ready."

### 3.4 Mystery Box

**Name:** "Oni-Puni Mystery Box"
**Contents:** Randy hand-picks items worth $50+ retail value. Mix of plush, charms, stickers, blind box, and surprise items.
**Price:** $35
**Savings displayed:** "$50+ value for $35"
**Target customer:** Adventurous buyers, content creators (great for unboxing content)
**Product page copy:** "Let us surprise you. Every Mystery Box is hand-picked by Randy with over $50 worth of kawaii goodies. No two boxes are the same."

**Operational note:** Randy assembles mystery boxes in batches of 5-10. Photograph one example box (contents spread out) for the product listing. Mention that exact contents vary.

### 3.5 Gift Box

**Name:** "Kawaii Gift Box"
**Contents:** Customer selects any items + gift wrapping + handwritten note included
**Price:** Add $5.99 to cart total (or create as a standalone add-on product)
**Target customer:** Gift buyers (birthdays, holidays, "just because")
**Product page copy:** "Make it special. We'll wrap your order in kawaii gift paper, add a ribbon, and include a handwritten note with your message. Just tell us what to write at checkout."

**Implementation:** Create as an add-to-cart product ($5.99) with a text field for the custom note message. Randy writes the note during packing.

### Bundle Pricing Summary

| Bundle | Contents | Individual Value | Bundle Price | Customer Saves |
|--------|----------|-----------------|-------------|----------------|
| Kawaii Starter Pack | Plush + 2 charms + sticker pack | $45+ | $35 | $10+ |
| Blind Box Triple | 3 blind boxes | $45-48 | $40 | $5-8 |
| Pokemon TCG Essentials | Binder + sleeves + toploaders | $35-39 | $30 | $5-9 |
| Oni-Puni Mystery Box | $50+ value, hand-picked | $50+ | $35 | $15+ |
| Kawaii Gift Box | Any items + wrapping + note | Varies | +$5.99 | N/A (premium service) |

---

## 4. UPSELL FLOW

Upsells happen at four touchpoints: product page, cart page, post-purchase, and email. Each one targets a different moment in the buying decision.

### 4.1 Cart Page Upsells

**Upsell 1 -- Gift Wrapping:**
- Trigger: Any item in cart
- Display: Checkbox with product thumbnail
- Copy: "Add gift wrapping for $3.99? We'll wrap it in kawaii paper with a handwritten note."
- Implementation: Shrine cart page customization or app (In Cart Upsell or ReConvert)

**Upsell 2 -- Mystery Sticker Pack:**
- Trigger: Cart total under $25 (also helps push toward free sticker threshold)
- Display: Small product card below cart items
- Copy: "Add a mystery sticker pack for $2.99 -- 5 surprise kawaii stickers in every pack."
- Implementation: Same app as above. Product is a $2.99 mystery sticker pack (Randy assembles from overstock stickers, cost to him: $0.50-0.75)

**Upsell 3 -- Free Sticker Threshold Nudge:**
- Trigger: Cart total between $20-24.99
- Display: Progress bar or banner at top of cart
- Copy: "You're $X away from a free sticker! Add one more item to qualify."
- Implementation: Shopify free gift app (Gift Box by Jenga or similar). Auto-adds free sticker product when cart hits $25.

### 4.2 Post-Purchase Page

**Trigger:** Immediately after checkout, on the order confirmation page.

**Display:** Full-width banner or card.

**Copy:** "Your order is confirmed! Here's 10% off your next order. Use code KAWAII10 at checkout. Valid for 30 days."

**Implementation:**
- Shopify post-purchase page customization (available in Shopify Basic and above)
- Or use ReConvert app for post-purchase upsell page
- Generate unique discount codes per customer if possible (Shopify Plus feature), or use a universal code with usage limits

### 4.3 Email Upsell Sequences

**Abandoned Cart Sequence (3 emails over 48 hours):**

| Email | Timing | Subject Line | Content |
|-------|--------|-------------|---------|
| 1 | 1 hour after abandonment | "You left something cute behind" | Product image, cart contents, direct link back to cart. No discount yet. |
| 2 | 24 hours after abandonment | "Still thinking about it?" | Social proof (review quote or "X people bought this today"), urgency ("selling fast"), link back to cart. |
| 3 | 48 hours after abandonment | "Last chance -- here's 10% off" | 10% discount code, expires in 24 hours. Final push. |

**Post-Purchase Sequence (2 emails):**

| Email | Timing | Subject Line | Content |
|-------|--------|-------------|---------|
| 1 | 2 days after delivery | "How's your new [product]?" | Ask for a photo, encourage Instagram tag @onipuni, link to leave a review. |
| 2 | 14 days after delivery | "Mind leaving us a quick review?" | Direct link to product review page. Offer: "Leave a review and get 10% off your next order." |

**Win-Back Sequence (for customers who haven't purchased in 60+ days):**

| Email | Timing | Subject Line | Content |
|-------|--------|-------------|---------|
| 1 | 60 days after last purchase | "We miss you" | New arrivals since their last order, "here's what you've missed." |
| 2 | 75 days after last purchase | "Come back for 15% off" | Stronger discount, limited time (7 days). |

**Platform:** Klaviyo (integrates natively with Shopify, free up to 250 contacts).

---

## 5. FUNNEL STRATEGY

This is the full customer journey from discovery to repeat purchase.

### 5.1 Top of Funnel -- Discovery (Free Traffic)

**Primary channel:** TikTok
- Blind box unboxing videos (1-2 per day)
- "Pack with me" order fulfillment videos
- Event booth walkthroughs and haul content
- Product showcase reels with trending audio
- "What sold today" transparency content

**Secondary channel:** Pinterest
- Every product pinned with keyword-rich description
- Boards organized by collection (Blind Boxes, Pokemon TCG, Plushies, Gift Ideas)
- Idea pins showing products styled in context (desk setup, shelf display)

**Goal:** Generate awareness and drive traffic to the store or social profiles. No selling at this stage. Just visibility.

### 5.2 Middle of Funnel -- Interest (Brand Building)

**Primary channel:** Instagram
- Curated aesthetic feed (9-post grid planning, consistent pastel palette)
- Reels repurposed from TikTok content
- Stories with polls, countdowns to events, behind-the-scenes
- Highlights organized by category: New Arrivals, Blind Boxes, Events, Reviews

**Goal:** Build brand recognition and trust. Turn casual viewers into followers who recognize the Oni-Puni name.

### 5.3 Capture -- Email Acquisition

**Website:** Free kawaii phone wallpaper for email signup (homepage newsletter section)
**Events:** QR code at booth leading to signup landing page with 10% off first online order
**Social:** Link in bio on TikTok and Instagram pointing to signup page

**Goal:** Convert followers and visitors into email subscribers. Email is the only channel Randy fully owns.

### 5.4 Nurture -- Relationship Building

**Weekly email:** Mix of new product announcements, upcoming event schedule, behind-the-scenes content, and one featured product.

**Cadence:** Every Tuesday at 11 AM CT (test and adjust based on open rates).

**Content ratio:** 70% value/entertainment, 30% promotional. Never send a pure sales email without context.

### 5.5 Convert -- Store Experience

This is where the redesigned store does its work:
- Hero banner highlights best offers
- Collection grid makes browsing easy
- Product pages include cross-sells, bundles, and urgency indicators
- Cart upsells push AOV higher
- Gift wrapping option captures gift buyers
- Free sticker threshold encourages adding one more item

### 5.6 Retain -- Post-Purchase and Loyalty

- Post-purchase email with 10% off next order
- Review request at 14 days (builds social proof and re-engages customer)
- Win-back sequence at 60 days for lapsed customers
- Loyalty program (phase 2): points per dollar spent, redeemable for discounts. Use Smile.io or BON Loyalty (both integrate with Shopify).

### Funnel Summary

| Stage | Channel | Action | Goal |
|-------|---------|--------|------|
| Discovery | TikTok, Pinterest | Unboxing, product pins | Get seen |
| Interest | Instagram | Aesthetic feed, Reels | Build brand |
| Capture | Website, events | Email signup, QR codes | Collect emails |
| Nurture | Email | Weekly newsletter | Build trust |
| Convert | Shopify store | Browsing, bundles, upsells | Make the sale |
| Retain | Email, loyalty | Post-purchase, points | Repeat purchase |

---

## 6. EVENT INTEGRATION

Randy's in-person events are his biggest competitive advantage. No online-only kawaii store can replicate face-to-face interaction. The goal is to make every event feed the online business.

### 6.1 QR Code to Email Signup

**Setup:**
- Create a dedicated landing page on Shopify: onipuni.com/events
- Page content: "Thanks for stopping by our booth! Sign up for 10% off your first online order, plus a free kawaii phone wallpaper."
- Email signup form connected to Klaviyo
- Auto-tag subscribers as "event-signup" with event name (e.g., "milwaukee-comic-con-2026")

**QR code:**
- Generate via QR Code Generator (qr-code-generator.com or similar)
- Print on a 4x6 table sign with the text: "Scan for 10% off your first online order"
- Also print on business cards (see below)

**Free digital sticker download:**
- After signup, redirect to a thank-you page with a downloadable kawaii sticker image (PNG, transparent background, sized for iMessage/WhatsApp)
- This gives the customer an immediate reward and a brand touchpoint on their phone

### 6.2 Business Cards with Discount Codes

**Card content (front):**
- Oni-Puni logo
- "Your Kawaii Obsession Starts Here"
- onipuni.com

**Card content (back):**
- QR code linking to onipuni.com/events
- Unique discount code per event (e.g., COMICCON10, FLEAMARKET15)
- "Use this code for 10% off your first online order"
- Social handles: @onipuni (TikTok, Instagram)

**Unique codes per event allow Randy to track which events drive the most online sales.** This is critical data for deciding which events to attend and which to skip.

**Print specs:**
- Standard business card size (3.5 x 2 inches)
- Matte finish (fits kawaii aesthetic better than gloss)
- 500 cards per print run ($20-30 at a local print shop or Vistaprint)

### 6.3 Post-Event Email

**Trigger:** Sent manually or scheduled 24 hours after each event ends.

**Subject line:** "Thanks for visiting us at [Event Name]!"

**Content:**
- "It was great meeting you at [Event Name]! Here's what we had at the booth (and what's still available online)."
- 3-4 product images from items that were popular at the event
- "Missed something? Your event discount code [CODE] is still active for 7 more days."
- Link to the store

**Segment:** Only send to subscribers tagged with that event name.

### 6.4 Event Content Pipeline

Every event produces content for social media:

| Content Type | When to Capture | Where to Post |
|-------------|----------------|---------------|
| Booth setup timelapse | Before event opens | TikTok, Instagram Reels |
| Customer reactions | During event | TikTok, Instagram Stories |
| "What sold today" recap | End of event day | TikTok, Instagram Stories |
| Haul/restock for next event | After event | TikTok |
| Event recap email | 24 hours after event | Email list |

---

## 7. VENDOR MARKETPLACE

This is a phase 2 initiative. Randy knows other kawaii vendors from the event circuit. There is an opportunity to build a small marketplace that benefits everyone.

### 7.1 Concept: "Kawaii Marketplace" Section

**What it is:** A dedicated section on onipuni.com featuring products from other kawaii vendors. Randy curates which vendors are listed. Each vendor gets a profile page with their products.

**Revenue model:** Randy takes 15% commission on every sale made through his platform. Vendors handle their own fulfillment (drop-ship model) or ship to Randy for consolidated fulfillment.

**Why this works:**
- Randy already has the relationships from events
- Vendors get online exposure they don't have (most event vendors have no website)
- Randy earns passive income on other people's inventory
- Expands the product catalog without Randy investing in more inventory
- Positions Oni-Puni as a platform, not just a store

### 7.2 Implementation

**Phase 1 (Manual):**
- Randy lists 2-3 vendors' products on his Shopify store as regular products
- Tags them with "vendor:[vendor-name]" for tracking
- When an order comes in for a vendor product, Randy forwards the order details to the vendor
- Randy collects payment, sends 85% to vendor, keeps 15%
- Use a spreadsheet to track vendor payouts until volume justifies automation

**Phase 2 (Automated):**
- Install Multi-Vendor Marketplace app on Shopify (Multi Vendor Marketplace by Webkul or similar)
- Vendors get their own dashboard to manage products and view sales
- Payouts automated via PayPal or Stripe Connect
- Randy approves all product listings before they go live (quality control)

### 7.3 Vendor Recruitment Pitch

When Randy talks to vendors at events:

"I run an online kawaii store that gets [X] visitors a month. Most of us at these events don't have a website. I'm building a section on my site for featured vendors. You send me your product photos and prices, I list them, and when they sell, I ship them out and send you 85% of the sale. You don't have to do anything except make great products."

### 7.4 Cross-Sell Opportunities with Vendors

Once vendors are onboarded, Randy can:
- Sell them the AI ebook ($19.99) for how to use AI tools in their small business
- Upsell them to Behike AI automation services ($297-$997/month) for their own social media, email marketing, and product descriptions
- Offer to build them their own Shopify store as a one-time project ($500-1,500)

This turns vendor relationships into a lead pipeline for Behike services.

---

## 8. SEO QUICK WINS

These are changes that take 1-2 hours and start paying off within 30-60 days as Google re-indexes the site.

### 8.1 Product Title Optimization

Every product title should follow this format: [Product Name] -- [Category Keyword] [Descriptor]

**Examples:**

| Current Title | Optimized Title |
|--------------|----------------|
| Rilakkuma Plush | Rilakkuma Plush Toy -- San-X Kawaii Stuffed Animal, 8 Inch |
| Pokemon Binder | Pokemon Card Binder -- 9-Pocket TCG Portfolio for Trading Cards |
| Sonny Angel Blind Box | Sonny Angel Blind Box Figure -- Mini Collectible Surprise Toy |
| Ghost Type Stickers | Ghost Type Pokemon Stickers -- Kawaii Vinyl Sticker Pack |
| Card Sleeves | Pokemon TCG Card Sleeves -- Clear Protective Penny Sleeves, 100 Count |

### 8.2 Collection Descriptions

Every collection page needs a 200+ word description below the collection title. This is prime SEO real estate that most Shopify stores leave blank.

**Example for Blind Boxes collection:**

"Blind boxes are the ultimate surprise for kawaii collectors. Each sealed box contains a random figure from the series, and you won't know which one you got until you open it. That's what makes them so fun to collect, trade, and unbox on camera.

Our blind box selection includes popular series from Sonny Angel, POP MART, Tokidoki, and more. We restock regularly and carry both current releases and harder-to-find retired series. Whether you're hunting for a specific secret figure or just love the thrill of the reveal, we have something for you.

Every blind box we sell is factory sealed and authentic. We source directly from authorized distributors, so you can buy with confidence. Orders ship from Milwaukee, WI, with same-day shipping on orders placed before 2 PM CT.

Looking for a deal? Check out our Blind Box Triple bundle and save when you grab three boxes at once. And don't forget to follow us on TikTok for live unboxing videos where we open boxes on camera."

### 8.3 Blog Content Plan

Publish one blog post per week targeting a long-tail keyword. These posts drive organic traffic from Google for months after publication.

**First 8 posts:**

| Post Title | Target Keyword | Word Count |
|-----------|---------------|------------|
| Best Kawaii Gifts Under $25 for Every Occasion | kawaii gifts under $25 | 1,200 |
| Pokemon TCG Accessories Guide: Binders, Sleeves, and Storage | pokemon tcg accessories | 1,500 |
| What Are Blind Boxes? A Beginner's Guide to Collecting | what are blind boxes | 1,000 |
| Sonny Angel Collecting 101: Series Guide and Tips | sonny angel collection guide | 1,200 |
| How to Display Your Kawaii Collection: Shelf Ideas and Tips | kawaii collection display ideas | 1,000 |
| Best Anime Conventions in the Midwest for 2026 | anime conventions midwest 2026 | 1,200 |
| Rilakkuma vs. Sumikko Gurashi: Which San-X Character Is for You? | rilakkuma vs sumikko gurashi | 1,000 |
| Kawaii Desk Setup Ideas for Students and Remote Workers | kawaii desk setup ideas | 1,200 |

### 8.4 Image Alt Text

Every product image needs descriptive alt text. This is critical for both SEO and accessibility.

**Format:** [Product name] -- [brief visual description]

**Examples:**
- "Rilakkuma plush toy sitting on a pastel pink background, 8 inches tall"
- "Pokemon 9-pocket card binder in blue, open showing card slots"
- "Sonny Angel blind box sealed, Flower Series packaging"

**Rule:** Never leave alt text blank. Never use generic alt text like "product image" or "IMG_4532."

### 8.5 Meta Descriptions

Write custom meta descriptions for every page. These appear in Google search results and directly affect click-through rates.

**Format:** 150-155 characters. Include the primary keyword and a call to action.

**Examples:**
- Homepage: "Shop kawaii accessories, blind boxes, Pokemon TCG supplies, and original stickers at Oni-Puni. Free sticker on orders over $25. Ships fast from Milwaukee."
- Blind Boxes collection: "Browse sealed blind boxes from Sonny Angel, POP MART, and more. Authentic, factory sealed. Free shipping on orders over $50. Shop now."
- Blog post: "Looking for kawaii gifts under $25? Here are 15 cute and affordable picks for anime fans, collectors, and anyone who loves all things kawaii."

---

## 9. TECHNICAL SPECS FOR SHRINE THEME

### 9.1 Color Palette

| Usage | Color | Hex Code | Notes |
|-------|-------|----------|-------|
| Primary | Pink | #FFB6C1 | Brand color. Buttons, accents, announcement bar background. |
| Secondary | Cream | #FFF8DC | Section backgrounds, newsletter section, alternating row backgrounds. |
| Text | Charcoal | #333333 | All body text. Never use pure black (#000). |
| Headings | Dark charcoal | #2D2D2D | Section headings, product titles. |
| Accent | Soft coral | #FF8A80 | Sale badges, urgency text ("Only 3 left"), hover states. |
| Background | White | #FFFFFF | Default page background. |
| Footer | Light pink | #FFE4E9 | Footer background to frame the page. |

### 9.2 Typography

**Primary font (headings):** Quicksand (Google Font)
- Weight: 600 for headings, 700 for hero text
- Why: Rounded letterforms match the kawaii aesthetic. Playful but still legible.

**Secondary font (body):** Nunito (Google Font)
- Weight: 400 for body text, 600 for bold/emphasis
- Why: Clean, friendly, excellent readability at small sizes on mobile.

**Fallback:** If Shrine does not support custom Google Fonts natively, use the closest available options in the theme editor. Look for rounded sans-serif options.

**Font sizes:**
- Hero headline: 48px desktop / 32px mobile
- Section headings: 28px desktop / 22px mobile
- Product titles: 18px desktop / 16px mobile
- Body text: 16px desktop / 15px mobile
- Small text (captions, badges): 13px desktop / 12px mobile

### 9.3 Mobile-First Design

The kawaii demographic skews heavily mobile. Instagram and TikTok traffic arrives on phones. Design every element for mobile first, then adapt for desktop.

**Mobile priorities:**
- Sticky "Add to Cart" button on product pages (always visible as user scrolls)
- Hamburger menu with collection shortcuts (not just a generic menu)
- Tap-friendly product image gallery (swipe between images)
- Cart drawer (slide-in from right) instead of separate cart page
- Announcement bar text fits on one line at 375px width
- Product grid: 2 columns on mobile (not 1)
- Newsletter signup form: single column, large tap targets on the button

**Breakpoints:**
- Mobile: up to 767px
- Tablet: 768px to 1023px
- Desktop: 1024px and above

### 9.4 Performance Optimization

**Image optimization:**
- All product images: WebP format with JPEG fallback
- Maximum file size: 150KB per product image
- Hero banners: maximum 200KB
- Use Shopify's built-in image resizing (append _300x, _600x, _1200x to image URLs)
- Lazy load all images below the fold

**App management:**
- Audit all installed Shopify apps. Remove any that are not actively used.
- Each app can add 50-200ms to page load time
- Required apps only: Judge.me (reviews), Klaviyo (email), one upsell/cross-sell app, one bundle app

**Target performance:**
- Google PageSpeed Insights: 70+ on mobile, 85+ on desktop
- Largest Contentful Paint (LCP): under 2.5 seconds
- Total page size: under 3MB on homepage

### 9.5 Navigation Structure

**Main menu:**

| Menu Item | Links To | Type |
|-----------|---------|------|
| Shop All | /collections/all | Link |
| Blind Boxes | /collections/blind-boxes | Link |
| Plushies | /collections/plushies | Link |
| Pokemon TCG | /collections/pokemon-tcg | Link |
| Stickers | /collections/stickers | Link |
| Bundles | /collections/bundles | Link |
| Sale | /collections/sale | Link (with red text or badge) |

**Footer menu:**

| Menu Item | Links To |
|-----------|---------|
| About Us | /pages/about |
| Shipping and Returns | /pages/shipping-returns |
| Contact | /pages/contact |
| FAQ | /pages/faq |
| Privacy Policy | /policies/privacy-policy |
| Terms of Service | /policies/terms-of-service |

**Utility bar (top right):**
- Search icon
- Account icon (if customer accounts are enabled)
- Cart icon with item count badge

---

## 10. IMPLEMENTATION CHECKLIST

Organized by priority. Each item includes estimated time and who handles it.

### Phase 1: Theme and Structure (Week 1)

- [ ] Purchase and install Shrine theme -- Randy (10 min)
- [ ] Configure color palette per Section 9.1 -- Behike (30 min)
- [ ] Set up typography per Section 9.2 -- Behike (15 min)
- [ ] Build navigation menus per Section 9.5 -- Behike (20 min)
- [ ] Create homepage layout per Section 1.7 order -- Behike (2 hrs)
- [ ] Design and upload 3 hero banner images -- Randy provides photos, Behike designs in Canva (1 hr)
- [ ] Set up announcement bar -- Behike (10 min)
- [ ] Configure mobile-first settings per Section 9.3 -- Behike (30 min)
- [ ] Create collections: New Arrivals, Best Sellers, Bundles, Sale -- Behike (30 min)

### Phase 2: Product Pages (Week 2)

- [ ] Rewrite all product titles per Section 8.1 -- Behike (2 hrs)
- [ ] Rewrite all product descriptions per Section 2.6 template -- Behike (4 hrs)
- [ ] Add alt text to all product images per Section 8.4 -- Behike (1 hr)
- [ ] Install and configure cross-sell app per Section 2.1 -- Behike (1 hr)
- [ ] Set up "Only X left" inventory display per Section 2.5 -- Behike (15 min)
- [ ] Create gift wrapping product per Section 2.3 -- Behike (30 min)
- [ ] Write collection descriptions per Section 8.2 -- Behike (2 hrs)
- [ ] Write meta descriptions per Section 8.5 -- Behike (1 hr)

### Phase 3: Bundles and Upsells (Week 3)

- [ ] Create all 5 bundle product listings per Section 3 -- Behike (2 hrs)
- [ ] Install and configure bundle builder app per Section 2.2 -- Behike (1 hr)
- [ ] Set up cart page upsells per Section 4.1 -- Behike (1 hr)
- [ ] Configure post-purchase discount per Section 4.2 -- Behike (30 min)
- [ ] Create mystery sticker pack product -- Randy (assembles packs), Behike (listing)
- [ ] Set up free sticker threshold per Section 4.1 -- Behike (30 min)

### Phase 4: Email and Capture (Week 4)

- [ ] Set up Klaviyo account and connect to Shopify -- Behike (30 min)
- [ ] Build welcome email sequence per Section 4.3 -- Behike (2 hrs)
- [ ] Build abandoned cart sequence per Section 4.3 -- Behike (1.5 hrs)
- [ ] Build post-purchase sequence per Section 4.3 -- Behike (1 hr)
- [ ] Create newsletter signup section on homepage per Section 1.5 -- Behike (30 min)
- [ ] Design free kawaii wallpaper lead magnet -- Randy or freelancer (1-2 hrs)
- [ ] Configure Judge.me automated review requests -- Behike (30 min)

### Phase 5: Events and Content (Ongoing)

- [ ] Design QR code table sign per Section 6.1 -- Behike (30 min)
- [ ] Design business cards per Section 6.2 -- Behike designs, Randy prints (1 hr)
- [ ] Create events landing page per Section 6.1 -- Behike (1 hr)
- [ ] Write first blog post per Section 8.3 -- Behike (2 hrs)
- [ ] Set up TikTok business account -- Randy (15 min)
- [ ] Film and post first 5 TikTok videos -- Randy (ongoing)

### Phase 6: Marketplace (Month 2+)

- [ ] Identify 2-3 vendor partners from event contacts -- Randy
- [ ] List first vendor products on Shopify -- Behike (1 hr per vendor)
- [ ] Set up vendor payout tracking spreadsheet -- Behike (30 min)
- [ ] Create "Kawaii Marketplace" section on site -- Behike (1 hr)

---

## APPENDIX: SHOPIFY APP STACK

These are the recommended apps for the rebuilt store. Keep the total count low to maintain site speed.

| App | Purpose | Cost | Priority |
|-----|---------|------|----------|
| Judge.me | Product reviews and automated review requests | Free plan available | Required |
| Klaviyo | Email marketing and automation | Free up to 250 contacts | Required |
| Frequently Bought Together (Code Black Belt) | Cross-sell and "bought together" widgets | $9.99/mo | Required |
| Wide Bundles or Bundler | Mix-and-match bundle builder | $9.99-19.99/mo | Required |
| ReConvert or In Cart Upsell | Cart upsells and post-purchase offers | $7.99/mo | Required |
| Gift Wrap Plus | Gift wrapping add-on checkbox | $5.99/mo or use manual product method (free) | Optional |
| Smile.io or BON Loyalty | Loyalty/rewards program | Free plan available | Phase 2 |

**Total monthly app cost estimate:** $28-44/month for required apps.

---

## NOTES FOR RANDY

This document is a complete blueprint for rebuilding onipuni.com. It covers every page, every section, every upsell trigger, and every email sequence.

You do not need to implement everything at once. The phases in Section 10 are designed to be tackled week by week. Phase 1 (theme and structure) is the foundation. Everything else builds on top of it.

The bundles, upsells, and email sequences are where the real revenue growth happens. The current store has solid products but leaves money on the table at every step. A customer who buys a $15 blind box and leaves is a missed opportunity. That same customer, with a cart upsell, a bundle suggestion, and a post-purchase email, could be a $35 sale today and a repeat buyer next month.

If you have questions about any section, we can walk through it on a call. Every recommendation here is based on what works for small kawaii and collectibles businesses selling online and at events.

---

**Prepared by:** Behike AI Services
**For:** Randy, Oni-Puni (onipuni.com)
**Date:** March 23, 2026
**Version:** 1.0
