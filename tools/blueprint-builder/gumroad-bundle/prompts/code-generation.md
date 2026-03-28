# Code Generation Prompts
## 10 Battle-Tested Prompts for Building Tools, Scripts, Dashboards, and Bots

---

### 1. Python Script Generator (Task Automation)

**When to use:** You have a repetitive task on your computer that should be a script. File processing, data cleaning, API calls, web scraping prep.

**Prompt:**
```
Write a Python script that [DESCRIBE WHAT IT DOES].

Context:
- Input: [WHERE THE DATA COMES FROM - file, API, user input, command line args]
- Output: [WHAT THE SCRIPT PRODUCES - file, API call, console output, database entry]
- Frequency: [HOW OFTEN THIS RUNS - once, daily cron, on-demand]
- My Python level: [BEGINNER / INTERMEDIATE / ADVANCED]

Requirements:
1. Use standard library where possible. If external packages are needed, list them at the top with install commands.
2. Include error handling for every external operation (file I/O, API calls, parsing).
3. Add logging (not just print statements) with timestamps.
4. Use argparse for any configurable values (don't hardcode paths, URLs, or keys).
5. Include a main() function and if __name__ == "__main__" guard.
6. Add docstrings explaining what each function does.
7. Handle edge cases:
   - Empty input
   - Malformed data
   - Network timeout (if applicable)
   - File not found
8. Print a summary at the end (records processed, errors encountered, time elapsed).

Also provide:
- How to run it (exact command)
- How to schedule it with cron (if it should run automatically)
- How to modify it for common variations of this task

Do NOT use classes unless the complexity genuinely requires it. Keep it simple.
```

**Expected output:** Production-ready Python script with error handling, logging, and usage instructions.

---

### 2. Web Scraper Builder

**When to use:** You need data from a website that doesn't have an API. Product prices, listings, public data.

**Prompt:**
```
Build a Python web scraper for [WEBSITE OR TYPE OF SITE].

What I need to extract:
- [DATA POINT 1 - e.g., "product name"]
- [DATA POINT 2 - e.g., "price"]
- [DATA POINT 3 - e.g., "rating"]
- [DATA POINT 4 - e.g., "URL"]

Details:
- URL pattern: [URL or describe the page structure]
- Number of pages/items to scrape: [APPROXIMATE]
- Does the site use JavaScript rendering? [YES / NO / NOT SURE]
- Login required? [YES / NO]
- Rate limiting needed? [AGGRESSIVE / MODERATE / GENTLE]

Build the scraper with:

1. APPROACH SELECTION
   - If static HTML: use requests + BeautifulSoup
   - If JavaScript-rendered: use Playwright
   - Explain why you chose this approach

2. THE SCRAPER CODE
   - Proper headers (User-Agent, etc.) to avoid blocks
   - Rate limiting with random delays between requests
   - Proxy support (configurable, not required by default)
   - Pagination handling
   - Data extraction with CSS selectors or XPath
   - Error handling for missing elements, timeouts, 403s

3. DATA OUTPUT
   - Save to CSV with proper encoding
   - Optional: JSON output
   - Include timestamp of when data was scraped
   - Deduplication logic

4. RESPECTFUL SCRAPING
   - Check robots.txt guidance
   - Reasonable delays between requests
   - Don't hammer the server

5. RUNNING INSTRUCTIONS
   - Dependencies to install
   - Command to run
   - How to modify for different pages on the same site
   - How to schedule daily runs

Include sample output showing what the CSV should look like.
```

**Expected output:** Complete scraper with anti-blocking measures, data output, and scheduling instructions.

---

### 3. REST API Builder

**When to use:** You need a simple API for your project. Webhook receiver, data endpoint, integration bridge.

