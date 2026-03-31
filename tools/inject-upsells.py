#!/usr/bin/env python3
"""
Upsell Injector - Add cross-sell widgets to all landing pages.

Injects a universal upsell bar before </body> on every landing page.
The widget shows related products and the bundle offer.

Usage:
    python3 inject-upsells.py                    # Preview (dry run)
    python3 inject-upsells.py --inject            # Actually inject
    python3 inject-upsells.py --remove            # Remove injected upsells
    python3 inject-upsells.py --preview <file>    # Preview single file
"""

import os
import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
LANDING_DIR = BASE_DIR / "themes" / "behike-store" / "landing-pages"

# The universal upsell widget
UPSELL_WIDGET = """
<!-- BEHIKE UPSELL WIDGET -->
<div id="behike-upsell" style="
  position:fixed;bottom:0;left:0;right:0;z-index:9999;
  background:linear-gradient(135deg,#111 0%,#0a0a0a 100%);
  border-top:1px solid #222;padding:12px 24px;
  display:flex;align-items:center;justify-content:center;gap:16px;
  font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
  transform:translateY(100%);transition:transform .5s ease;
">
  <span style="color:#888;font-size:13px;">Want more?</span>
  <a href="https://behike.gumroad.com/l/blueprint-bundle" style="
    background:#00e5ff;color:#000;padding:8px 20px;border-radius:50px;
    text-decoration:none;font-weight:700;font-size:13px;white-space:nowrap;
  ">All 15 Blueprints — $49</a>
  <a href="https://behike.gumroad.com/l/behike-os" style="
    color:#00e5ff;text-decoration:none;font-size:13px;font-weight:600;white-space:nowrap;
  ">or Behike OS — $97</a>
  <button onclick="this.parentElement.style.display='none'" style="
    background:none;border:none;color:#555;font-size:18px;cursor:pointer;
    margin-left:8px;padding:4px 8px;
  ">&times;</button>
</div>
<script>
setTimeout(function(){
  var u=document.getElementById('behike-upsell');
  if(u)u.style.transform='translateY(0)';
},3000);
</script>
<!-- /BEHIKE UPSELL WIDGET -->
"""

UPSELL_MARKER = "<!-- BEHIKE UPSELL WIDGET -->"


def inject_file(filepath, dry_run=True):
    """Inject upsell widget into a single file."""
    content = filepath.read_text()

    # Skip if already injected
    if UPSELL_MARKER in content:
        return "skip"

    # Skip if no </body>
    if "</body>" not in content:
        return "no-body"

    new_content = content.replace("</body>", UPSELL_WIDGET + "\n</body>")

    if not dry_run:
        filepath.write_text(new_content)

    return "injected"


def remove_file(filepath):
    """Remove upsell widget from a file."""
    content = filepath.read_text()

    if UPSELL_MARKER not in content:
        return "clean"

    # Remove everything between the markers
    pattern = r'\n<!-- BEHIKE UPSELL WIDGET -->.*?<!-- /BEHIKE UPSELL WIDGET -->\n'
    new_content = re.sub(pattern, '\n', content, flags=re.DOTALL)

    filepath.write_text(new_content)
    return "removed"


def main():
    dry_run = "--inject" not in sys.argv
    remove = "--remove" in sys.argv
    preview = "--preview" in sys.argv

    if preview:
        filepath = Path(sys.argv[sys.argv.index("--preview") + 1])
        if filepath.exists():
            result = inject_file(filepath, dry_run=True)
            print(f"  {result}: {filepath.name}")
        return

    if not LANDING_DIR.exists():
        print(f"Landing pages dir not found: {LANDING_DIR}")
        return

    html_files = list(LANDING_DIR.glob("*.html"))
    print(f"\n{'='*50}")
    print(f"  UPSELL INJECTOR - {'REMOVE' if remove else ('INJECT' if not dry_run else 'DRY RUN')}")
    print(f"  {len(html_files)} landing pages found")
    print(f"{'='*50}\n")

    counts = {"injected": 0, "skip": 0, "no-body": 0, "removed": 0, "clean": 0}

    for filepath in sorted(html_files):
        if remove:
            result = remove_file(filepath)
        else:
            result = inject_file(filepath, dry_run=dry_run)

        counts[result] = counts.get(result, 0) + 1

        if result in ("injected", "removed"):
            print(f"  {result}: {filepath.name}")

    print(f"\n  Results:")
    for k, v in counts.items():
        if v > 0:
            print(f"    {k}: {v}")

    if dry_run and not remove:
        print(f"\n  This was a DRY RUN. Use --inject to apply.")


if __name__ == "__main__":
    main()
