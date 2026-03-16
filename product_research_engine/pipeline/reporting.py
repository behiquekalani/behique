"""
Reporting pipeline — generates CSV, JSON, and human-readable top-25 report.
"""

import csv
import json
import logging
from pathlib import Path
from datetime import datetime
from core.database import Database

logger = logging.getLogger(__name__)


class ReportingPipeline:

    def __init__(self, config, output_dir="./output"):
        self.config = config
        self.db = Database(config["database"]["path"])
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(self, top_n=25):
        products = self.db.get_scored_products(limit=200)

        if not products:
            logger.warning("No scored products to report.")
            return

        date_str = datetime.now().strftime("%Y-%m-%d")

        # CSV
        csv_path = self.output_dir / f"products_{date_str}.csv"
        fieldnames = [
            "rank", "name", "source", "category", "source_price",
            "final_score", "demand_score", "margin_score",
            "competition_score", "recency_score", "quality_score",
        ]
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for i, p in enumerate(products, 1):
                p["rank"] = i
                writer.writerow(p)
        logger.info(f"CSV: {csv_path}")

        # JSON
        json_path = self.output_dir / f"products_{date_str}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({
                "generated_at": datetime.now().isoformat(),
                "total_products": len(products),
                "products": products,
            }, f, indent=2, default=str)
        logger.info(f"JSON: {json_path}")

        # Human-readable top 25
        report_path = self.output_dir / f"top25_report_{date_str}.txt"
        top = products[:top_n]
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"PRODUCT RESEARCH REPORT -- {date_str}\n")
            f.write(f"Total scored: {len(products)}\n")
            f.write("=" * 70 + "\n\n")
            for i, p in enumerate(top, 1):
                score = p.get("final_score", 0)
                f.write(
                    f"{i:2}. {p['name'][:45]:<46} "
                    f"score:{score:6.2f} "
                    f"[{p.get('source', '?')}] "
                    f"${p.get('source_price', 0):.2f}\n"
                )
            f.write(f"\nGenerated: {datetime.now().isoformat()}\n")

        logger.info(f"Report: {report_path}")
        logger.info(f"Top product: {top[0]['name']} (score: {top[0].get('final_score', 0):.2f})" if top else "No products")

        return str(csv_path)
