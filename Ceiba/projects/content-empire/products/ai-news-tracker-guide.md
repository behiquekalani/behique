# Build Your Own AI News Tracker in Python

**By Behike** | $4.99

---

> Copyright 2026 Behike. All rights reserved.
> This guide was written with AI assistance. The code, architecture, and editorial direction are original work by the author.
> You may use and modify the code for personal or commercial projects. You may not redistribute this guide.

---

## What You're Building

Most people consume AI news passively. They scroll Twitter, skim headlines, and miss the stories that actually matter.

You're going to build something better: an RSS feed aggregator that pulls news from 18+ sources, scores every article by market impact, tracks key people and companies, and generates a daily digest you can read in 2 minutes.

Think of it like a ForexFactory economic calendar, but for AI. Every story gets a rating: HIGH, MEDIUM, or LOW. The stories about billion-dollar acquisitions and model launches float to the top. The "10 Tips for Prompt Engineering" listicles sink to the bottom.

Here is what the finished tool does:

- Pulls articles from TechCrunch, The Verge, Ars Technica, Hacker News, MIT Tech Review, OpenAI Blog, Anthropic News, Google AI Blog, NVIDIA Blog, VentureBeat, and 8 Reddit subreddits
- Scores every article using keyword matching (HIGH, MEDIUM, LOW impact)
- Tracks mentions of people like Sam Altman, Jensen Huang, and Dario Amodei
- Generates text or HTML digests sorted by impact
- Stores 30 days of articles in JSON for search and analysis
- Runs from the command line with simple flags

Total setup time: about 10 minutes.

### Why build this instead of using Google Alerts or Feedly

Google Alerts is reactive. You get an email hours (sometimes days) after something happens. Feedly is a reader, not a scorer. You still have to manually decide what matters.

This tracker is opinionated. It assigns impact scores the moment an article arrives. When NVIDIA drops a new chip or OpenAI fires someone, the story jumps to the top automatically. You open the digest and the first thing you see is the most important thing that happened.

The scoring system is also customizable. Google Alerts has no concept of "high impact" versus "low impact." This tracker does, and you control the definition of each level by editing a list of keywords.

Finally, everything stays local. No accounts, no API keys, no cloud dependencies. Your articles live in a JSON file on your machine. Search them, analyze them, pipe them into other tools. You own the data.

---

## Setup (10 Minutes)

### Requirements

- Python 3.8 or later (check with `python3 --version`)
- One external library: `feedparser`

### Step 1: Install feedparser

```bash
pip install feedparser
```

That is the only dependency. The rest is standard library.

### Step 2: Create the project structure

```bash
mkdir -p ~/ai-tracker
cd ~/ai-tracker
touch ai_news_tracker.py
```

### Step 3: Configure your RSS feeds

The feed list is a simple Python list of dictionaries. Each feed has a name, URL, and category. Here is a starter set:

```python
FEEDS = [
    {"name": "TechCrunch AI", "url": "https://techcrunch.com/category/artificial-intelligence/feed/", "category": "ai"},
    {"name": "The Verge AI", "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml", "category": "ai"},
    {"name": "Ars Technica", "url": "https://feeds.arstechnica.com/arstechnica/technology-lab", "category": "tech"},
    {"name": "Hacker News Best", "url": "https://hnrss.org/best?q=AI+OR+LLM+OR+GPT+OR+Claude+OR+NVIDIA", "category": "ai"},
    {"name": "OpenAI Blog", "url": "https://openai.com/blog/rss.xml", "category": "releases"},
    {"name": "Anthropic News", "url": "https://www.anthropic.com/news/rss.xml", "category": "releases"},
    {"name": "Google AI Blog", "url": "https://blog.google/technology/ai/rss/", "category": "releases"},
    {"name": "NVIDIA Blog", "url": "https://blogs.nvidia.com/feed/", "category": "hardware"},
    {"name": "VentureBeat AI", "url": "https://venturebeat.com/category/ai/feed/", "category": "ai"},
    {"name": "r/MachineLearning", "url": "https://www.reddit.com/r/MachineLearning/hot.rss", "category": "research"},
    {"name": "r/LocalLLaMA", "url": "https://www.reddit.com/r/LocalLLaMA/hot.rss", "category": "ai"},
    {"name": "r/artificial", "url": "https://www.reddit.com/r/artificial/hot.rss", "category": "ai"},
]
```

