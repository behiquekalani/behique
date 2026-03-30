#!/usr/bin/env python3
"""
Creative Flooding System - Behike
Generate dozens of distinct static ad concepts at near-zero cost.
Test fast, read data, double down on winners.

Usage:
  python3 flood.py generate --business "Innova Barber" --config campaigns/innova-barber.json
  python3 flood.py generate --business "Behike" --config campaigns/behike-blueprints.json
  python3 flood.py render --campaign campaigns/innova-barber.json --output output/innova-barber/
  python3 flood.py analyze --campaign campaigns/innova-barber.json
  python3 flood.py list
"""

import json
import os
import sys
import hashlib
import subprocess
from datetime import datetime
from pathlib import Path

TOOL_DIR = Path(__file__).parent
CAMPAIGNS_DIR = TOOL_DIR / "campaigns"
TEMPLATES_DIR = TOOL_DIR / "templates"
OUTPUT_DIR = TOOL_DIR / "output"


# ============================================================
# CORE: CONCEPT GENERATOR
# ============================================================

class ConceptGenerator:
    """
    Generates distinct ad concepts from a business profile.
    Each concept = unique angle + headline + body + CTA.
    No two concepts should test the same message.
    """

    # Master angle library - the strategic layer
    ANGLE_FRAMEWORKS = {
        "pain_agitate_solve": {
            "description": "Identify a specific pain, twist the knife, present solution",
            "template": "pain → agitate → solve",
            "example": "Tired of bad haircuts? → You've wasted $500 on barbers who don't listen → Innova Barber: precision cuts, every time."
        },
        "before_after": {
            "description": "Show the transformation",
            "template": "before state → after state",
            "example": "Before: 47 open tabs, zero revenue → After: one blueprint, first dollar made"
        },
        "social_proof": {
            "description": "Let others sell for you",
            "template": "number/stat + what it proves",
            "example": "186 five-star reviews. Zero marketing budget. The work speaks."
        },
        "fear_of_missing": {
            "description": "What they lose by NOT acting",
            "template": "cost of inaction → urgency",
            "example": "Every day without a system is another day your competitor builds one."
        },
        "identity": {
            "description": "Make them see themselves in the product",
            "template": "you are [type] → this was made for you",
            "example": "You have ADHD. You have 47 ideas. You've finished zero. This blueprint was built for your brain."
        },
        "contrarian": {
            "description": "Challenge conventional wisdom",
            "template": "everyone says X → here's why that's wrong → our way",
            "example": "Stop watching YouTube courses. Start building. Here's a one-page system that replaces 40 hours of fluff."
        },
        "specificity": {
            "description": "Ultra-specific claim that builds trust",
            "template": "exact number/detail that proves expertise",
            "example": "We've built 100+ products in 14 days using this exact workflow."
        },
        "objection_crusher": {
            "description": "Address the #1 reason they won't buy",
            "template": "I know what you're thinking → here's why you're wrong",
            "example": "\"I can't afford it\" — It's $4.99. You spent more on coffee this morning."
        },
        "us_vs_them": {
            "description": "Position against the alternative",
            "template": "them (bad) → us (good)",
            "example": "Agencies charge $3,000. We built the same thing for $19.99. Same results. Different price."
        },
        "story": {
            "description": "Mini narrative that hooks",
            "template": "situation → struggle → discovery → result",
            "example": "6 months ago I had zero revenue. Then I found Claude Code. Now I have 100+ products live."
        },
        "question_hook": {
            "description": "Ask a question they can't ignore",
            "template": "question that reveals a gap → answer is your product",
            "example": "What if you could build a business in one page? You can. Here's the blueprint."
        },
        "authority": {
            "description": "Establish credibility fast",
            "template": "credential/experience → what it means for them",
            "example": "20+ years cutting hair. Not YouTube tutorials. Real experience, real results."
        },
    }

    def __init__(self, business_config):
        self.config = business_config
        self.business = business_config["business"]
        self.products = business_config.get("products", [])
        self.customer = business_config.get("customer", {})
        self.pain_points = business_config.get("pain_points", [])
        self.differentiators = business_config.get("differentiators", [])
        self.proof_points = business_config.get("proof_points", [])
        self.offers = business_config.get("offers", [])

    def generate_concepts(self, count=50):
        """Generate N distinct ad concepts using strategic angle rotation."""
        concepts = []
        angle_keys = list(self.ANGLE_FRAMEWORKS.keys())

        for i in range(count):
            # Rotate through angles
            angle_key = angle_keys[i % len(angle_keys)]
            angle = self.ANGLE_FRAMEWORKS[angle_key]

            # Rotate through pain points
            pain = self.pain_points[i % len(self.pain_points)] if self.pain_points else "general"

            # Rotate through products/offers
            product = self.products[i % len(self.products)] if self.products else {"name": self.business["name"]}
            offer = self.offers[i % len(self.offers)] if self.offers else None

            # Rotate through differentiators
            diff = self.differentiators[i % len(self.differentiators)] if self.differentiators else ""

            # Rotate through proof points
            proof = self.proof_points[i % len(self.proof_points)] if self.proof_points else ""

            concept = self._build_concept(
                index=i + 1,
                angle_key=angle_key,
                angle=angle,
                pain=pain,
                product=product,
                offer=offer,
                differentiator=diff,
                proof=proof
            )
            concepts.append(concept)

        return concepts

    def _build_concept(self, index, angle_key, angle, pain, product, offer, differentiator, proof):
        """Build a single ad concept from components."""
        product_name = product.get("name", self.business["name"])
        product_price = product.get("price", "")
        business_name = self.business["name"]
        cta = product.get("cta", self.business.get("default_cta", "Learn More"))
        cta_url = product.get("url", self.business.get("url", "#"))

        # Generate headline based on angle
        headline = self._generate_headline(angle_key, pain, product_name, differentiator, proof)

        # Generate body text
        body = self._generate_body(angle_key, pain, product_name, differentiator, proof, product_price)

        # Generate concept ID
        concept_id = f"CF-{hashlib.md5(f'{index}{angle_key}{pain}{product_name}'.encode()).hexdigest()[:8]}"

        return {
            "id": concept_id,
            "index": index,
            "angle": angle_key,
            "angle_description": angle["description"],
            "pain_point": pain,
            "product": product_name,
            "price": product_price,
            "headline": headline,
            "body": body,
            "cta": cta,
            "cta_url": cta_url,
            "offer": offer,
            "business": business_name,
            "generated_at": datetime.now().isoformat(),
            "status": "draft",  # draft → testing → winner → video_candidate → produced
            "metrics": {
                "impressions": 0,
                "clicks": 0,
                "ctr": 0,
                "conversions": 0,
                "spend": 0,
                "cpa": 0
            }
        }

    def _generate_headline(self, angle_key, pain, product, diff, proof):
        """Generate a headline based on the angle framework."""
        headlines = {
            "pain_agitate_solve": [
                f"Cansado de {pain}?",
                f"{pain}. Ya basta.",
                f"Si {pain}, necesitas leer esto.",
                f"El problema no eres tu. Es que nadie te dio {product}.",
            ],
            "before_after": [
                f"Antes: {pain}. Despues: {diff}.",
                f"De {pain} a {diff}. En una pagina.",
                f"{pain} → {diff}. Asi de simple.",
            ],
            "social_proof": [
                f"{proof}",
                f"No lo decimos nosotros. {proof}",
                f"{proof}. Y sigue creciendo.",
            ],
            "fear_of_missing": [
                f"Cada dia sin {product} es un dia perdido.",
                f"Tu competencia ya tiene esto. Tu no.",
                f"No es que no puedes. Es que no has empezado.",
            ],
            "identity": [
                f"Tienes ADHD y 47 ideas? Esto es para ti.",
                f"Si eres {self.customer.get('identity', 'builder')}, esto te va a cambiar la vida.",
                f"Hecho para gente que {self.customer.get('behavior', 'builds, not just talks')}.",
            ],
            "contrarian": [
                f"Deja de {pain}. Hay un camino mejor.",
                f"Todo el mundo dice que necesitas X. Estan equivocados.",
                f"No necesitas otro curso. Necesitas {product}.",
            ],
            "specificity": [
                f"{diff}. Exactamente.",
                f"No es teoria. Son {diff}.",
                f"{diff}. Comprobado.",
            ],
            "objection_crusher": [
                f'"No tengo dinero" — Es ${product.split("$")[-1] if "$" in str(product) else "menos de lo que piensas"}.',
                f'"No tengo tiempo" — Son 15 minutos.',
                f'"No se si funciona" — {proof}',
            ],
            "us_vs_them": [
                f"Agencias cobran $3,000. Nosotros: {product}.",
                f"Cursos de 40 horas vs. una pagina que funciona.",
                f"Ellos te venden humo. Nosotros te damos {product}.",
            ],
            "story": [
                f"Hace 6 meses no tenia nada. Hoy tengo {diff}.",
                f"Lo construi con mis propias manos. Tu tambien puedes.",
                f"No soy experto. Solo encontre el sistema correcto.",
            ],
            "question_hook": [
                f"Y si pudieras {diff}?",
                f"Que harias si {pain} ya no fuera un problema?",
                f"Sabias que puedes {diff} en un dia?",
            ],
            "authority": [
                f"{diff}. No tutoriales de YouTube.",
                f"Experiencia real. Resultados reales.",
                f"{proof}. El trabajo habla solo.",
            ],
        }

        options = headlines.get(angle_key, [f"{product} - {diff}"])
        return options[hash(f"{pain}{product}") % len(options)]

    def _generate_body(self, angle_key, pain, product, diff, proof, price):
        """Generate body text for the ad."""
        bodies = {
            "pain_agitate_solve": f"Llevas meses con {pain}. Cada dia es igual. {product} te da un sistema que funciona. {proof}.",
            "before_after": f"Antes de {product}: {pain}. Despues: {diff}. No es magia. Es un sistema.",
            "social_proof": f"{proof}. No necesitamos convencerte. Los numeros hablan solos. {product}.",
            "fear_of_missing": f"Mientras tu esperas, otros estan construyendo. {product} es el primer paso. {diff}.",
            "identity": f"Este no es otro producto generico. {product} fue hecho para gente como tu. {diff}.",
            "contrarian": f"Olvidate de lo que te dijeron. {product} es diferente. {diff}. {proof}.",
            "specificity": f"{diff}. No promesas vacias. {product} te da exactamente lo que necesitas. {proof}.",
            "objection_crusher": f"Entendemos la duda. Por eso {product} viene con {diff}. {proof}.",
            "us_vs_them": f"La alternativa cuesta 10x mas y toma 10x mas tiempo. {product}: {diff}. {price}.",
            "story": f"Empece desde cero. {pain} era mi realidad. Entonces descubri {product}. Ahora: {diff}.",
            "question_hook": f"La respuesta es {product}. {diff}. {proof}. Empieza hoy.",
            "authority": f"No somos teoricos. {diff}. {proof}. {product} es el resultado de experiencia real.",
        }
        return bodies.get(angle_key, f"{product}. {diff}. {proof}.")


