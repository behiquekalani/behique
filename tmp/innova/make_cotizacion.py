"""
Innova Barber — Cotización Anual (Apple-style + Hormozi copy)
1080x1620 PNG, minimalist dark, single gold accent, value-stack framing.
"""
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1960
BG = (8, 8, 10)
WHITE = (248, 248, 250)
SOFT = (168, 168, 176)
MUTED = (110, 110, 118)
DIM = (70, 70, 78)
GOLD = (212, 175, 55)
LINE = (32, 32, 38)

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

F  = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def font(path, size): return ImageFont.truetype(path, size)

# ---------- HEADER ----------
y = 110
d.text((W//2, y), "INNOVA BARBER STUDIO", font=font(FB, 32), fill=GOLD, anchor="mm")
y += 45
d.line([(W//2 - 40, y), (W//2 + 40, y)], fill=GOLD, width=1)

# ---------- HERO ----------
y += 110
d.text((W//2, y), "Tu barbería online.", font=font(FB, 68), fill=WHITE, anchor="mm")
y += 78
d.text((W//2, y), "Trabajando por ti 24/7.", font=font(FB, 68), fill=WHITE, anchor="mm")
y += 75
d.text((W//2, y), "Por menos de $1 al día.", font=font(F, 32), fill=SOFT, anchor="mm")

# ---------- VALUE STACK ----------
y += 120
d.text((100, y), "TODO LO QUE ESTÁ INCLUIDO", font=font(FB, 20), fill=GOLD, anchor="lm")
y += 20
d.line([(100, y + 15), (W-100, y + 15)], fill=LINE, width=1)

items = [
    ("Website profesional que convierte visitas en clientes",      "$800"),
    ("Rankeado #1 en Google. Los clientes te encuentran solos.",    "$600"),
    ("Mantenimiento y cambios ilimitados todo el año",              "$400"),
    ("Rediseño de tema cuando lo necesites",                        "$200"),
    ("Hosting 24/7 rápido y sin caídas",                            "$120"),
    ("Integración con Booksy para reservas automáticas",            "$80"),
    ("Protección Cloudflare contra hackers y ataques",              "$60"),
    ("Presencia en Google Maps con dirección y horarios",           "$50"),
    ("Dominio innovabarberpr.shop con renovación anual",            "$20"),
]

y += 50
for title, price in items:
    d.text((100, y), title, font=font(F, 24), fill=WHITE, anchor="lm")
    d.text((W-100, y), price, font=font(FB, 24), fill=SOFT, anchor="rm")
    y += 30
    d.line([(100, y), (W-100, y)], fill=LINE, width=1)
    y += 30

# ---------- VALUE TOTAL ----------
y += 20
d.text((100, y), "Valor total en el mercado", font=font(F, 26), fill=MUTED, anchor="lm")
total_txt = "$2,330 / año"
d.text((W-100, y), total_txt, font=font(FB, 30), fill=MUTED, anchor="rm")
bbox = d.textbbox((W-100, y), total_txt, font=font(FB, 30), anchor="rm")
d.line([(bbox[0]-4, (bbox[1]+bbox[3])//2), (bbox[2]+4, (bbox[1]+bbox[3])//2)], fill=MUTED, width=2)

# ---------- PRICE REVEAL ----------
y += 100
d.text((W//2, y), "TU INVERSIÓN", font=font(FB, 22), fill=GOLD, anchor="mm")
y += 90
d.text((W//2, y), "$300", font=font(FB, 180), fill=WHITE, anchor="mm")
y += 120
d.text((W//2, y), "por todo el año", font=font(F, 32), fill=SOFT, anchor="mm")

y += 70
d.text((W//2, y), "Ahorras $2,030.  Un solo pago.  Cero preocupaciones.", font=font(FB, 22), fill=GOLD, anchor="mm")

# ---------- CLOSE ----------
y += 90
d.line([(W//2 - 60, y), (W//2 + 60, y)], fill=LINE, width=1)
y += 60
d.text((W//2, y), "Tú te enfocas en cortar.", font=font(F, 26), fill=WHITE, anchor="mm")
y += 38
d.text((W//2, y), "Del website me encargo yo.", font=font(F, 26), fill=WHITE, anchor="mm")

# ---------- UPGRADE NOTE ----------
y += 70
d.text((W//2, y), "Opcional: upgrade a dominio .com disponible (costo adicional).",
       font=font(F, 18), fill=DIM, anchor="mm")

out = "/home/user/behique/tmp/innova/innova_cotizacion.png"
img.save(out, "PNG", quality=95)
print(f"Saved: {out}  ({W}x{H})")