Categories help you filter later. Use whatever labels make sense for your workflow: `ai`, `tech`, `releases`, `hardware`, `research`, `business`.

To add a new feed, just append another dictionary to the list. Any valid RSS or Atom feed URL works.

### Step 4: Set up storage

The tracker stores everything in JSON files. No database needed. Define your paths at the top of the script:

```python
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
ARTICLES_FILE = DATA_DIR / "articles.json"
TRACKED_FILE = DATA_DIR / "tracked.json"
DIGEST_DIR = DATA_DIR / "digests"
```

Then create a setup function:

```python
def ensure_dirs():
    """Create data directories if they don't exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    DIGEST_DIR.mkdir(parents=True, exist_ok=True)
```

Call `ensure_dirs()` at the start of your main function. The first time you run the script, it creates the folder structure automatically.

---

## The Scoring System

This is where the tracker becomes useful. Instead of showing you 200 articles in chronological order, it ranks them by market impact.

### How keyword matching works

The scoring function takes the article title and summary, converts everything to lowercase, and counts how many impact keywords appear.

```python
IMPACT_KEYWORDS = {
    "high": [
        "launch", "release", "announce", "acquire", "billion", "million funding",
        "ipo", "regulation", "ban", "lawsuit", "breakthrough", "open source",
        "gpt-5", "gpt-6", "claude 4", "claude 5", "gemini 2", "llama 4",
        "fired", "resign", "ceo", "arrested", "sec", "ftc", "antitrust",
        "nvidia", "blackwell", "h100", "h200", "b100", "b200",
        "agi", "superintelligence", "safety", "alignment",
        "apple intelligence", "siri", "alexa", "cortana",
    ],
    "medium": [
        "update", "feature", "partnership", "integration", "api",
        "pricing", "model", "benchmark", "performance", "fine-tune",
        "agent", "plugin", "tool", "mcp", "function calling",
        "series a", "series b", "series c", "seed round", "valuation",
        "layoff", "hire", "expansion", "revenue",
    ],
    "low": [
        "tutorial", "guide", "how to", "review", "comparison",
        "opinion", "analysis", "research paper", "arxiv",
        "community", "developer", "conference", "meetup",
    ],
}
```

### The scoring function

```python
def score_impact(title, summary=""):
    """Score article impact: HIGH / MEDIUM / LOW."""
    text = f"{title} {summary}".lower()

    high_hits = sum(1 for kw in IMPACT_KEYWORDS["high"] if kw.lower() in text)
    med_hits = sum(1 for kw in IMPACT_KEYWORDS["medium"] if kw.lower() in text)

    if high_hits >= 1:
        return "HIGH", high_hits * 3 + med_hits
    elif med_hits >= 1:
        return "MEDIUM", med_hits * 2
    else:
        return "LOW", 1
```

The numeric score (second return value) lets you sort within the same impact level. An article that hits 3 HIGH keywords ranks above one that hits 1.

### Customizing the keywords

This is the most important part to personalize. If you work in robotics, add keywords like "humanoid", "boston dynamics", "figure", "1x". If you care about open source models, add "weights released", "apache 2.0", "mit license".

The keyword lists are just Python lists. Edit them freely.

### Entity tracking

The tracker also watches for mentions of specific people and companies:

```python
DEFAULT_TRACKED = [
    {"name": "Sam Altman", "type": "person", "org": "OpenAI"},
    {"name": "Dario Amodei", "type": "person", "org": "Anthropic"},
    {"name": "Jensen Huang", "type": "person", "org": "NVIDIA"},
    {"name": "OpenAI", "type": "company", "org": "OpenAI"},
    {"name": "Anthropic", "type": "company", "org": "Anthropic"},
    {"name": "NVIDIA", "type": "company", "org": "NVIDIA"},
]

def find_mentions(text, tracked):
    """Find tracked people/companies mentioned in text."""
    mentions = []
    text_lower = text.lower()
    for entity in tracked:
        if entity["name"].lower() in text_lower:
            mentions.append(entity["name"])
    return mentions
```

When an article mentions a tracked entity, it shows up in the digest with their name attached. This makes it easy to spot when a CEO makes a move or a company drops an announcement.

You can add new entities from the command line:

```bash
python3 ai_news_tracker.py --track "Yann LeCun" --track-type person --track-org Meta
```

---

## Running It

### Fetch new articles

```bash
python3 ai_news_tracker.py --fetch
```

