#!/bin/bash
# Run daily at midnight to scrape fresh Reddit stories
# Cron: 0 0 * * * ~/behique/tools/auto_reddit_stories.sh
cd ~/behique/tools
python3 reddit_story_scraper.py --count 3
echo "$(date): Scraped Reddit stories" >> ~/behique/Ceiba/news/reddit-scrape.log
