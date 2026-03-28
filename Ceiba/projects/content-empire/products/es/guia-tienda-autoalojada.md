# Crea Tu Tienda Online por $0/Mes

**Por Behike** | $4.99

---

> Copyright 2026 Behike. Todos los derechos reservados. Spanish Edition.
> Esta guia fue escrita con asistencia de IA. El codigo, la arquitectura y la direccion editorial son trabajo original del autor.
> Puedes usar y modificar el codigo para proyectos personales o comerciales. No puedes redistribuir esta guia.

---

## Por Que Autoalojar

Shopify cuesta $39/mes. Eso son $468/ano antes de vender un solo producto. Squarespace cuesta $16/mes. Wix empieza en $17/mes. Hasta plataformas "gratis" como Gumroad se llevan el 10% de cada venta.

Si estas vendiendo productos digitales, plantillas, guias o cursos, no necesitas una plataforma. Necesitas una pagina web y un link de pago.

Una tienda autoalojada es:

- **$0/mes en costos de hosting.** GitHub Pages es gratis. Los tunnels de Cloudflare son gratis. Las laptops viejas son gratis.
- **Sin dependencia de plataformas.** Tus paginas son archivos HTML en tu computadora. Son completamente tuyas.
- **Sin suscripcion mensual desangrando tus margenes.** El unico costo es la comision de Gumroad (10% en el plan gratis, o 5% en el plan de $10/mes cuando escales).
- **Control total del diseno.** Cada pixel es tuyo. Sin limitaciones de plantillas, sin muros de "paga para personalizar".
- **Rapido.** HTML estatico carga en milisegundos. Sin renderizado del lado del servidor, sin consultas a base de datos, sin bloat.

El tradeoff: escribes algo de HTML y CSS. Esta guia te muestra exactamente que escribir.

---

## El Stack

Tres componentes. Nada mas.

### 1. Landing pages en HTML/CSS

Cada producto tiene su propia landing page. Un archivo HTML, autocontenido, sin build tools, sin frameworks. La pagina maneja el pitch: que es el producto, por que alguien deberia comprarlo, que recibe, y un boton para comprar.

### 2. Gumroad para pagos

Gumroad maneja el checkout, procesamiento de pagos, entrega de archivos y reembolsos. Subes tu producto digital a Gumroad, obtienes un link del producto, e incrustas ese link como el boton "Comprar Ahora" en tu landing page.

Por que Gumroad en vez de Stripe directo: Gumroad te da hosting de archivos, emails de entrega, llaves de licencia, manejo de reembolsos y una pagina de checkout. Construir todo eso tu mismo tomaria semanas. La comision del 10% vale la pena hasta que estes generando suficiente para justificar una integracion custom con Stripe.

### 3. Cualquier computadora para hosting

Tus landing pages son HTML estatico. Puedes alojarlas desde:

- Un repositorio de GitHub (gratis, CDN global)
- Una laptop vieja corriendo en un closet
- Tu computadora principal con un tunnel de Cloudflare
- Cualquier VPS barato ($0-5/mes)

La seccion de deployment cubre las tres opciones paso a paso.

---

## Construyendo Tu Pagina de Producto

Cada pagina de producto sigue la misma estructura. Esto no es arbitrario. Es la anatomia de una pagina que convierte visitantes en compradores.

### La estructura

1. **Barra de navegacion** con el nombre de tu marca y un boton CTA
2. **Seccion hero** con el nombre del producto, una descripcion de una linea, el precio y un boton de compra
3. **Seccion Problema-Agitacion-Solucion** que explica por que existe el producto
4. **Stack de valor** listando todo lo incluido
5. **Seccion FAQ** respondiendo objeciones antes de que se conviertan en razones para no comprar
6. **CTA final** repitiendo el boton de compra

### Las variables CSS

Cada pagina usa custom properties de CSS para que puedas cambiar toda la apariencia editando 6 valores:

```css
:root {
    --black: #000000;
    --blue: #0A84FF;
    --light: #F5F5F7;
    --secondary-bg: #1D1D1F;
    --gray: #86868B;
    --font: -apple-system, 'Helvetica Neue', Helvetica, Arial, sans-serif;
}
```

- `--black` es tu color de fondo principal
- `--blue` es tu color de acento/CTA (botones, resaltados, badges)
- `--light` es tu color de texto principal
- `--secondary-bg` es para tarjetas, secciones y fondos alternados
- `--gray` es para texto secundario, etiquetas y contenido atenuado
- `--font` es tu stack de fuentes

Para hacer una pagina con tema claro, intercambia `--black` y `--light`:

```css
:root {
    --black: #FFFFFF;
    --light: #1D1D1F;
    --secondary-bg: #F5F5F7;
    --blue: #0066CC;
    --gray: #6E6E73;
}
```

Ese solo cambio voltea toda la pagina de modo oscuro a claro. Cada elemento hereda de estas variables.

### La seccion hero

```html
<section class="hero">
    <div class="container">
        <span class="hero-badge">NEW RELEASE</span>
        <h1>The Product Name<br><span>In Accent Color</span></h1>
        <p class="hero-sub">One sentence that explains what this product does
        and who it is for.</p>
        <div class="hero-cta-group">
            <a href="https://behike.gumroad.com/l/your-product" class="hero-cta">
                Get It Now - $4.99
            </a>
        </div>
    </div>
</section>
```

El CSS correspondiente:

```css
.hero {
    padding: 120px 0 80px;
    text-align: center;
}

.hero h1 {
    font-size: clamp(36px, 5vw, 56px);
    font-weight: 800;
    line-height: 1.1;
    margin-bottom: 20px;
    color: var(--light);
}

.hero h1 span {
    color: var(--blue);
}

.hero-badge {
    display: inline-block;
    padding: 6px 16px;
    border: 1px solid rgba(10, 132, 255, 0.3);
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.1em;
    color: var(--blue);
    margin-bottom: 24px;
}

.hero-cta {
    display: inline-block;
    padding: 16px 40px;
    background: var(--blue);
    color: #fff;
    text-decoration: none;
    border-radius: 12px;
    font-weight: 700;
    font-size: 18px;
    transition: transform 0.2s, box-shadow 0.2s;
}

.hero-cta:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(10, 132, 255, 0.3);
}
```

La funcion `clamp()` hace el titulo responsive. Escala entre 36px en movil y 56px en escritorio sin media queries.

### La seccion PAS

Problema, Agitacion, Solucion. Este es el motor de persuasion de la pagina.

```html
<section class="pain-section">
    <div class="container">
        <h2>The Problem</h2>
        <p>Describe the pain your buyer is feeling. Be specific.
        "You're spending 2 hours a day writing social media posts by hand"
        is better than "Content creation is hard."</p>

        <h2>Why It Gets Worse</h2>
        <p>Agitate. What happens if they do not solve this?
        "While you're writing captions, your competitors are shipping.
        Every day without a system is a day you fall behind."</p>

        <h2>The Solution</h2>
        <p>Present your product as the fix. Connect it directly to the
        pain you just described. "This pipeline generates 5 posts in 5
        minutes. Same quality. A fraction of the time."</p>
    </div>
</section>
```

### El stack de valor

Lista todo lo incluido. Haz que se sienta como mucho.

```html
<section class="features">
    <div class="container">
        <h2>What You Get</h2>
        <div class="feature-grid">
            <div class="feature-card">
                <h3>The Complete Script</h3>
                <p>400+ lines of production Python code, fully commented.</p>
            </div>
            <div class="feature-card">
                <h3>18 RSS Feed Sources</h3>
                <p>Pre-configured feeds from every major AI news outlet.</p>
            </div>
            <div class="feature-card">
                <h3>Impact Scoring System</h3>
                <p>Keyword-based scoring that surfaces what matters.</p>
            </div>
            <div class="feature-card">
                <h3>HTML Digest Generator</h3>
                <p>Dark-themed, styled digest you can read in a browser.</p>
            </div>
        </div>
    </div>
</section>
```

```css
.feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 20px;
    margin-top: 40px;
}

.feature-card {
    background: var(--secondary-bg);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 32px;
}

.feature-card h3 {
    font-size: 20px;
    font-weight: 700;
    color: var(--light);
    margin-bottom: 8px;
}

.feature-card p {
    font-size: 15px;
    color: var(--gray);
    line-height: 1.6;
}
```

### El FAQ

Maneja las objeciones de forma proactiva:

```html
<section class="faq">
    <div class="container">
        <h2>Common Questions</h2>
        <div class="faq-item">
            <h3>Do I need to know Python?</h3>
            <p>Basic familiarity helps, but the guide walks through every
            step. If you can copy-paste into a terminal, you can follow along.</p>
        </div>
        <div class="faq-item">
            <h3>What if I want a refund?</h3>
            <p>Full refund within 30 days, no questions asked.</p>
        </div>
    </div>
</section>
```

---

## El Widget de Configuracion

Este es un widget JavaScript que agrega cambio de temas y controles de tamano de fuente a cualquier landing page. Agregalo y tus visitantes pueden personalizar su experiencia de lectura.

### Que hace