This pulls from all configured feeds, deduplicates against existing articles (using an MD5 hash of title + URL), scores them, and saves everything to `articles.json`. Old articles beyond 30 days are automatically pruned.

Here is what happens under the hood when you run `--fetch`:

1. The script loops through every feed in your `FEEDS` list
2. For each feed, it parses the RSS XML using feedparser and takes the most recent 15 entries
3. Each entry gets a unique ID generated from its title and URL (so the same article from different feeds does not get counted twice)
4. The title and summary are run through the impact scoring function
5. Entity tracking scans for mentions of anyone in your tracked list
6. New articles are appended to the existing JSON file
7. Articles older than 30 days are removed to keep the file manageable

The 30-day retention window means your `articles.json` file stays under a few megabytes even with 18 feeds running hourly. If you want to keep articles longer, change the `timedelta(days=30)` value in the `fetch_feeds` function.

### View top stories by impact

```bash
python3 ai_news_tracker.py --top 10
```

Output looks like this:

```
  [HIGH] NVIDIA Announces Blackwell B300 GPU for AI Training [NVIDIA, Jensen Huang]
         NVIDIA Blog | 2026-03-21
         The new B300 delivers 4x the performance of H100...

  [HIGH] OpenAI Releases GPT-5 with Reasoning Capabilities [OpenAI, Sam Altman]
         TechCrunch AI | 2026-03-21
         The latest model from OpenAI shows significant...

  [MEDIUM] New MCP Integration Connects Claude to Enterprise Tools
           Anthropic News | 2026-03-20
           The model context protocol now supports...
```

HIGH articles show in red. MEDIUM in yellow. LOW in gray. Entity mentions appear in brackets.

### Generate a daily digest

Text format (prints to terminal):

```bash
python3 ai_news_tracker.py --digest
```

HTML format (saves to file, great for reading in a browser):

```bash
python3 ai_news_tracker.py --digest --format html
```

The HTML digest is styled with a dark theme, impact color badges, clickable links, and a stats bar showing total stories and breakdown by impact level.

### Search past articles

```bash
python3 ai_news_tracker.py --search "claude"
python3 ai_news_tracker.py --search "funding"
python3 ai_news_tracker.py --search "regulation"
```

Search matches against title, summary, and entity mentions. Results are sorted by impact score.

### Default behavior

Running the script with no flags does a fetch + digest:

```bash
python3 ai_news_tracker.py
```

This is the "daily driver" command. Run it once in the morning.

---

## Automate It

### Cron job: fetch every hour

Open your crontab:

```bash
crontab -e
```

Add this line to fetch new articles every hour:

```
0 * * * * /usr/bin/python3 /path/to/ai_news_tracker.py --fetch >> /tmp/news_tracker.log 2>&1
```

### Daily digest at 6am

Add a second cron job:

```
0 6 * * * /usr/bin/python3 /path/to/ai_news_tracker.py --digest --format html --save /path/to/data/digests/daily.html
```

### Bash script for one-command operation

Create a file called `daily_news.sh`:

```bash
#!/bin/bash
# Daily AI News - fetch and generate digest

TRACKER="/path/to/ai_news_tracker.py"
PYTHON="/usr/bin/python3"

echo "Fetching latest AI news..."
$PYTHON $TRACKER --fetch

echo ""
echo "Generating digest..."
$PYTHON $TRACKER --digest

echo ""
echo "Top 5 stories:"
$PYTHON $TRACKER --top 5
```

Make it executable:

```bash
chmod +x daily_news.sh
```

Now you have a single command for your morning routine:

```bash
./daily_news.sh
```

### What to do with the digest

The HTML digest works as a standalone webpage. Open it in any browser. The text digest works in a terminal or as the body of an email.

Some ideas for using the output:

- Forward the HTML digest to your team's Slack channel
- Use the top HIGH stories as content inspiration (see the companion guide on turning news into Instagram posts)
- Track entity mention frequency over time to spot trends
- Pipe the text digest into a notification system

The article data is plain JSON. You can write additional scripts to analyze it, export to CSV, or feed it into other tools. The tracker is intentionally simple. It does one thing well: surface the AI news that matters, and hide the noise.

---

**Next steps:** Once you have a steady flow of scored articles, check out "Turn RSS Feeds into Instagram Posts with Python" to automatically generate social media content from your highest-impact stories.

---

*Built by Behike. For builders who want signal, not noise.*
