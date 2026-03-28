# Construye Tu Propio Rastreador de Noticias de IA en Python

**Por Behike** | $4.99

---

> Copyright 2026 Behike. Todos los derechos reservados. Spanish Edition.
> Esta guia fue escrita con asistencia de IA. El codigo, la arquitectura y la direccion editorial son trabajo original del autor.
> Puedes usar y modificar el codigo para proyectos personales o comerciales. No puedes redistribuir esta guia.

---

## Lo Que Vas a Construir

La mayoria de la gente consume noticias de IA de forma pasiva. Scrollean Twitter, ojean titulares y se pierden las historias que realmente importan.

Tu vas a construir algo mejor: un agregador de feeds RSS que jala noticias de 18+ fuentes, puntua cada articulo por impacto de mercado, rastrea personas y empresas clave, y genera un resumen diario que puedes leer en 2 minutos.

Piensa en ello como un calendario economico de ForexFactory, pero para IA. Cada historia recibe una calificacion: HIGH, MEDIUM o LOW. Las historias sobre adquisiciones multimillonarias y lanzamientos de modelos flotan hacia arriba. Los listicles de "10 Tips para Prompt Engineering" se hunden al fondo.

Esto es lo que hace la herramienta terminada:

- Jala articulos de TechCrunch, The Verge, Ars Technica, Hacker News, MIT Tech Review, OpenAI Blog, Anthropic News, Google AI Blog, NVIDIA Blog, VentureBeat, y 8 subreddits
- Puntua cada articulo usando keyword matching (impacto HIGH, MEDIUM, LOW)
- Rastrea menciones de personas como Sam Altman, Jensen Huang y Dario Amodei
- Genera resumenes en texto o HTML ordenados por impacto
- Almacena 30 dias de articulos en JSON para busqueda y analisis
- Se ejecuta desde la linea de comandos con flags simples

Tiempo total de setup: unos 10 minutos.

### Por que construir esto en vez de usar Google Alerts o Feedly

Google Alerts es reactivo. Recibes un email horas (a veces dias) despues de que algo pasa. Feedly es un lector, no un evaluador. Todavia tienes que decidir manualmente que importa.

Este rastreador es opinionado. Asigna puntuaciones de impacto en el momento que llega un articulo. Cuando NVIDIA saca un nuevo chip u OpenAI despide a alguien, la historia salta al tope automaticamente. Abres el resumen y lo primero que ves es lo mas importante que paso.

El sistema de puntuacion tambien es personalizable. Google Alerts no tiene concepto de "alto impacto" versus "bajo impacto". Este rastreador si, y tu controlas la definicion de cada nivel editando una lista de keywords.

Finalmente, todo se queda local. Sin cuentas, sin API keys, sin dependencias de la nube. Tus articulos viven en un archivo JSON en tu maquina. Buscalos, analizalos, pasa los datos a otras herramientas. Tu eres dueno de los datos.

---

## Setup (10 Minutos)

### Requisitos

- Python 3.8 o mas reciente (verifica con `python3 --version`)
- Una libreria externa: `feedparser`

### Paso 1: Instalar feedparser

```bash
pip install feedparser
```

Esa es la unica dependencia. El resto es libreria estandar.

### Paso 2: Crear la estructura del proyecto

```bash
mkdir -p ~/ai-tracker
cd ~/ai-tracker
touch ai_news_tracker.py
```

### Paso 3: Configurar tus feeds RSS

La lista de feeds es una simple lista de diccionarios en Python. Cada feed tiene un nombre, URL y categoria. Aqui tienes un set inicial:

```python
FEEDS = [
    {"name": "TechCrunch AI", "url": "https://techcrunch.com/category/artificial-intelligence/feed/", "category": "ai"},
    {"name": "The Verge AI", "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml", "category": "ai"},
    {"name": "Ars Technica", "url": "https://feeds.arstechnica.com/arstechnica/technology-lab", "category": "tech"},
    {"name": "Hacker News Best", "url": "https://hnrss.org/best?q=AI+OR+LLM+OR+GPT+OR+Claude+OR+NVIDIA", "category": "ai"},
    {"name": "OpenAI Blog", "url": "https://openai.com/blog/rss.xml", "category": "releases"},
    {"name": "Anthropic News", "url": "https://www.anthropic.com/news/rss.xml", "category": "releases"},
    {"name": "Google AI Blog", "url": "https://blog.google/technology/ai/rss/", "category": "releases"},
    {"name": "NVIDIA Blog", "url": "https://blogs.nvidia.com/feed/", "category": "hardware"},
    {"name": "VentureBeat AI", "url": "https://venturebeat.com/category/ai/feed/", "category": "ai"},
    {"name": "r/MachineLearning", "url": "https://www.reddit.com/r/MachineLearning/hot.rss", "category": "research"},
    {"name": "r/LocalLLaMA", "url": "https://www.reddit.com/r/LocalLLaMA/hot.rss", "category": "ai"},
    {"name": "r/artificial", "url": "https://www.reddit.com/r/artificial/hot.rss", "category": "ai"},
]
```

Las categorias te ayudan a filtrar despues. Usa las etiquetas que tengan sentido para tu flujo de trabajo: `ai`, `tech`, `releases`, `hardware`, `research`, `business`.

Para agregar un nuevo feed, simplemente agrega otro diccionario a la lista. Cualquier URL valida de RSS o Atom funciona.

### Paso 4: Configurar el almacenamiento

El rastreador almacena todo en archivos JSON. No se necesita base de datos. Define tus rutas al inicio del script:

```python
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
ARTICLES_FILE = DATA_DIR / "articles.json"
TRACKED_FILE = DATA_DIR / "tracked.json"
DIGEST_DIR = DATA_DIR / "digests"
```

Luego crea una funcion de setup:

```python
def ensure_dirs():
    """Create data directories if they don't exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    DIGEST_DIR.mkdir(parents=True, exist_ok=True)
```

Llama a `ensure_dirs()` al inicio de tu funcion main. La primera vez que corras el script, crea la estructura de carpetas automaticamente.

---

## El Sistema de Puntuacion

Aqui es donde el rastreador se vuelve util. En vez de mostrarte 200 articulos en orden cronologico, los rankea por impacto de mercado.

### Como funciona el keyword matching

La funcion de puntuacion toma el titulo y resumen del articulo, convierte todo a minusculas y cuenta cuantos keywords de impacto aparecen.

```python
IMPACT_KEYWORDS = {
    "high": [
        "launch", "release", "announce", "acquire", "billion", "million funding",
        "ipo", "regulation", "ban", "lawsuit", "breakthrough", "open source",
        "gpt-5", "gpt-6", "claude 4", "claude 5", "gemini 2", "llama 4",
        "fired", "resign", "ceo", "arrested", "sec", "ftc", "antitrust",
        "nvidia", "blackwell", "h100", "h200", "b100", "b200",
        "agi", "superintelligence", "safety", "alignment",
        "apple intelligence", "siri", "alexa", "cortana",
    ],
    "medium": [
        "update", "feature", "partnership", "integration", "api",
        "pricing", "model", "benchmark", "performance", "fine-tune",
        "agent", "plugin", "tool", "mcp", "function calling",
        "series a", "series b", "series c", "seed round", "valuation",
        "layoff", "hire", "expansion", "revenue",
    ],
    "low": [
        "tutorial", "guide", "how to", "review", "comparison",
        "opinion", "analysis", "research paper", "arxiv",
        "community", "developer", "conference", "meetup",
    ],
}
```

### La funcion de puntuacion