- 8 temas de color: Midnight, Snow, Ocean, Sunset, Forest, Royal, Ember, Candy
- 4 tamanos de fuente: S, M, L, XL
- Guarda preferencias en localStorage (persiste entre visitas)
- Boton de engranaje flotante en la esquina inferior derecha
- Panel que se desliza hacia arriba con puntos de tema y botones de tamano

### Agregarlo a tu pagina

Un script tag al final de tu HTML, antes de `</body>`:

```html
<script src="settings-widget.js"></script>
```

Eso es todo. El widget crea su propio HTML, inyecta su propio CSS y agrega sus propios event listeners. Es completamente autocontenido.

### Como funcionan los temas

Cada tema es un objeto JavaScript con valores de color:

```javascript
const themes = {
    midnight: {
        name: 'Midnight',
        black: '#000000',
        accent: '#0A84FF',
        light: '#F5F5F7',
        secondaryBg: '#1D1D1F',
        gray: '#86868B',
        navBg: 'rgba(0,0,0,0.8)',
        cardBg: 'rgba(29,29,31,0.6)',
        border: 'rgba(245,245,247,0.08)',
    },
    snow: {
        name: 'Snow',
        black: '#FFFFFF',
        accent: '#0066CC',
        light: '#1D1D1F',
        secondaryBg: '#F5F5F7',
        gray: '#6E6E73',
        navBg: 'rgba(255,255,255,0.85)',
        cardBg: 'rgba(245,245,247,0.8)',
        border: 'rgba(0,0,0,0.08)',
    },
    // ... 6 more themes
};
```

Cuando un visitante hace clic en un punto de tema, la funcion `applyTheme` actualiza las custom properties de CSS en el root del documento:

```javascript
function applyTheme(key) {
    const t = themes[key];
    const r = document.documentElement.style;
    r.setProperty('--black', t.black);
    r.setProperty('--blue', t.accent);
    r.setProperty('--light', t.light);
    r.setProperty('--secondary-bg', t.secondaryBg);
    r.setProperty('--gray', t.gray);
    localStorage.setItem('behike-theme', key);
}
```

Como tu pagina usa variables CSS para todos los colores, una sola llamada a funcion repinta la pagina entera al instante. Sin recargar la pagina.

### Escalado de tamano de fuente

El sistema de tamano de fuente usa un multiplicador de escala en el tamano de fuente root:

```javascript
const fontSizes = {
    small:  { label: 'S',  scale: 0.85 },
    medium: { label: 'M',  scale: 1.0 },
    large:  { label: 'L',  scale: 1.15 },
    xl:     { label: 'XL', scale: 1.3 },
};

function applyFontSize(key) {
    const s = fontSizes[key];
    document.documentElement.style.fontSize = (16 * s.scale) + 'px';
    localStorage.setItem('behike-fontsize', key);
}
```

Si tu pagina usa unidades `rem` para tamanos de fuente, todo escala proporcionalmente. La base es 16px en "M", 13.6px en "S", 18.4px en "L" y 20.8px en "XL".

### Haciendo tu pagina compatible

Para que el widget funcione correctamente con tu pagina, sigue dos reglas:

1. Usa custom properties de CSS (`--black`, `--blue`, `--light`, `--secondary-bg`, `--gray`) para todos los colores
2. Usa unidades `rem` para tamanos de fuente donde sea posible

Si tu pagina ya sigue estas convenciones, el widget funciona inmediatamente con cero configuracion.

---

## Desplegarlo

Tres opciones, todas gratis. Escoge la que se adapte a tu setup.

### Opcion A: GitHub Pages (recomendado para principiantes)

GitHub Pages te da hosting gratis con CDN global. Tu sitio carga rapido desde cualquier parte del mundo.

**Paso 1:** Crea una cuenta de GitHub en github.com si no tienes una.

**Paso 2:** Crea un nuevo repositorio. Ponle el nombre que quieras. Hazlo publico.

**Paso 3:** Sube tus archivos HTML al repositorio. Puedes arrastrar y soltar archivos directamente en la interfaz web de GitHub, o usar git desde la terminal:

```bash
cd ~/my-store
git init
git add .
git commit -m "Initial store pages"
git remote add origin https://github.com/yourusername/your-repo.git
git push -u origin main
```

**Paso 4:** Activa GitHub Pages. Ve a Settings de tu repositorio, baja hasta Pages, y configura la fuente como "Deploy from a branch", branch "main", carpeta "/ (root)".