# ============================================================
# RENDERER: HTML STATIC AD GENERATOR
# ============================================================

class StaticAdRenderer:
    """Renders ad concepts as HTML static images ready for screenshot."""

    SIZES = {
        "feed_square": (1080, 1080),
        "feed_portrait": (1080, 1350),
        "story": (1080, 1920),
        "landscape": (1200, 628),
    }

    def __init__(self, template_dir=None):
        self.template_dir = template_dir or TEMPLATES_DIR

    def render_concept(self, concept, size="feed_square", style="dark"):
        """Generate HTML for a single ad concept."""
        w, h = self.SIZES[size]

        if style == "dark":
            bg, text, accent, dim = "#0a0a0a", "#f0f0f0", "#c8ff00", "#888888"
        elif style == "light":
            bg, text, accent, dim = "#f8f5f0", "#2c2c2c", "#2d6a4f", "#6b6b6b"
        elif style == "warm":
            bg, text, accent, dim = "#1a0a00", "#f0e0d0", "#d4a373", "#998877"
        else:
            bg, text, accent, dim = "#0a0a0a", "#f0f0f0", "#c8ff00", "#888888"

        headline = concept["headline"]
        body = concept["body"]
        cta = concept["cta"]
        business = concept["business"]
        price = concept.get("price", "")
        offer = concept.get("offer", {})
        offer_text = offer.get("text", "") if offer else ""

        html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    width: {w}px; height: {h}px;
    background: {bg}; color: {text};
    font-family: 'Inter', sans-serif;
    display: flex; flex-direction: column;
    justify-content: center; padding: {int(w*0.08)}px;
    overflow: hidden; position: relative;
  }}
  .headline {{
    font-size: {int(w*0.055)}px; font-weight: 900;
    line-height: 1.15; margin-bottom: {int(h*0.03)}px;
    max-width: 90%;
  }}
  .headline .accent {{ color: {accent}; }}
  .body {{
    font-size: {int(w*0.028)}px; color: {dim};
    line-height: 1.6; margin-bottom: {int(h*0.04)}px;
    max-width: 85%;
  }}
  .cta-wrap {{
    display: flex; align-items: center; gap: {int(w*0.02)}px;
  }}
  .cta {{
    background: {accent}; color: {bg};
    padding: {int(w*0.015)}px {int(w*0.04)}px;
    border-radius: 50px; font-weight: 700;
    font-size: {int(w*0.025)}px; letter-spacing: 0.5px;
  }}
  .price {{
    font-size: {int(w*0.04)}px; font-weight: 800;
    color: {accent}; margin-left: {int(w*0.02)}px;
  }}
  .offer {{
    position: absolute; top: {int(h*0.04)}px; right: {int(w*0.06)}px;
    background: {accent}; color: {bg};
    padding: {int(w*0.012)}px {int(w*0.025)}px;
    border-radius: 8px; font-weight: 700;
    font-size: {int(w*0.022)}px;
    transform: rotate(3deg);
  }}
  .brand {{
    position: absolute; bottom: {int(h*0.04)}px; right: {int(w*0.06)}px;
    font-size: {int(w*0.018)}px; color: {dim};
    letter-spacing: 3px; text-transform: uppercase; opacity: 0.5;
  }}
  .angle-tag {{
    font-size: {int(w*0.016)}px; color: {accent};
    letter-spacing: 2px; text-transform: uppercase;
    margin-bottom: {int(h*0.02)}px; font-weight: 600;
  }}
  .id-tag {{
    position: absolute; bottom: {int(h*0.04)}px; left: {int(w*0.06)}px;
    font-size: {int(w*0.014)}px; color: {dim}; opacity: 0.3;
  }}
