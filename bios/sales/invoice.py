#!/usr/bin/env python3
"""
Invoice/Receipt Generator -- Behike

Generates professional HTML receipts from sales.json data.

Usage:
    python3 invoice.py --generate SALE_ID     # Single receipt
    python3 invoice.py --generate-all         # All sales
    python3 invoice.py --list                 # List all sales

Called from onboarding.py after each new sale.

Output: bios/sales/receipts/invoice-{id}.html
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

SALES_DIR = Path(__file__).parent
RECEIPTS_DIR = SALES_DIR / "receipts"
ANALYTICS_DIR = SALES_DIR.parent / "analytics"
SALES_FILE = ANALYTICS_DIR / "data" / "sales.json"

RECEIPTS_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# HTML template
# ---------------------------------------------------------------------------

HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Invoice {invoice_number}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
    background: #fff; color: #111; line-height: 1.5;
    max-width: 700px; margin: 0 auto; padding: 40px 32px;
  }}
  .header {{
    border-top: 4px solid #C9A84C;
    padding-top: 24px; margin-bottom: 32px;
    display: flex; justify-content: space-between; align-items: flex-start;
  }}
  .brand {{ font-size: 28px; font-weight: 700; letter-spacing: -0.5px; }}
  .brand span {{ color: #C9A84C; }}
  .invoice-label {{
    text-align: right; font-size: 13px; color: #666;
  }}
  .invoice-label strong {{
    display: block; font-size: 15px; color: #111;
  }}
  .divider {{ border: none; border-top: 1px solid #e0e0e0; margin: 24px 0; }}
  .section {{ margin-bottom: 24px; }}
  .section-title {{
    font-size: 11px; text-transform: uppercase; letter-spacing: 1px;
    color: #999; margin-bottom: 8px;
  }}
  .field {{ margin-bottom: 4px; font-size: 14px; }}
  .field .label {{ color: #666; display: inline-block; width: 140px; }}
  .field .value {{ color: #111; font-weight: 500; }}
  table {{
    width: 100%; border-collapse: collapse; margin: 16px 0;
  }}
  th {{
    text-align: left; font-size: 11px; text-transform: uppercase;
    letter-spacing: 1px; color: #999; padding: 8px 0;
    border-bottom: 1px solid #e0e0e0;
  }}
  th:last-child {{ text-align: right; }}
  td {{
    padding: 12px 0; font-size: 14px; border-bottom: 1px solid #f0f0f0;
  }}
  td:last-child {{ text-align: right; font-weight: 600; }}
  .total-row td {{
    border-bottom: none; border-top: 2px solid #111;
    font-size: 16px; font-weight: 700; padding-top: 12px;
  }}
  .refund-note {{
    background: #fafafa; border: 1px solid #e8e8e8; border-radius: 6px;
    padding: 16px; font-size: 12px; color: #555; margin-top: 32px;
  }}
  .refund-note strong {{ color: #111; }}
  .footer {{
    margin-top: 40px; text-align: center;
    font-size: 11px; color: #aaa;
  }}
  @media print {{
    body {{ padding: 20px; }}
    .refund-note {{ break-inside: avoid; }}
  }}
</style>
</head>
<body>

<div class="header">
  <div class="brand">behike<span>.co</span></div>
  <div class="invoice-label">
    INVOICE
    <strong>{invoice_number}</strong>
    {date}
  </div>
</div>

<hr class="divider">

<div class="section">
  <div class="section-title">Bill To</div>
  <div class="field"><span class="label">Email</span><span class="value">{customer_email}</span></div>
</div>

<div class="section">
  <div class="section-title">Payment Details</div>
  <div class="field"><span class="label">Method</span><span class="value">{payment_method}</span></div>
  <div class="field"><span class="label">Status</span><span class="value">Paid</span></div>
</div>

<hr class="divider">

<table>
  <thead>
    <tr><th>Product</th><th>Amount</th></tr>
  </thead>
  <tbody>
    <tr><td>{product}</td><td>${price}</td></tr>
    <tr class="total-row"><td>Total</td><td>${price}</td></tr>
  </tbody>
</table>

<div class="refund-note">
  <strong>Refund Policy.</strong> This purchase is covered by a 30-day refund policy.
  If you are not satisfied with your purchase, contact us within 30 days of the
  transaction date for a full refund. No questions asked.
</div>

<div class="footer">
  behike.co &middot; Digital products for builders &middot; Thank you for your purchase
</div>

</body>
</html>
"""

# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------