**Prompt:**
```
Build a REST API with [PYTHON FLASK / PYTHON FASTAPI / NODE.JS EXPRESS].

Purpose: [WHAT THIS API DOES - e.g., "receives webhook data from Shopify and stores it in a database"]

Endpoints needed:
1. [METHOD] [PATH] - [WHAT IT DOES]
   Example: POST /webhooks/orders - Receives new order data
2. [METHOD] [PATH] - [WHAT IT DOES]
3. [METHOD] [PATH] - [WHAT IT DOES]

Data model:
- [ENTITY]: [FIELDS AND TYPES]
  Example: Order: id (string), customer_email (string), total (float), created_at (datetime)

Requirements:
1. Input validation on all endpoints
2. Proper HTTP status codes (not just 200 for everything)
3. JSON error responses with useful messages
4. Authentication: [API KEY / BEARER TOKEN / WEBHOOK SECRET / NONE]
5. CORS configuration
6. Request logging
7. Health check endpoint (GET /health)
8. Rate limiting if public-facing

Database: [SQLITE / POSTGRESQL / NONE - just process and forward]

Provide:
- Complete application code (single file for simple, multi-file for complex)
- Requirements.txt / package.json
- Environment variables needed (.env.example)
- How to run locally
- How to deploy to [RAILWAY / RENDER / VERCEL]
- How to test each endpoint with curl commands
- Dockerfile (if deploying to Railway/Render)

Keep it minimal. No over-engineering. This should be deployable in under 30 minutes.
```

**Expected output:** Deployable API with all endpoints, validation, auth, and deployment instructions.

---

### 4. Dashboard Generator (Single HTML File)

**When to use:** You need a visual dashboard for data and don't want to set up a full frontend framework. One HTML file, opens in any browser.

**Prompt:**
```
Create a single-file HTML dashboard for [PURPOSE - e.g., "tracking weekly sales metrics"].

Data source: [HOW DATA GETS IN]
- Option A: Hardcoded sample data (I'll update manually)
- Option B: Fetches from API endpoint [URL]
- Option C: Reads from localStorage (I paste data in)

I want to display:
1. [METRIC - e.g., "Total revenue this week"] - as a big number card
2. [METRIC - e.g., "Orders per day"] - as a line chart
3. [METRIC - e.g., "Top products"] - as a bar chart or table
4. [METRIC - e.g., "Conversion rate"] - as a percentage with trend arrow
5. [DATA - e.g., "Recent orders"] - as a scrollable table

Design requirements:
- Dark theme (professional, not gamer)
- Responsive (works on desktop and mobile)
- Self-contained (no external CDN dependencies except Chart.js if needed)
- Clean typography, good spacing
- Color palette: [DESCRIBE or "your choice, dark background with accent color"]

Include:
- Auto-refresh capability (configurable interval)
- Last updated timestamp
- Print-friendly view (Ctrl+P should look clean)
- Filter or date range selector if applicable

The entire thing should be ONE .html file I can open in a browser.
No build tools. No npm install. No frameworks. Just HTML + CSS + vanilla JS.
```

**Expected output:** Single HTML file dashboard, ready to open in a browser.

---

### 5. Telegram Bot Scaffold

**When to use:** You want a Telegram bot that does something useful. This gives you the complete skeleton.

**Prompt:**
```
Build a Telegram bot in Python using python-telegram-bot library.

What the bot does: [DESCRIBE - e.g., "captures ideas via text and voice, categorizes them, and stores them in a JSON file"]

Commands:
- /start - [WHAT HAPPENS]
- /help - [WHAT HAPPENS]
- [/COMMAND] - [WHAT HAPPENS]
- [/COMMAND] - [WHAT HAPPENS]

Message handlers:
- Text messages: [WHAT HAPPENS - e.g., "saves as a new idea"]
- Voice messages: [WHAT HAPPENS - e.g., "transcribes with Whisper, then saves"]
- Photos: [WHAT HAPPENS or "not supported"]

Features:
1. Persistent storage: [JSON FILE / SQLITE / NOTION API / GOOGLE SHEETS]
2. User authentication: [ANYONE / WHITELIST OF USER IDS / PASSWORD]
3. AI integration: [NONE / OPENAI / OLLAMA / CLAUDE] for [WHAT]
4. Daily summary: [YES - at what time / NO]

Provide:
1. Complete bot code (production-ready, not a tutorial snippet)
2. Environment variables (.env.example)
3. Requirements.txt
4. How to get a bot token from BotFather
5. How to run locally for testing
6. How to deploy to Railway (with Procfile)
7. How to set up the webhook (or use polling for simplicity)

Error handling:
- Graceful handling of API rate limits
- Retry logic for external service calls
- User-friendly error messages (not stack traces)
- Logging to file

Keep the code clean enough that I can add features later without rewriting everything.
```

**Expected output:** Complete Telegram bot, deployable to Railway, with storage and optional AI integration.

---

### 6. Database Schema Designer

**When to use:** Before writing any code that touches a database. Plan the schema first, avoid painful migrations later.

