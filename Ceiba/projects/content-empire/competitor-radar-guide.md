# Competitor Radar: Setup and Usage Guide

Competitor Radar is a local Python tool that monitors Gumroad sellers for price changes, new product launches, and competitive positioning. It runs on your machine, costs nothing per month, and feeds directly into your product strategy.

---

## Setup (one time)

Make sure you have the dependencies installed:

```bash
pip install requests beautifulsoup4
```

Then run the setup command to create the config directory:

```bash
python ~/behique/tools/competitor_radar.py --setup
```

This creates `~/.competitor_radar/` with two files:

- `config.json` -- your competitor list and alert settings
- `our_products.json` -- your own product catalog (used for positioning in reports)

---

## Adding Competitors

Open `~/.competitor_radar/config.json` and edit the competitors array:

```json
{
  "competitors": [
    {
      "name": "Koe Digital",
      "gumroad": "koe-digital",
      "twitter": "@thedankoe"
    },
    {
      "name": "Some Seller",
      "gumroad": "their-gumroad-username",
      "twitter": "@theirhandle"
    }
  ],
  "check_interval_hours": 24,
  "alert_on_price_change": true,
  "alert_on_new_product": true
}
```

The `gumroad` field is the username from their Gumroad URL: `app.gumroad.com/USERNAME`. The `twitter` field is optional and only used for labeling in reports.

Also update `~/.competitor_radar/our_products.json` with your actual product list and prices. This populates the "Your Position" section of every report.

---

## Running Daily Checks

Run manually:

```bash
python ~/behique/tools/competitor_radar.py
```

Or automate with a cron job. Open your crontab:

```bash
crontab -e
```

Add this line to run every morning at 7am:

```
0 7 * * * /usr/bin/python3 /Users/kalani/behique/tools/competitor_radar.py >> /Users/kalani/.competitor_radar/cron.log 2>&1
```

Snapshots are saved to `~/.competitor_radar/snapshots/YYYY-MM-DD/` one file per competitor per day.

To preview what the tool would check without making any requests:

```bash
python ~/behique/tools/competitor_radar.py --dry-run
```

---

## Generating the Report

```bash
python ~/behique/tools/competitor_radar.py --report
```

The report is printed to the terminal and also saved to `~/.competitor_radar/report-YYYY-MM-DD.md`.

The report covers:

- Your products and price range vs. each competitor
- Each competitor's product count and price range
- Bestseller badges detected this week
- New products launched in the last 7 days
- Price changes detected in the last 7 days
- A tail of the alerts log

Run the report after at least two days of snapshots so the change detection has something to compare.

---

## Interpreting the Report

**Product count gap.** If a competitor has 30 products and you have 10, they have more surface area for discovery. The goal is not to match their count blindly. Look at what price tiers they cover that you do not.

**Price range.** If their lowest product is $19.99 and yours is $4.99, you are competing on different audiences. If their highest is $49 and yours is $99, you have room at the top.

**Bestseller flags.** These are badges Gumroad shows on high-performing products. A bestseller at $14.99 tells you that price point converts well in that niche.

**New products this week.** Frequency matters. A competitor launching two products a week is in growth mode. One launching one a month is coasting.

**Price changes.** A price drop usually means the product is underperforming. A price increase usually means it is converting well and they are testing upward movement. Both signal something worth noting.

---

## When a Competitor Drops Prices

Do not immediately match. Ask two questions first:

1. Is this a permanent change or a launch promotion?
2. Does their product serve the same buyer as yours?

If yes to both, check your conversion rate first. A price problem and a positioning problem look identical from the outside. Dropping prices when the real issue is messaging solves nothing.

If they drop below your anchor price on a comparable product, consider bundling instead of dropping. Bundle two products, price the bundle 20-30% below the combined individual price, and the per-unit economics stay intact.

---

## When a Competitor Launches a New Product

Check whether it overlaps with something you have in development or already have live. If it overlaps:

- Your version goes live faster, this week if possible.
- You write a comparison post or thread: "I saw [X product type] just launched. Here is how mine is different."
- If you do not have a competing product, decide in 48 hours whether to build one or let it go. Do not let the decision sit.

---

## The Intelligence Workflow

Morning routine (10 minutes):

1. Check `~/.competitor_radar/alerts.log` for overnight changes.
2. If there are alerts, open the relevant snapshot file and read the product list.
3. Run the report once a week (Mondays work well).
4. Log any strategic decisions in `Ceiba/projects/content-empire/competitive-notes.md`.

The value is not in the data. The value is in the speed of your response. Most creators do not track competitors at all. You now have a 24-hour advantage on any pricing or launch move they make.
