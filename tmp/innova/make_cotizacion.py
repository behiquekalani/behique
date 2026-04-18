"""
Innova Barber — Cotización Anual
Generates a WhatsApp-ready pricing card in PR Spanish.
Design: dark bg, gold accent, clean typography.
Output: 1080x1350 PNG.
"""
from PIL import Image, ImageDraw, ImageFont

# Canvas
W, H = 1080, 1520
BG = (13, 13, 15)
CARD = (22, 22, 26)
GOLD = (212, 175, 55)
GOLD_SOFT = (184, 148, 40)
WHITE = (245, 245, 245)
MUTED = (140, 140, 148)
GREEN = (80, 200, 120)
STRIKE = (110, 110, 118)
DIVIDER = (45, 45, 52)

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

# Fonts
F = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FS = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"

def font(path, size):
    return ImageFont.truetype(path, size)

# Header strip (gold)
d.rectangle([(0, 0), (W, 8)], fill=GOLD)

# Brand header
y = 70
d.text((W//2, y), "INNOVA BARBER STUDIO", font=font(FS, 44), fill=GOLD, anchor="mm")
y += 55
d.text((W//2, y), "Cotización Anual · Servicios Web", font=font(F, 26), fill=MUTED, anchor="mm")
y += 50
d.text((W//2, y), "────────────────", font=font(F, 20), fill=GOLD_SOFT, anchor="mm")

# Intro line
y += 60
d.text((W//2, y), "Hermano, esto es todo lo que incluye", font=font(F, 28), fill=WHITE, anchor="mm")
y += 36
d.text((W//2, y), "tu servicio — y lo que cuesta en el mercado:", font=font(F, 28), fill=WHITE, anchor="mm")

# Services table
services = [
    ("Diseño y desarrollo del website",          "$800"),
    ("Dominio .com (renovación anual incluida)", "$20"),
    ("Hosting del servidor (24/7)",               "$120"),
    ("Seguridad Cloudflare + SSL",                "$60"),
    ("SEO — rankeado #1 en 'barbero Morovis'",    "$600"),
    ("Integración con Booksy",                    "$80"),
    ("Google Maps + info del negocio",            "$50"),
    ("Mantenimiento y cambios ilimitados",        "$400"),
    ("Cambios de diseño / tema cuando quieras",   "$200"),
]

# Card background
card_top = y + 60
card_bottom = card_top + 50 + (len(services) * 62) + 90
d.rounded_rectangle([(50, card_top), (W-50, card_bottom)], radius=24, fill=CARD, outline=GOLD_SOFT, width=2)

# Card header
ch_y = card_top + 40
d.text((90, ch_y), "SERVICIO", font=font(FB, 22), fill=GOLD, anchor="lm")
d.text((W-90, ch_y), "VALOR MERCADO", font=font(FB, 22), fill=GOLD, anchor="rm")
d.line([(90, ch_y + 30), (W-90, ch_y + 30)], fill=DIVIDER, width=2)

row_y = ch_y + 60
for name, price in services:
    d.text((90, row_y), "✓", font=font(FB, 26), fill=GREEN, anchor="lm")
    d.text((130, row_y), name, font=font(F, 24), fill=WHITE, anchor="lm")
    d.text((W-90, row_y), price, font=font(FB, 26), fill=STRIKE, anchor="rm")
    # Strike-through on price
    bbox = d.textbbox((W-90, row_y), price, font=font(FB, 26), anchor="rm")
    d.line([(bbox[0]-2, (bbox[1]+bbox[3])//2), (bbox[2]+2, (bbox[1]+bbox[3])//2)], fill=STRIKE, width=2)
    row_y += 62

# Total mercado row
row_y += 10
d.line([(90, row_y - 18), (W-90, row_y - 18)], fill=DIVIDER, width=2)
d.text((90, row_y + 14), "Valor total de mercado:", font=font(FB, 26), fill=MUTED, anchor="lm")
d.text((W-90, row_y + 14), "$2,330 / año", font=font(FB, 28), fill=STRIKE, anchor="rm")

# Your price block
yp_top = card_bottom + 50
yp_bottom = yp_top + 280
d.rounded_rectangle([(50, yp_top), (W-50, yp_bottom)], radius=24, fill=GOLD, outline=GOLD, width=2)

d.text((W//2, yp_top + 45), "TU PRECIO", font=font(FB, 28), fill=(13,13,15), anchor="mm")
d.text((W//2, yp_top + 115), "$300 / año", font=font(FS, 82), fill=(13,13,15), anchor="mm")
d.text((W//2, yp_top + 185), "($30/mes · pagas anual y ahorras $60)", font=font(F, 24), fill=(40,40,45), anchor="mm")
d.text((W//2, yp_top + 230), "Menos de $1 al día — todo incluido", font=font(FB, 24), fill=(13,13,15), anchor="mm")

# Footer note
fy = yp_bottom + 55
d.text((W//2, fy), "Pagas una vez al año y te olvidas de to'.", font=font(F, 26), fill=WHITE, anchor="mm")
d.text((W//2, fy + 38), "Yo me encargo del website, cambios, dominio,", font=font(F, 24), fill=MUTED, anchor="mm")
d.text((W//2, fy + 70), "hosting, seguridad y SEO. Tú enfócate en cortar.", font=font(F, 24), fill=MUTED, anchor="mm")

# Bottom gold strip
d.rectangle([(0, H-8), (W, H)], fill=GOLD)

out = "/home/user/behique/tmp/innova/innova_cotizacion.png"
img.save(out, "PNG", quality=95)
print(f"Saved: {out}")
print(f"Size: {W}x{H}")