**Prompt:**
```
Design a database schema for [APPLICATION/SYSTEM].

What it stores: [DESCRIBE THE DOMAIN - e.g., "an e-commerce store with products, orders, customers, and inventory"]

Database: [POSTGRESQL / SQLITE / MYSQL / MONGODB]

Business rules:
- [RULE 1 - e.g., "A customer can have multiple orders"]
- [RULE 2 - e.g., "Each order can have multiple products"]
- [RULE 3 - e.g., "Products have variants (size, color) with separate inventory"]
- [RULE 4 - e.g., "We need to track price history"]

Provide:

1. ENTITY RELATIONSHIP DIAGRAM (text-based)
   - All entities and their relationships
   - Cardinality (one-to-one, one-to-many, many-to-many)

2. TABLE DEFINITIONS
   - For each table: columns, data types, constraints
   - Primary keys, foreign keys, unique constraints
   - Indexes (which columns and why)
   - Default values

3. SQL CREATE STATEMENTS
   - Ready to run (for the chosen database)
   - Include comments explaining design decisions

4. SAMPLE QUERIES
   - 5 common queries this schema will need to handle
   - With expected performance notes (will this be fast or need optimization?)

5. MIGRATION NOTES
   - What's likely to change as the app grows
   - How to add [LIKELY FUTURE FEATURE] without breaking existing data
   - Columns to consider adding later

6. ANTI-PATTERNS AVOIDED
   - Explain any design decisions that prevent common schema mistakes

Keep it normalized but practical. Don't normalize to the point where every query needs 7 JOINs.
```

**Expected output:** Complete schema with SQL, ERD, sample queries, and future-proofing notes.

---

### 7. CLI Tool Builder

**When to use:** You want a command-line tool for a specific task. Something you or your team will run from the terminal.

**Prompt:**
```
Build a command-line tool in [PYTHON / NODE.JS / BASH] that [DESCRIBE WHAT IT DOES].

Example usage:
```
[SHOW HOW YOU WANT TO CALL IT]
Example: mytool process --input data.csv --output results.json --format json
```

Commands/subcommands:
1. [COMMAND] - [WHAT IT DOES] - [REQUIRED FLAGS] - [OPTIONAL FLAGS]
2. [COMMAND] - [WHAT IT DOES] - [REQUIRED FLAGS] - [OPTIONAL FLAGS]

Requirements:
1. Clear --help output for every command and subcommand
2. Colored terminal output (green for success, red for errors, yellow for warnings)
3. Progress indicator for long operations (progress bar or spinner)
4. Configuration file support (read defaults from ~/.mytoolrc or .mytool.yml)
5. Verbose mode (-v) for debugging
6. Quiet mode (-q) for scripting
7. Exit codes (0 for success, 1 for error, 2 for invalid input)

Error handling:
- Clear error messages that tell the user what went wrong AND how to fix it
- Validate inputs before processing
- Graceful Ctrl+C handling

Provide:
- Complete tool code
- Installation instructions
- Usage examples for every command
- How to add it to PATH for global access
```

**Expected output:** Complete CLI tool with help text, colored output, and error handling.

---

### 8. Cron Job / Scheduled Task Builder

**When to use:** You need something to run automatically at specific times. Daily reports, data syncs, cleanup tasks.

**Prompt:**
```
Build a scheduled task system for these recurring jobs:

Job 1: [DESCRIBE - e.g., "Pull sales data from Shopify API and update Google Sheet"]
- Schedule: [e.g., "Every day at 6 AM"]
- Expected runtime: [e.g., "2-3 minutes"]

Job 2: [DESCRIBE]
- Schedule: [WHEN]
- Expected runtime: [HOW LONG]

Job 3: [DESCRIBE]
- Schedule: [WHEN]
- Expected runtime: [HOW LONG]

For each job, provide:

1. THE SCRIPT
   - Complete, self-contained Python script
   - Logging with timestamps to a log file
   - Error notification (send alert via [TELEGRAM / EMAIL / SLACK] if job fails)
   - Lock file to prevent overlapping runs
   - Success/failure summary

2. CRON SETUP
   - Exact crontab entry
   - Environment setup (PATH, virtual env activation)
   - Log rotation (don't fill up disk)

3. MONITORING
   - How to check if jobs are running successfully
   - Where to find logs
   - What "healthy" looks like vs "something's wrong"

4. DEPLOYMENT OPTIONS
   - Option A: crontab on local machine / VPS
   - Option B: Railway scheduled worker
   - Option C: GitHub Actions scheduled workflow
   - Recommend the best option for [MY SETUP]

5. MAINTENANCE
   - How to temporarily disable a job
   - How to run a job manually for testing
   - How to change the schedule

Include a master script that runs all health checks and reports status.
```