def load_sales():
    """Load all sales from analytics data."""
    if not SALES_FILE.exists():
        return []
    try:
        data = json.loads(SALES_FILE.read_text())
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, ValueError):
        return []


def find_sale(sale_id, sales=None):
    """Find a sale by ID."""
    if sales is None:
        sales = load_sales()
    for sale in sales:
        if str(sale.get("id", "")) == str(sale_id):
            return sale
    return None


def generate_invoice(sale):
    """Generate an HTML invoice for a single sale. Returns the output path."""
    sale_id = sale.get("id", "unknown")
    product = sale.get("product", "Digital Product")
    price_raw = sale.get("price", 0)
    email = sale.get("customer_email", sale.get("email", "customer@example.com"))
    date_raw = sale.get("date", sale.get("created_at", ""))
    payment = sale.get("payment_method", sale.get("platform", "Card"))

    # Format price
    try:
        price = f"{float(price_raw):.2f}"
    except (TypeError, ValueError):
        price = "0.00"

    # Format date
    if date_raw:
        try:
            dt = datetime.fromisoformat(str(date_raw).replace("Z", "+00:00"))
            date_display = dt.strftime("%B %d, %Y")
        except (ValueError, TypeError):
            date_display = str(date_raw)[:10]
    else:
        date_display = datetime.now().strftime("%B %d, %Y")

    # Invoice number: BHK-{id} padded to 4 digits
    try:
        num = int(sale_id)
        invoice_number = f"BHK-{num:04d}"
    except (TypeError, ValueError):
        invoice_number = f"BHK-{sale_id}"

    html = HTML_TEMPLATE.format(
        invoice_number=invoice_number,
        date=date_display,
        customer_email=email,
        payment_method=payment.capitalize() if payment else "Card",
        product=product,
        price=price,
    )

    out_path = RECEIPTS_DIR / f"invoice-{sale_id}.html"
    out_path.write_text(html)
    return out_path


# ---------------------------------------------------------------------------
# Public API (called from onboarding.py)
# ---------------------------------------------------------------------------


def generate_for_sale(sale):
    """Generate invoice for a sale dict. Returns path or None."""
    try:
        path = generate_invoice(sale)
        print(f"  [invoice] Generated: {path.name}")
        return path
    except Exception as e:
        print(f"  [invoice] Error: {e}")
        return None


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def cmd_generate(sale_id):
    """Generate a single invoice by sale ID."""
    sale = find_sale(sale_id)
    if not sale:
        print(f"  Sale '{sale_id}' not found in {SALES_FILE}")
        sys.exit(1)
    path = generate_invoice(sale)
    print(f"  Generated: {path}")


def cmd_generate_all():
    """Batch-generate invoices for all sales."""
    sales = load_sales()
    if not sales:
        print("  No sales found.")
        return

    generated = 0
    skipped = 0
    for sale in sales:
        sid = sale.get("id", "unknown")
        out = RECEIPTS_DIR / f"invoice-{sid}.html"
        if out.exists():
            skipped += 1
            continue
        generate_invoice(sale)
        generated += 1

    print(f"  Generated: {generated}  Skipped (exist): {skipped}  Total: {len(sales)}")


def cmd_list():
    """List all sales with invoice status."""
    sales = load_sales()
    if not sales:
        print("  No sales found.")
        return

    print(f"\n  {'ID':<8} {'Product':<25} {'Price':>8}  {'Invoice'}")
    print("  " + "-" * 60)
    for sale in sales:
        sid = sale.get("id", "?")
        product = sale.get("product", "?")[:24]
        price = sale.get("price", 0)
        has_invoice = (RECEIPTS_DIR / f"invoice-{sid}.html").exists()
        mark = "yes" if has_invoice else " - "
        print(f"  {str(sid):<8} {product:<25} ${float(price):>7.2f}  {mark}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Invoice/Receipt Generator -- Behike",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  python3 invoice.py --generate 1         # Single receipt
  python3 invoice.py --generate-all       # All sales
  python3 invoice.py --list               # List sales + invoice status
        """,
    )
    parser.add_argument("--generate", metavar="SALE_ID", help="Generate invoice for a sale")
    parser.add_argument("--generate-all", action="store_true", help="Generate all missing invoices")
    parser.add_argument("--list", action="store_true", dest="list_sales", help="List sales")

    args = parser.parse_args()

    if not any([args.generate, args.generate_all, args.list_sales]):
        parser.print_help()
        sys.exit(0)

    if args.generate:
        cmd_generate(args.generate)
    if args.generate_all:
        cmd_generate_all()
    if args.list_sales:
        cmd_list()


if __name__ == "__main__":
    main()
