"""
telegram_commands.py -- BehiqueBot Command Handler Extension (REMIX 3)
Telegram Command Center for the Behike brand.

Import into the main bot file:
    from tools.telegram_commands import register_commands
    register_commands(app)
"""

import os
import re
import subprocess
from datetime import datetime

BASE_DIR = "/Users/kalani/behique"
PRIMER_PATH = os.path.join(BASE_DIR, "primer.md")
PRODUCTS_DIR = os.path.join(BASE_DIR, "Ceiba/projects/content-empire/products")
LANDING_PAGES_DIR = os.path.join(BASE_DIR, "themes/behike-store/landing-pages")
IDEAS_FILE = os.path.join(BASE_DIR, "Ceiba/IDEAS_BRAINDUMP_2026-03-22.md")
SPRINT_AUDIT = os.path.join(BASE_DIR, "tools/sprint_audit.py")
MASTER_TODO = os.path.join(BASE_DIR, "MASTER_TODO.md")


def _read_file(path):
    """Read a file and return its contents, or None if not found."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return None
    except Exception:
        return None


def _extract_section(content, heading):
    """Extract text under a markdown heading until the next heading."""
    pattern = rf"## {re.escape(heading)}\n(.*?)(?=\n## |\Z)"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


async def cmd_briefing(update, context):
    """
    /brief -- Morning briefing.
    Reads primer.md and returns current project, top 3 next actions,
    open blockers, and today's date.
    """
    try:
        content = _read_file(PRIMER_PATH)
        if not content:
            await update.message.reply_text("Could not read primer.md. File missing.")
            return

        # Current project
        project_section = _extract_section(content, "CURRENT PROJECT")
        if project_section:
            # First non-empty line
            project_line = next(
                (ln.strip() for ln in project_section.splitlines() if ln.strip()),
                "Unknown"
            )
        else:
            project_line = "Not set"

        # Next actions -- find the block after "Next action for Kalani:"
        next_actions = []
        in_actions = False
        for line in content.splitlines():
            if "Next action for Kalani" in line or "next action" in line.lower():
                in_actions = True
                continue
            if in_actions:
                stripped = line.strip()
                if stripped.startswith(("1.", "2.", "3.", "4.", "5.", "-", "*")):
                    # Clean markdown bold/italic
                    clean = re.sub(r"\*\*(.+?)\*\*", r"\1", stripped)
                    clean = re.sub(r"\*(.+?)\*", r"\1", clean)
                    next_actions.append(clean)
                    if len(next_actions) >= 3:
                        break
                elif stripped.startswith("##") and next_actions:
                    break

        # Blockers
        blockers_section = _extract_section(content, "BLOCKERS")
        blockers = []
        if blockers_section:
            for line in blockers_section.splitlines():
                stripped = line.strip()
                if stripped and re.match(r"^\d+\.", stripped):
                    clean = re.sub(r"\*\*(.+?)\*\*", r"\1", stripped)
                    blockers.append(clean)

        today = datetime.now().strftime("%Y-%m-%d")

        lines = [
            f"GOOD MORNING. {today}",
            "",
            "CURRENT PROJECT:",
            f"  {project_line}",
            "",
            "NEXT 3 ACTIONS:",
        ]
        for i, action in enumerate(next_actions[:3], 1):
            lines.append(f"  {i}. {action}")
        if not next_actions:
            lines.append("  (none found in primer.md)")

        lines += ["", "OPEN BLOCKERS:"]
        for b in blockers[:5]:
            lines.append(f"  {b}")
        if not blockers:
            lines.append("  (none)")

        await update.message.reply_text("\n".join(lines))

    except Exception as e:
        await update.message.reply_text(f"Error running /brief: {e}")


async def cmd_build(update, context):
    """
    /build [product name] -- Quick product lookup.
    Searches products/ for a matching .md file and reports status.
    """
    try:
        args = context.args
        if not args:
            await update.message.reply_text(
                "Usage: /build [product name]\nExample: /build solopreneur-os"
            )
            return

        query = "-".join(args).lower()

        # Search products dir for matching .md files
        matches = []
        try:
            for fname in os.listdir(PRODUCTS_DIR):
                if fname.endswith(".md") and query in fname.lower():
                    matches.append(fname)
        except FileNotFoundError:
            await update.message.reply_text("Products directory not found.")
            return

        if not matches:
            await update.message.reply_text(f'No products found matching "{query}".')
            return

        lines = [f"Products matching '{query}':"]
        for md_file in sorted(matches):
            base = md_file[:-3]  # strip .md
            pdf_exists = os.path.exists(os.path.join(PRODUCTS_DIR, base + ".pdf"))
            landing_exists = os.path.exists(
                os.path.join(LANDING_PAGES_DIR, base + ".html")
            )

            # Try to extract price from file
            price = "?"
            content = _read_file(os.path.join(PRODUCTS_DIR, md_file))
            if content:
                price_match = re.search(r"\$(\d+(?:\.\d{2})?)", content[:1000])
                if price_match:
                    price = "$" + price_match.group(1)

            pdf_tag = "PDF" if pdf_exists else "no PDF"
            landing_tag = "landing page" if landing_exists else "no landing page"

            lines.append(f"\n  {base}")
            lines.append(f"  Price: {price} | {pdf_tag} | {landing_tag}")

        await update.message.reply_text("\n".join(lines))

    except Exception as e:
        await update.message.reply_text(f"Error running /build: {e}")


async def cmd_todo(update, context):
    """
    /todo -- Show today's top 3 tasks.
    Reads MASTER_TODO.md and extracts first 3 uncompleted items.
    Falls back to primer.md next actions if TODO file missing.
    """
    try:
        content = _read_file(MASTER_TODO)

        if content:
            # Find uncompleted items: lines with [ ] (not [x])
            todos = []
            for line in content.splitlines():
                stripped = line.strip()
                if re.search(r"\[ \]", stripped):
                    clean = re.sub(r"- \[ \] ", "", stripped)
                    todos.append(clean)
                    if len(todos) >= 3:
                        break

            if todos:
                lines = ["TODAY'S TOP 3:"]
                for i, task in enumerate(todos, 1):
                    lines.append(f"  {i}. {task}")
                await update.message.reply_text("\n".join(lines))
                return

        # Fallback to primer.md
        primer = _read_file(PRIMER_PATH)
        if primer:
            actions = []
            in_actions = False
            for line in primer.splitlines():
                if "Next action for Kalani" in line:
                    in_actions = True
                    continue
                if in_actions:
                    stripped = line.strip()
                    if stripped.startswith(("1.", "2.", "3.")):
                        clean = re.sub(r"\*\*(.+?)\*\*", r"\1", stripped)
                        actions.append(clean)
                        if len(actions) >= 3:
                            break
                    elif stripped.startswith("##") and actions:
                        break

            if actions:
                lines = ["TOP 3 (from primer.md -- no MASTER_TODO.md found):"]
                for a in actions:
                    lines.append(f"  {a}")
                await update.message.reply_text("\n".join(lines))
                return

        await update.message.reply_text("No todo items found. Create MASTER_TODO.md or check primer.md.")

    except Exception as e:
        await update.message.reply_text(f"Error running /todo: {e}")


async def cmd_revenue(update, context):
    """
    /revenue -- Revenue check.
    Returns Gumroad dashboard link. Will show live data when API is integrated.
    """
    try:
        message = (
            "REVENUE CHECK\n"
            "\n"
            "Gumroad dashboard: behikeai.gumroad.com/dashboard\n"
            "\n"
            "Live revenue API not yet connected.\n"
            "Next: integrate Gumroad API key to pull sales data here."
        )
        await update.message.reply_text(message)
    except Exception as e:
        await update.message.reply_text(f"Error running /revenue: {e}")


async def cmd_idea(update, context):
    """
    /idea [text] -- Capture an idea immediately.
    Appends to IDEAS_BRAINDUMP file with timestamp.
    """
    try:
        args = context.args
        if not args:
            await update.message.reply_text(
                "Usage: /idea [your idea]\nExample: /idea build a notion sync tool"
            )
            return

        idea_text = " ".join(args)
        timestamp = datetime.now().strftime("%H:%M")
        entry = f"- [{timestamp}] {idea_text}\n"

        # Ensure file exists
        if not os.path.exists(IDEAS_FILE):
            today = datetime.now().strftime("%Y-%m-%d")
            with open(IDEAS_FILE, "w", encoding="utf-8") as f:
                f.write(f"# Ideas Braindump {today}\n\n")

        with open(IDEAS_FILE, "a", encoding="utf-8") as f:
            f.write(entry)

        await update.message.reply_text(f"Captured: {idea_text}")

    except Exception as e:
        await update.message.reply_text(f"Error running /idea: {e}")


async def cmd_products(update, context):
    """
    /products -- List all products with prices.
    Reads product .md files from the products directory.
    """
    try:
        if not os.path.exists(PRODUCTS_DIR):
            await update.message.reply_text("Products directory not found.")
            return

        products = []
        for fname in sorted(os.listdir(PRODUCTS_DIR)):
            if not fname.endswith(".md"):
                continue
            # Skip files in subdirs
            base = fname[:-3]
            price = "?"
            content = _read_file(os.path.join(PRODUCTS_DIR, fname))
            if content:
                price_match = re.search(r"\$(\d+(?:\.\d{2})?)", content[:800])
                if price_match:
                    price = "$" + price_match.group(1)
            products.append((base, price))

        if not products:
            await update.message.reply_text("No products found.")
            return

        lines = [f"PRODUCTS ({len(products)} total):"]
        for name, price in products:
            lines.append(f"  {name} -- {price}")

        # Telegram message limit is 4096 chars. Split if needed.
        full_message = "\n".join(lines)
        if len(full_message) <= 4000:
            await update.message.reply_text(full_message)
        else:
            # Send in chunks
            chunk = []
            chunk_size = 0
            for line in lines:
                if chunk_size + len(line) + 1 > 3800:
                    await update.message.reply_text("\n".join(chunk))
                    chunk = [line]
                    chunk_size = len(line)
                else:
                    chunk.append(line)
                    chunk_size += len(line) + 1
            if chunk:
                await update.message.reply_text("\n".join(chunk))

    except Exception as e:
        await update.message.reply_text(f"Error running /products: {e}")


async def cmd_status(update, context):
    """
    /status -- System status.
    Returns product count, landing page count, content stats from primer.md.
    """
    try:
        # Count products
        product_count = 0
        if os.path.exists(PRODUCTS_DIR):
            product_count = sum(
                1 for f in os.listdir(PRODUCTS_DIR)
                if f.endswith(".md") and os.path.isfile(os.path.join(PRODUCTS_DIR, f))
            )

        # Count landing pages
        landing_count = 0
        if os.path.exists(LANDING_PAGES_DIR):
            landing_count = sum(
                1 for f in os.listdir(LANDING_PAGES_DIR)
                if f.endswith(".html")
            )

        # Session + content stats from primer.md
        primer = _read_file(PRIMER_PATH)
        session_num = "?"
        ig_posts = "?"
        yt_scripts = "?"

        if primer:
            session_match = re.search(r"session (\d+)", primer[:500], re.IGNORECASE)
            if session_match:
                session_num = session_match.group(1)

            ig_match = re.search(r"Instagram.*?(\d+)\+?\s*posts", primer, re.IGNORECASE)
            if ig_match:
                ig_posts = ig_match.group(1) + "+"

            yt_match = re.search(r"(\d+)\+?\s*scripts", primer, re.IGNORECASE)
            if yt_match:
                yt_scripts = yt_match.group(1) + "+"

        lines = [
            "SYSTEM STATUS",
            "",
            f"Session: #{session_num}",
            f"Products (.md files): {product_count}",
            f"Landing pages (.html): {landing_count}",
            f"Instagram posts (est.): {ig_posts}",
            f"YouTube scripts (est.): {yt_scripts}",
            "",
            "Store: /themes/behike-store/landing-pages/index.html",
            "Gumroad: behikeai.gumroad.com",
        ]

        await update.message.reply_text("\n".join(lines))

    except Exception as e:
        await update.message.reply_text(f"Error running /status: {e}")


async def cmd_audit(update, context):
    """
    /audit -- Run sprint audit.
    Runs tools/sprint_audit.py and returns verdict + critical finding count.
    """
    try:
        if not os.path.exists(SPRINT_AUDIT):
            await update.message.reply_text(
                "sprint_audit.py not found at tools/sprint_audit.py."
            )
            return

        await update.message.reply_text("Running sprint audit... this may take a moment.")

        result = subprocess.run(
            ["python3", SPRINT_AUDIT],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=BASE_DIR,
        )

        output = result.stdout + result.stderr

        # Extract verdict
        verdict = "UNKNOWN"
        if "PASS" in output.upper():
            verdict = "PASS"
        elif "BLOCK" in output.upper() or "FAIL" in output.upper():
            verdict = "BLOCK"

        # Count critical findings
        critical_count = output.upper().count("CRITICAL")
        security_count = output.upper().count("SECURITY")

        lines = [
            f"AUDIT VERDICT: {verdict}",
            f"Critical findings: {critical_count}",
            f"Security flags: {security_count}",
            "",
        ]

        # Include first 10 lines of output for context
        output_lines = [ln for ln in output.splitlines() if ln.strip()][:10]
        if output_lines:
            lines.append("Output (first 10 lines):")
            lines.extend(output_lines)

        await update.message.reply_text("\n".join(lines))

    except subprocess.TimeoutExpired:
        await update.message.reply_text("Audit timed out after 60s. Run manually: python3 tools/sprint_audit.py")
    except Exception as e:
        await update.message.reply_text(f"Error running /audit: {e}")


async def cmd_help(update, context):
    """
    /help -- Show all commands with descriptions.
    """
    try:
        message = (
            "BEHIQUEBOT COMMANDS\n"
            "\n"
            "/brief       -- Morning briefing. Current project, next 3 actions, blockers.\n"
            "/build [name] -- Look up a product by name. Shows price, PDF, landing page.\n"
            "/todo        -- Top 3 tasks. Reads MASTER_TODO.md or falls back to primer.md.\n"
            "/revenue     -- Revenue check. Gumroad dashboard link.\n"
            "/idea [text] -- Capture an idea immediately to IDEAS_BRAINDUMP file.\n"
            "/products    -- List all products with prices.\n"
            "/status      -- System status. Product counts, landing pages, content stats.\n"
            "/audit       -- Run sprint_audit.py. Returns PASS/BLOCK and critical count.\n"
            "/help        -- This message.\n"
        )
        await update.message.reply_text(message)
    except Exception as e:
        await update.message.reply_text(f"Error running /help: {e}")


def register_commands(application):
    """
    Register all command handlers with the bot application.
    Call this from the main bot file.

    Usage:
        from tools.telegram_commands import register_commands
        register_commands(app)
    """
    from telegram.ext import CommandHandler

    application.add_handler(CommandHandler("brief", cmd_briefing))
    application.add_handler(CommandHandler("build", cmd_build))
    application.add_handler(CommandHandler("todo", cmd_todo))
    application.add_handler(CommandHandler("revenue", cmd_revenue))
    application.add_handler(CommandHandler("idea", cmd_idea))
    application.add_handler(CommandHandler("products", cmd_products))
    application.add_handler(CommandHandler("status", cmd_status))
    application.add_handler(CommandHandler("audit", cmd_audit))
    application.add_handler(CommandHandler("help", cmd_help))