**Expected output:** Complete scheduled task system with scripts, cron configuration, and monitoring.

---

### 9. Data Processing Pipeline

**When to use:** You have raw data that needs to be cleaned, transformed, and output in a specific format. CSV processing, JSON transformation, log parsing.

**Prompt:**
```
Build a data processing pipeline in Python for:

INPUT: [DESCRIBE THE RAW DATA]
- Format: [CSV / JSON / XML / LOG FILES / API RESPONSE]
- Size: [NUMBER OF RECORDS / FILE SIZE]
- Sample:
"""
[PASTE 3-5 LINES OF SAMPLE DATA]
"""

OUTPUT: [DESCRIBE THE DESIRED RESULT]
- Format: [CSV / JSON / DATABASE / API POST]
- Sample of desired output:
"""
[PASTE WHAT THE OUTPUT SHOULD LOOK LIKE]
"""

TRANSFORMATIONS NEEDED:
1. [TRANSFORM - e.g., "Parse dates from 'MM/DD/YYYY' to 'YYYY-MM-DD'"]
2. [TRANSFORM - e.g., "Combine first_name and last_name into full_name"]
3. [TRANSFORM - e.g., "Filter out rows where status is 'cancelled'"]
4. [TRANSFORM - e.g., "Calculate total from quantity * unit_price"]
5. [TRANSFORM - e.g., "Deduplicate by email, keeping the most recent entry"]

Requirements:
1. Use pandas for tabular data (or standard library for simple tasks)
2. Handle encoding issues (UTF-8, Latin-1, etc.)
3. Validate data at each stage (log warnings for bad rows, don't crash)
4. Memory-efficient for large files (chunked reading if needed)
5. Summary statistics after processing (rows in, rows out, rows skipped, why)
6. Dry run mode (process but don't write output, just show summary)
7. Configurable via command line args (input path, output path, options)

Provide:
- Complete script
- How to run it
- How to modify transformations for similar but different data
- Performance expectations (how long for [X] records)
```

**Expected output:** Production data processing script with validation, logging, and dry-run mode.

---

### 10. Full-Stack Project Scaffold

**When to use:** Starting a new project and want the file structure, configuration, and boilerplate done right from the start.

**Prompt:**
```
Scaffold a [PROJECT TYPE] project for [DESCRIBE WHAT IT DOES].

Tech stack:
- Backend: [PYTHON FLASK / PYTHON FASTAPI / NODE EXPRESS / NONE]
- Frontend: [VANILLA HTML+CSS+JS / REACT / NONE]
- Database: [SQLITE / POSTGRESQL / NONE]
- Hosting target: [RAILWAY / VERCEL / VPS / LOCAL ONLY]

Generate the complete project structure with:

1. DIRECTORY STRUCTURE
   - Show the full tree
   - Explain what goes in each directory

2. CONFIGURATION FILES
   - .env.example (with every variable documented)
   - .gitignore (comprehensive for this stack)
   - requirements.txt or package.json
   - Dockerfile (if deploying to containers)
   - Procfile (if Railway)

3. BOILERPLATE CODE
   - Main application entry point
   - Database connection setup (if applicable)
   - Basic routing / endpoint structure
   - Error handling middleware
   - Health check endpoint
   - CORS setup
   - Logging configuration

4. DEVELOPMENT SETUP
   - How to clone and run locally (step by step)
   - How to set up the database
   - How to run in development mode (hot reload)
   - How to run tests

5. DEPLOYMENT
   - Step-by-step deployment to [HOSTING TARGET]
   - Environment variables to set
   - Domain/DNS setup if needed

6. AI INTEGRATION (OPTIONAL)
   - CLAUDE.md starter file for this project
   - .cursorrules if using Cursor

Do NOT add features that aren't requested. Keep the scaffold minimal and clean.
Every file should have a comment at the top explaining its purpose.
```

**Expected output:** Complete project scaffold with all configuration, ready to start building features.