```python
def score_impact(title, summary=""):
    """Score article impact: HIGH / MEDIUM / LOW."""
    text = f"{title} {summary}".lower()

    high_hits = sum(1 for kw in IMPACT_KEYWORDS["high"] if kw.lower() in text)
    med_hits = sum(1 for kw in IMPACT_KEYWORDS["medium"] if kw.lower() in text)

    if high_hits >= 1:
        return "HIGH", high_hits * 3 + med_hits
    elif med_hits >= 1:
        return "MEDIUM", med_hits * 2
    else:
        return "LOW", 1
```

La puntuacion numerica (segundo valor de retorno) te permite ordenar dentro del mismo nivel de impacto. Un articulo que toca 3 keywords HIGH rankea por encima de uno que toca 1.

### Personalizando los keywords

Esta es la parte mas importante de personalizar. Si trabajas en robotica, agrega keywords como "humanoid", "boston dynamics", "figure", "1x". Si te interesan los modelos open source, agrega "weights released", "apache 2.0", "mit license".

Las listas de keywords son simplemente listas de Python. Editalas libremente.

### Rastreo de entidades

El rastreador tambien vigila menciones de personas y empresas especificas:

```python
DEFAULT_TRACKED = [
    {"name": "Sam Altman", "type": "person", "org": "OpenAI"},
    {"name": "Dario Amodei", "type": "person", "org": "Anthropic"},
    {"name": "Jensen Huang", "type": "person", "org": "NVIDIA"},
    {"name": "OpenAI", "type": "company", "org": "OpenAI"},
    {"name": "Anthropic", "type": "company", "org": "Anthropic"},
    {"name": "NVIDIA", "type": "company", "org": "NVIDIA"},
]

def find_mentions(text, tracked):
    """Find tracked people/companies mentioned in text."""
    mentions = []
    text_lower = text.lower()
    for entity in tracked:
        if entity["name"].lower() in text_lower:
            mentions.append(entity["name"])
    return mentions
```

Cuando un articulo menciona una entidad rastreada, aparece en el resumen con su nombre adjunto. Esto hace facil detectar cuando un CEO hace un movimiento o una empresa lanza un anuncio.

Puedes agregar nuevas entidades desde la linea de comandos:

```bash
python3 ai_news_tracker.py --track "Yann LeCun" --track-type person --track-org Meta
```

---

## Ejecutarlo

### Obtener articulos nuevos

```bash
python3 ai_news_tracker.py --fetch
```

Esto jala de todos los feeds configurados, deduplica contra articulos existentes (usando un hash MD5 de titulo + URL), los puntua y guarda todo en `articles.json`. Los articulos viejos de mas de 30 dias se eliminan automaticamente.

Esto es lo que pasa bajo el capo cuando ejecutas `--fetch`:

1. El script recorre cada feed en tu lista `FEEDS`
2. Para cada feed, parsea el XML del RSS usando feedparser y toma las 15 entradas mas recientes
3. Cada entrada recibe un ID unico generado de su titulo y URL (para que el mismo articulo de diferentes feeds no se cuente dos veces)
4. El titulo y resumen pasan por la funcion de puntuacion de impacto
5. El rastreo de entidades busca menciones de cualquiera en tu lista de rastreados
6. Los articulos nuevos se agregan al archivo JSON existente
7. Los articulos de mas de 30 dias se eliminan para mantener el archivo manejable

La ventana de retencion de 30 dias significa que tu archivo `articles.json` se mantiene por debajo de unos pocos megabytes incluso con 18 feeds corriendo cada hora. Si quieres mantener articulos por mas tiempo, cambia el valor `timedelta(days=30)` en la funcion `fetch_feeds`.

### Ver las historias top por impacto

```bash
python3 ai_news_tracker.py --top 10
```

La salida se ve asi:

```
  [HIGH] NVIDIA Announces Blackwell B300 GPU for AI Training [NVIDIA, Jensen Huang]
         NVIDIA Blog | 2026-03-21
         The new B300 delivers 4x the performance of H100...

  [HIGH] OpenAI Releases GPT-5 with Reasoning Capabilities [OpenAI, Sam Altman]
         TechCrunch AI | 2026-03-21
         The latest model from OpenAI shows significant...

  [MEDIUM] New MCP Integration Connects Claude to Enterprise Tools
           Anthropic News | 2026-03-20
           The model context protocol now supports...
```

Los articulos HIGH se muestran en rojo. MEDIUM en amarillo. LOW en gris. Las menciones de entidades aparecen entre corchetes.

### Generar un resumen diario

Formato texto (se imprime en terminal):

```bash
python3 ai_news_tracker.py --digest
```

Formato HTML (se guarda en archivo, ideal para leer en un navegador):

```bash
python3 ai_news_tracker.py --digest --format html
```

El resumen HTML tiene un tema oscuro, badges de color por impacto, links clickeables y una barra de estadisticas mostrando el total de historias y desglose por nivel de impacto.

### Buscar articulos pasados

```bash
python3 ai_news_tracker.py --search "claude"
python3 ai_news_tracker.py --search "funding"
python3 ai_news_tracker.py --search "regulation"
```

La busqueda compara contra titulo, resumen y menciones de entidades. Los resultados se ordenan por puntuacion de impacto.

### Comportamiento por defecto

Ejecutar el script sin flags hace un fetch + resumen:

```bash
python3 ai_news_tracker.py
```

Este es el comando del dia a dia. Ejecutalo una vez en la manana.

---

## Automatizarlo

### Cron job: buscar cada hora

Abre tu crontab:

```bash
crontab -e
```

Agrega esta linea para buscar articulos nuevos cada hora:

```
0 * * * * /usr/bin/python3 /path/to/ai_news_tracker.py --fetch >> /tmp/news_tracker.log 2>&1
```

### Resumen diario a las 6am

Agrega un segundo cron job:

```
0 6 * * * /usr/bin/python3 /path/to/ai_news_tracker.py --digest --format html --save /path/to/data/digests/daily.html
```

### Script bash para operacion de un solo comando

Crea un archivo llamado `daily_news.sh`:

```bash
#!/bin/bash
# Daily AI News - fetch and generate digest

TRACKER="/path/to/ai_news_tracker.py"
PYTHON="/usr/bin/python3"

echo "Fetching latest AI news..."
$PYTHON $TRACKER --fetch

echo ""
echo "Generating digest..."
$PYTHON $TRACKER --digest

echo ""
echo "Top 5 stories:"
$PYTHON $TRACKER --top 5
```

Hazlo ejecutable:

```bash
chmod +x daily_news.sh
```

Ahora tienes un solo comando para tu rutina de la manana:

```bash
./daily_news.sh
```

### Que hacer con el resumen

El resumen HTML funciona como una pagina web independiente. Abrelo en cualquier navegador. El resumen de texto funciona en una terminal o como cuerpo de un email.

Algunas ideas para usar la salida:

- Reenvia el resumen HTML al canal de Slack de tu equipo
- Usa las historias HIGH como inspiracion de contenido (revisa la guia complementaria sobre como convertir noticias en posts de Instagram)
- Rastrea la frecuencia de menciones de entidades a lo largo del tiempo para detectar tendencias
- Envia el resumen de texto a un sistema de notificaciones

Los datos de articulos son JSON plano. Puedes escribir scripts adicionales para analizarlos, exportar a CSV o pasarlos a otras herramientas. El rastreador es intencionalmente simple. Hace una cosa bien: sacar a la superficie las noticias de IA que importan y esconder el ruido.

---

**Siguientes pasos:** Una vez que tengas un flujo constante de articulos puntuados, revisa "Convierte Feeds RSS en Posts de Instagram con Python" para generar automaticamente contenido de redes sociales a partir de tus historias de mayor impacto.

---

*Construido por Behike. Para builders que quieren senal, no ruido.*