</style>
</head>
<body>
  <div class="angle-tag">{concept['angle'].replace('_', ' ')}</div>
  <div class="headline">{headline}</div>
  <div class="body">{body}</div>
  <div class="cta-wrap">
    <div class="cta">{cta}</div>
    {"<div class='price'>" + price + "</div>" if price else ""}
  </div>
  {"<div class='offer'>" + offer_text + "</div>" if offer_text else ""}
  <div class="brand">{business}</div>
  <div class="id-tag">{concept['id']}</div>
</body>
</html>"""
        return html

    def render_all(self, concepts, output_dir, size="feed_square", style="dark"):
        """Render all concepts to HTML files."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        rendered = []
        for concept in concepts:
            filename = f"{concept['id']}.html"
            filepath = output_path / filename
            html = self.render_concept(concept, size=size, style=style)
            filepath.write_text(html)
            rendered.append(str(filepath))

        # Generate index page
        self._generate_index(concepts, output_path, style)

        return rendered

    def _generate_index(self, concepts, output_path, style):
        """Generate an index page showing all concepts as a grid."""
        if style == "dark":
            bg, text, accent, border = "#0a0a0a", "#f0f0f0", "#c8ff00", "#222"
        else:
            bg, text, accent, border = "#f8f5f0", "#2c2c2c", "#2d6a4f", "#ddd"

        cards = ""
        for c in concepts:
            status_color = {
                "draft": "#888", "testing": "#f0ad4e",
                "winner": "#5cb85c", "video_candidate": "#c8ff00",
                "produced": "#5bc0de"
            }.get(c["status"], "#888")

            cards += f"""
        <div class="card" onclick="window.open('{c['id']}.html')">
          <div class="card-angle">{c['angle'].replace('_', ' ')}</div>
          <div class="card-headline">{c['headline'][:80]}{'...' if len(c['headline']) > 80 else ''}</div>
          <div class="card-body">{c['body'][:120]}{'...' if len(c['body']) > 120 else ''}</div>
          <div class="card-meta">
            <span class="card-id">{c['id']}</span>
            <span class="card-status" style="color:{status_color}">{c['status']}</span>
            <span class="card-product">{c['product'][:30]}</span>
          </div>
        </div>"""

        html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Creative Flooding - Campaign Overview</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ background:{bg}; color:{text}; font-family:'Inter',sans-serif; padding:40px; }}
  h1 {{ font-size:28px; margin-bottom:8px; }}
  .subtitle {{ color:{accent}; font-size:14px; letter-spacing:2px; text-transform:uppercase; margin-bottom:32px; }}
  .stats {{ display:flex; gap:24px; margin-bottom:32px; }}
  .stat {{ background:{border}; padding:16px 24px; border-radius:12px; }}
  .stat-num {{ font-size:28px; font-weight:700; color:{accent}; }}
  .stat-label {{ font-size:12px; color:#888; text-transform:uppercase; letter-spacing:1px; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(300px,1fr)); gap:16px; }}
  .card {{ background:{"#111" if style=="dark" else "#fff"}; border:1px solid {border}; border-radius:12px; padding:20px; cursor:pointer; transition:all 0.2s; }}
  .card:hover {{ border-color:{accent}; transform:translateY(-2px); }}
  .card-angle {{ font-size:11px; color:{accent}; letter-spacing:2px; text-transform:uppercase; margin-bottom:8px; font-weight:600; }}
  .card-headline {{ font-size:16px; font-weight:700; margin-bottom:8px; line-height:1.3; }}
  .card-body {{ font-size:13px; color:#888; line-height:1.5; margin-bottom:12px; }}
  .card-meta {{ display:flex; justify-content:space-between; font-size:11px; color:#666; }}
  .card-status {{ font-weight:600; text-transform:uppercase; letter-spacing:1px; }}
  .filters {{ display:flex; gap:8px; margin-bottom:24px; flex-wrap:wrap; }}
  .filter-btn {{ padding:6px 16px; border-radius:50px; border:1px solid {border}; background:none; color:{text}; font-size:12px; cursor:pointer; font-family:inherit; }}
  .filter-btn.active {{ background:{accent}; color:{bg}; border-color:{accent}; }}
</style></head><body>
  <h1>Creative Flooding</h1>
  <div class="subtitle">{concepts[0]['business'] if concepts else 'Campaign'} &bull; {len(concepts)} concepts generated</div>
  <div class="stats">
    <div class="stat"><div class="stat-num">{len(concepts)}</div><div class="stat-label">Total Concepts</div></div>
    <div class="stat"><div class="stat-num">{len(set(c['angle'] for c in concepts))}</div><div class="stat-label">Unique Angles</div></div>
    <div class="stat"><div class="stat-num">{len(set(c['product'] for c in concepts))}</div><div class="stat-label">Products</div></div>
    <div class="stat"><div class="stat-num">{len(set(c['pain_point'] for c in concepts))}</div><div class="stat-label">Pain Points</div></div>
  </div>
  <div class="filters">
    <button class="filter-btn active" onclick="filterCards('all')">All</button>
    {"".join('<button class="filter-btn" onclick="filterCards(' + "'" + a + "'" + ')">' + a.replace("_"," ") + '</button>' for a in sorted(set(c['angle'] for c in concepts)))}
  </div>
  <div class="grid" id="grid">{cards}</div>
  <script>
    function filterCards(angle) {{
      document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
      event.target.classList.add('active');
      document.querySelectorAll('.card').forEach(c => {{
        if (angle === 'all' || c.querySelector('.card-angle').textContent.trim() === angle.replace(/_/g, ' ')) {{
          c.style.display = '';
        }} else {{
          c.style.display = 'none';
        }}
      }});
    }}
  </script>
</body></html>"""

        (output_path / "index.html").write_text(html)


# ============================================================
# CAMPAIGN MANAGER
# ============================================================

class CampaignManager:
    """Manages campaigns, tracks concepts, marks winners."""

    def __init__(self, campaign_path):
        self.path = Path(campaign_path)
        if self.path.exists():
            self.data = json.loads(self.path.read_text())
        else:
            self.data = {}

    def save(self):
        self.path.write_text(json.dumps(self.data, indent=2, ensure_ascii=False))

    def add_concepts(self, concepts):
        if "concepts" not in self.data:
            self.data["concepts"] = []
        self.data["concepts"].extend(concepts)
        self.data["last_generated"] = datetime.now().isoformat()
        self.data["total_concepts"] = len(self.data["concepts"])
        self.save()

    def mark_status(self, concept_id, status):
        """Mark a concept as testing/winner/video_candidate/produced."""
        for c in self.data.get("concepts", []):
            if c["id"] == concept_id:
                c["status"] = status
                break
        self.save()

    def update_metrics(self, concept_id, metrics):
        """Update metrics for a concept after running ads."""
        for c in self.data.get("concepts", []):
            if c["id"] == concept_id:
                c["metrics"].update(metrics)
                if metrics.get("clicks") and metrics.get("impressions"):
                    c["metrics"]["ctr"] = round(metrics["clicks"] / metrics["impressions"] * 100, 2)
                break
        self.save()

    def get_winners(self, min_ctr=2.0):
        """Get concepts with CTR above threshold."""
        winners = []
        for c in self.data.get("concepts", []):
            if c["metrics"]["ctr"] >= min_ctr:
                winners.append(c)
        return sorted(winners, key=lambda x: x["metrics"]["ctr"], reverse=True)

    def get_by_angle(self, angle):
        return [c for c in self.data.get("concepts", []) if c["angle"] == angle]

    def get_stats(self):
        concepts = self.data.get("concepts", [])
        if not concepts:
            return {"total": 0}

        by_status = {}
        by_angle = {}
        for c in concepts:
            by_status[c["status"]] = by_status.get(c["status"], 0) + 1
            by_angle[c["angle"]] = by_angle.get(c["angle"], 0) + 1

        return {
            "total": len(concepts),
            "by_status": by_status,
            "by_angle": by_angle,
            "winners": len(self.get_winners()),
        }


# ============================================================
# CLI
# ============================================================

def color(text, code):
    return f"\033[{code}m{text}\033[0m"

def green(t): return color(t, "32")
def yellow(t): return color(t, "33")
def cyan(t): return color(t, "36")
def dim(t): return color(t, "90")
def bold(t): return color(t, "1")


def cmd_generate(args):
    """Generate ad concepts from a campaign config."""
    config_path = args.get("config")
    count = int(args.get("count", 50))

    if not config_path or not Path(config_path).exists():
        print(f"Config not found: {config_path}")
        print("Create one first or use a preset:")
        print("  python3 flood.py preset behike")
        print("  python3 flood.py preset innova-barber")
        print("  python3 flood.py preset hogar-ana-gabriel")
        return

    config = json.loads(Path(config_path).read_text())
    generator = ConceptGenerator(config)
    concepts = generator.generate_concepts(count=count)

    # Save to campaign
    campaign_path = Path(config_path).with_suffix('.campaign.json')
    manager = CampaignManager(campaign_path)
    manager.add_concepts(concepts)

    print(cyan(f"\n{'='*50}"))
    print(cyan(f"  CREATIVE FLOODING - {config['business']['name']}"))
    print(cyan(f"{'='*50}"))
    print(f"\n  Generated: {green(str(len(concepts)))} concepts")
    print(f"  Angles used: {green(str(len(set(c['angle'] for c in concepts))))}")
    print(f"  Pain points: {green(str(len(set(c['pain_point'] for c in concepts))))}")
    print(f"  Campaign: {dim(str(campaign_path))}")

    print(f"\n  {bold('Sample concepts:')}\n")
    for c in concepts[:5]:
        print(f"  {cyan(c['id'])} [{dim(c['angle'])}]")
        print(f"    {bold(c['headline'])}")
        print(f"    {dim(c['body'][:100])}...")
        print()

    print(f"  Next: python3 flood.py render --campaign {campaign_path}")


def cmd_render(args):
    """Render concepts to HTML static ads."""
    campaign_path = args.get("campaign")
    output_dir = args.get("output", "output/default")
    size = args.get("size", "feed_square")
    style = args.get("style", "dark")

    if not campaign_path or not Path(campaign_path).exists():
        print("Campaign file not found. Generate concepts first.")
        return

    campaign = json.loads(Path(campaign_path).read_text())
    concepts = campaign.get("concepts", [])

    if not concepts:
        print("No concepts in campaign. Generate first.")
        return

    renderer = StaticAdRenderer()
    rendered = renderer.render_all(concepts, output_dir, size=size, style=style)

    print(cyan(f"\n  Rendered {green(str(len(rendered)))} ad concepts"))
    print(f"  Output: {dim(output_dir)}")
    print(f"  Index: {green(output_dir + '/index.html')}")
    print(f"\n  Open: open {output_dir}/index.html")


def cmd_stats(args):
    """Show campaign statistics."""
    campaign_path = args.get("campaign")
    if not campaign_path or not Path(campaign_path).exists():
        # List all campaigns
        campaigns = list(CAMPAIGNS_DIR.glob("*.campaign.json"))
        if not campaigns:
            print("No campaigns found. Generate some first.")
            return
        print(cyan("\n  Campaigns:"))
        for cp in campaigns:
            data = json.loads(cp.read_text())
            print(f"  {green(cp.stem.replace('.campaign',''))}: {data.get('total_concepts', 0)} concepts")
        return

    manager = CampaignManager(campaign_path)
    stats = manager.get_stats()

    print(cyan(f"\n  Campaign Stats"))
    print(f"  Total concepts: {green(str(stats['total']))}")
    if stats.get("by_status"):
        print(f"\n  By status:")
        for s, n in stats["by_status"].items():
            print(f"    {s}: {n}")
    if stats.get("by_angle"):
        print(f"\n  By angle:")
        for a, n in sorted(stats["by_angle"].items(), key=lambda x: -x[1]):
            print(f"    {a}: {n}")


def cmd_preset(args):
    """Create a preset campaign config."""
    preset = args.get("name", "")

    presets = {
        "behike": {
            "business": {
                "name": "Behike",
                "url": "https://behike.gumroad.com",
                "default_cta": "Get the Blueprint"
            },
            "products": [
                {"name": "Solopreneur Starter (FREE)", "price": "Free", "url": "https://behike.gumroad.com/l/starter", "cta": "Download Free"},
                {"name": "E-Commerce Blueprint", "price": "$19.99", "url": "https://behike.gumroad.com/l/ecommerce", "cta": "Get Blueprint"},
                {"name": "AI Agency Blueprint", "price": "$19.99", "url": "https://behike.gumroad.com/l/ai-agency", "cta": "Get Blueprint"},
                {"name": "Freelancer Blueprint", "price": "$19.99", "url": "https://behike.gumroad.com/l/freelancer", "cta": "Get Blueprint"},
                {"name": "Content Creator Blueprint", "price": "$19.99", "url": "https://behike.gumroad.com/l/content-creator", "cta": "Get Blueprint"},
                {"name": "Behike OS", "price": "$97", "url": "https://behike.gumroad.com/l/behike-os", "cta": "Get the System"},
                {"name": "Claude Code for Builders", "price": "$9.99", "url": "https://behike.gumroad.com/l/claude-code", "cta": "Start Building"},
                {"name": "First Dollar Guide", "price": "$4.99", "url": "https://behike.gumroad.com/l/first-dollar", "cta": "Make Your First Dollar"},
            ],
            "customer": {
                "identity": "ADHD builder with 47 ideas and zero launches",
                "behavior": "starts 10 things, finishes none",
                "age": "20-30",
                "location": "US/LATAM",
                "budget": "$5-20 impulse buys"
            },
            "pain_points": [
                "too many ideas, no system to execute",
                "watched 200 hours of YouTube, still no revenue",
                "can't focus long enough to finish anything",
                "every course was 40 hours of fluff",
                "feels behind because everyone else seems to be winning",
                "has a laptop and wifi but nothing launched",
                "tried dropshipping, freelancing, content — nothing stuck",
                "smart but can't organize thoughts into action",
                "knows AI exists but hasn't found the right tool",
                "doesn't know how to code but wants to build things"
            ],
            "differentiators": [
                "100+ products built in 2 weeks",
                "one-page system, not a 40-hour course",
                "fill-in blueprint, not theory",
                "built for ADHD brains",
                "built by someone who uses Claude Code 8+ hours a day",
                "dark theme PDF, print it or use in GoodNotes",
                "Hormozi-style: no fluff, just systems"
            ],
            "proof_points": [
                "100+ products built in 14 days",
                "28 products ready to sell",
                "11 live on Gumroad right now",
                "Built with zero coding experience",
                "ADHD brain, still shipped"
            ],
            "offers": [
                {"text": "FREE", "product": "Solopreneur Starter"},
                {"text": "$4.99 — less than coffee", "product": "First Dollar Guide"},
                {"text": "LAUNCH WEEK: $19.99", "product": "Any Blueprint"},
                {"text": "BUNDLE: All Blueprints $49", "product": "Blueprint Bundle"},
            ]
        },
        "innova-barber": {
            "business": {
                "name": "Innova Barber Studio",
                "url": "https://booksy.com/en-us/51293_luis-anexis-innova-barber_barber-shop_107016_morovis",
                "default_cta": "Reserva Tu Cita"
            },
            "products": [
                {"name": "Corte", "price": "$25", "cta": "Reservar"},
                {"name": "Corte + Barba", "price": "$30", "cta": "Reservar"},
                {"name": "Color Platinado", "price": "$125", "cta": "Reservar"},
                {"name": "Color Fantasia", "price": "$100", "cta": "Reservar"},
                {"name": "Fusion de Colores", "price": "$150", "cta": "Reservar"},
            ],
            "customer": {
                "identity": "hombre que quiere verse bien",
                "behavior": "se corta el pelo cada 2-3 semanas",
                "age": "18-40",
                "location": "Morovis, PR area"
            },
            "pain_points": [
                "tu barbero actual no te escucha",
                "siempre sales con un corte que no pediste",
                "el fade nunca queda bien",
                "quieres probar color pero no confias en cualquiera",
                "llegas sin cita y esperas 2 horas",
                "buscas un barbero que entienda tu estilo",
                "quieres que tu hijo salga fresh tambien",
                "cada vez que cambias de barbero es una loteria"
            ],
            "differentiators": [
                "20+ anos de experiencia",
                "186 resenas 5 estrellas en Booksy",
                "especialista en color fantasia y disenos custom",
                "reserva online, sin espera",
                "Morovis, PR — EST 2018"
            ],
            "proof_points": [
                "186 resenas, todas 5 estrellas",
                "100% recomendado en Booksy",
                "20+ anos cortando pelo",
                "Abriendo segunda localidad"
            ],
            "offers": [
                {"text": "Reserva online", "product": "Booksy"},
                {"text": "Corte + Barba $30", "product": "Combo"},
            ]
        },
        "hogar-ana-gabriel": {
            "business": {
                "name": "Hogar Ana Gabriel",
                "url": "tel:+17875014445",
                "default_cta": "Llamar Ahora"
            },
            "products": [
                {"name": "Vivienda Asistida 24/7", "cta": "Informacion"},
                {"name": "Segunda Localidad (Proximamente)", "cta": "Reserva Tu Espacio"},
            ],
            "customer": {
                "identity": "hijo/a adulto buscando cuidado para su padre/madre",
                "behavior": "investiga hogares, visita varios, toma meses para decidir",
                "age": "35-60",
                "location": "Ciales, PR area"
            },
            "pain_points": [
                "culpa por no poder cuidar a tu familiar tu mismo",
                "miedo de que no lo traten bien",
                "no quieres que este solo todo el dia",
                "has visto hogares frios y sin vida",
                "no sabes si puedes confiar en desconocidos",
                "tu familiar necesita atencion que tu no puedes darle",
                "buscas un lugar que se sienta como hogar, no como hospital",
                "te preocupa la calidad de la comida y el cuidado diario"
            ],
            "differentiators": [
                "era la casa de nuestros propios abuelos",
                "ambiente familiar, no institucional",
                "100% recomendado en Facebook",
                "2.7K seguidores",
                "siempre abierto 24/7",
                "actividades recreativas diarias",
                "comida casera puertorriquena",
                "abriendo segunda localidad"
            ],
            "proof_points": [
                "100% recomendado (9 resenas perfectas)",
                "2.7K seguidores en Facebook",
                "La casa de nuestros abuelos — no es marketing, es real",
                "Abriendo segunda localidad por la demanda"
            ],
            "offers": [
                {"text": "Visita sin compromiso", "product": "Tour"},
                {"text": "Espacios limitados — segunda localidad", "product": "Nueva sede"},
            ]
        }
    }

    if preset not in presets:
        print(f"Available presets: {', '.join(presets.keys())}")
        return

    config = presets[preset]
    config_path = CAMPAIGNS_DIR / f"{preset}.json"
    config_path.write_text(json.dumps(config, indent=2, ensure_ascii=False))
    print(green(f"\n  Preset saved: {config_path}"))
    print(f"  Next: python3 flood.py generate --config {config_path} --count 50")


def cmd_list(args):
    """List all campaigns and presets."""
    print(cyan("\n  Presets available:"))
    print("    behike, innova-barber, hogar-ana-gabriel")
    print(f"\n  Create: python3 flood.py preset <name>")

    configs = list(CAMPAIGNS_DIR.glob("*.json"))
    campaigns = [c for c in configs if ".campaign." not in c.name]
    active = [c for c in configs if ".campaign." in c.name]

    if campaigns:
        print(cyan(f"\n  Configs ({len(campaigns)}):"))
        for c in campaigns:
            print(f"    {c.name}")

    if active:
        print(cyan(f"\n  Active campaigns ({len(active)}):"))
        for c in active:
            data = json.loads(c.read_text())
            n = data.get("total_concepts", 0)
            print(f"    {c.stem.replace('.campaign','')}: {n} concepts")


def main():
    if len(sys.argv) < 2:
        print(cyan("""
  Creative Flooding System — Behike
  ==================================

  Usage:
    python3 flood.py preset <name>                    Create campaign config
    python3 flood.py generate --config <path> [--count N]  Generate N concepts
    python3 flood.py render --campaign <path> [--style dark|light|warm] [--size feed_square|story|landscape]
    python3 flood.py stats [--campaign <path>]        Show campaign stats
    python3 flood.py list                             List campaigns

  Quick start:
    python3 flood.py preset behike
    python3 flood.py generate --config campaigns/behike.json --count 50
    python3 flood.py render --campaign campaigns/behike.campaign.json
    open output/default/index.html
        """))
        return

    command = sys.argv[1]
    args = {}

    # Parse args
    i = 2
    while i < len(sys.argv):
        if sys.argv[i].startswith("--"):
            key = sys.argv[i][2:]
            val = sys.argv[i + 1] if i + 1 < len(sys.argv) else ""
            args[key] = val
            i += 2
        else:
            args["name"] = sys.argv[i]
            i += 1

    commands = {
        "generate": cmd_generate,
        "render": cmd_render,
        "stats": cmd_stats,
        "preset": cmd_preset,
        "list": cmd_list,
    }

    if command in commands:
        commands[command](args)
    else:
        print(f"Unknown command: {command}. Use: {', '.join(commands.keys())}")


if __name__ == "__main__":
    main()
