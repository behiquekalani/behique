#!/bin/bash
cd ~/behique/tools
python3 reddit_niche_crawler.py
python3 reddit_niche_crawler.py --digest
echo "$(date): Niche scan complete" >> ~/behique/Ceiba/news/niche-scan.log