**Paso 5:** Tu sitio esta en vivo en `https://yourusername.github.io/your-repo/`. Cada archivo HTML es accesible en su propia URL. Si tu pagina de producto es `ai-tracker-guide.html`, la URL es `https://yourusername.github.io/your-repo/ai-tracker-guide.html`.

**Paso 6 (opcional):** Conecta un dominio custom. En la configuracion de Pages, ingresa tu nombre de dominio. Luego agrega un registro CNAME en tu proveedor de DNS apuntando a `yourusername.github.io`. GitHub maneja SSL automaticamente.

Tiempo total: 10 minutos. Costo: $0.

### Opcion B: Laptop vieja como servidor casero

Si tienes una laptop vieja, un Raspberry Pi, o cualquier computadora que no estes usando, puede servir tu tienda 24/7.

**Paso 1:** Instala un servidor web simple. Python tiene uno integrado:

```bash
cd ~/my-store
python3 -m http.server 8080
```

Esto sirve tus archivos HTML en el puerto 8080. Visita `http://localhost:8080` para ver tu tienda.

Para algo mas robusto, instala Caddy:

```bash
# macOS
brew install caddy

# Linux
sudo apt install caddy
```

Crea un `Caddyfile`:

```
:8080 {
    root * /path/to/your/store
    file_server
}
```

Ejecutalo:

```bash
caddy run
```

**Paso 2:** Mantenlo corriendo. En macOS, usa `caffeinate` para prevenir el modo de suspension:

```bash
caffeinate -s caddy run
```

En Linux, crea un servicio de systemd:

```bash
sudo tee /etc/systemd/system/store.service << 'EOF'
[Unit]
Description=Product Store
After=network.target

[Service]
ExecStart=/usr/bin/caddy run --config /path/to/Caddyfile
WorkingDirectory=/path/to/your/store
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable store
sudo systemctl start store
```

**Paso 3:** Hazlo accesible desde internet usando Cloudflare Tunnel (ver Opcion C abajo).

### Opcion C: Cloudflare Tunnel a tu computadora

Cloudflare Tunnel expone un servidor web local a internet a traves de una conexion segura. Sin port forwarding, sin IP estatica requerida, sin cambios de firewall.

**Paso 1:** Crea una cuenta gratis de Cloudflare en cloudflare.com.

**Paso 2:** Agrega tu dominio a Cloudflare y actualiza tus nameservers (Cloudflare te guia paso a paso).

**Paso 3:** Instala cloudflared:

```bash
# macOS
brew install cloudflare/cloudflare/cloudflared

# Linux
sudo apt install cloudflared
```

**Paso 4:** Autenticate:

```bash
cloudflared tunnel login
```

Esto abre una ventana del navegador. Selecciona tu dominio y autoriza.

**Paso 5:** Crea un tunnel:

```bash
cloudflared tunnel create my-store
```

**Paso 6:** Configura el tunnel. Crea `~/.cloudflared/config.yml`:

```yaml
tunnel: YOUR_TUNNEL_ID
credentials-file: /path/to/.cloudflared/YOUR_TUNNEL_ID.json

ingress:
  - hostname: store.yourdomain.com
    service: http://localhost:8080
  - service: http_status:404
```

**Paso 7:** Agrega un registro DNS:

```bash
cloudflared tunnel route dns my-store store.yourdomain.com
```

**Paso 8:** Inicia el tunnel:

```bash
cloudflared tunnel run my-store
```

Tu tienda esta en vivo en `https://store.yourdomain.com`. Cloudflare maneja SSL, proteccion DDoS y cache. Gratis.

Para mantenerlo corriendo permanentemente, configura cloudflared como servicio del sistema:

```bash
# macOS
sudo cloudflared service install

# Linux
sudo cloudflared service install
sudo systemctl enable cloudflared
sudo systemctl start cloudflared
```

### Cual opcion escoger

- **GitHub Pages** si quieres cero mantenimiento y no te importa la URL de `github.io` (o ya tienes un dominio custom)
- **Laptop vieja + Cloudflare Tunnel** si tienes hardware disponible y quieres control total
- **Cloudflare Tunnel en tu computadora principal** si solo estas probando y quieres salir en vivo rapido

Las tres opciones cuestan $0/mes. Las tres sirven HTML estatico lo suficientemente rapido para cualquier nivel de trafico que vayas a ver como creador independiente.

---

**La matematica es simple. Shopify cobra $468/ano. Este setup cobra $0/ano. Si vendes 94 copias de un producto de $4.99 en Shopify, los primeros $468 van para Shopify. Con autoalojamiento, esos $468 se quedan en tu bolsillo. Cada venta despues de esa, la misma historia.**

---

*Construido por Behike. Tu tienda. Tus margenes.*
