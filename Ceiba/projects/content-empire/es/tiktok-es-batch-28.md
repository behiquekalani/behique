# TikTok Scripts en Español — Batch 28
# Tema: n8n automatizacion para principiantes
# Marca: Behike
# 5 Scripts | 60-90 segundos cada uno

---

### Script 1 — Que es n8n y por que nadie habla de esto

**Hook (0-3s):** Esta herramienta gratuita automatiza cosas que te costarian $500 al mes en software.

**Setup (3-10s):** Se llama n8n. Es de codigo abierto. Y es la herramienta de automatizacion mas poderosa que la mayoria nunca ha escuchado.

**Contenido (10-55s):**
n8n es como Zapier pero lo alojas tu mismo. Lo que significa sin precio por tarea. Lo que significa automatizaciones ilimitadas gratis.

Lo que puede hacer:
Cuando alguien llena un formulario, automaticamente crea una fila en tu hoja de calculo, te envia un correo de bienvenida, lo agrega a tu CRM y te avisa en Telegram. Todo al mismo tiempo. Cero trabajo manual.

Conectas apps usando bloques visuales llamados nodos. Cada nodo hace una cosa. Los encadenas juntos.

Las tres cosas que los principiantes usan:
1. Automatizacion de captura de leads a lista de correo
2. Programacion de posts en redes desde Notion
3. Alertas de resumen diario desde fuentes RSS

No necesitas saber programar. Arrastras, sueltas, conectas. Si te atascas, hay una comunidad de 50 mil personas que te ayudan.

La curva de aprendizaje es un fin de semana. El tiempo ahorrado es para siempre.

**CTA (55-60s):** Sigueme. El proximo video muestra como construir tu primer flujo de trabajo en menos de 10 minutos.

**Texto en pantalla:** "n8n = Zapier gratis que eres tu dueño" / "Sin precio por tarea" / "Constructor visual de automatizacion"

**Tipo de sonido:** Musica de fondo orientada a tecnologia, un poco animada, limpia y enfocada

---

### Script 2 — Construye este flujo de n8n en 10 minutos (lead a correo)

**Hook (0-3s):** Cada vez que alguien descarga tu cosa gratis, este flujo maneja todo automaticamente.

**Setup (3-10s):** Captura de lead a correo de bienvenida, sin codigo, diez minutos para construir.

**Contenido (10-55s):**
Esto es exactamente lo que vamos a construir.
Alguien llena tu formulario de Tally. n8n lo detecta. Lo agrega a tu lista de correo en Brevo. Le envia el link de descarga. Registra su informacion en Google Sheets. Listo.

Paso 1 — Abre n8n. Crea un nuevo flujo de trabajo.
Paso 2 — Agrega un nodo Webhook. Copia la URL en la configuracion de tu formulario de Tally.
Paso 3 — Agrega un nodo de Google Sheets. Conecta tu cuenta. Mapea los campos del formulario a las columnas de la hoja.
Paso 4 — Agrega un nodo de Brevo. Mapea el campo de correo. Selecciona tu lista.
Paso 5 — Agrega un nodo de Enviar Correo. Escribe tu mensaje de bienvenida. Incluye el link de descarga como variable.
Paso 6 — Activa. Prueba con tu propio correo.

Total de nodos: 4. Tiempo total: menos de 10 minutos.
Cada nuevo suscriptor activa toda la cadena automaticamente.

**CTA (55-60s):** Comenta "flujo" y te mando el link de la plantilla.

**Texto en pantalla:** "Formulario Tally a lista de correo en 10 min" / "Automatizacion gratis con n8n" / "Sin codigo"

**Tipo de sonido:** Energia de tutorial limpia, tempo medio, amigable para la concentracion, sin letra

---

### Script 3 — Como recibir el resumen de noticias IA cada manana sin hacer nada

**Hook (0-3s):** Cada manana recibo un resumen de las principales noticias de IA. No leo un solo articulo. n8n lo hace por mi.

**Setup (3-10s):** Este es el flujo de RSS a resumen de Telegram. Puedes construirlo en 15 minutos.

**Contenido (10-55s):**
Lo que hace:
Cada manana a las 8am, n8n extrae los ultimos posts de cinco fuentes RSS de noticias de IA. Envia cada titular y resumen a un canal privado de Telegram que controlas tu. Lo lees en 2 minutos en vez de 45.

Como construirlo:
Paso 1 — Nodo Cron. Configuralo para activarse cada dia a las 8am.
Paso 2 — Nodo Feed RSS. Agrega las URLs de los feeds de tus fuentes.
Paso 3 — Nodo de Codigo. Escribe un bucle corto que formatea cada item como un mensaje limpio.
Paso 4 — Nodo de Telegram. Conecta tu bot. Apuntalo a tu canal. Envia el mensaje formateado.

Cuatro nodos. El nodo de Codigo es el unico que necesita una linea de JavaScript, que ChatGPT te escribe en diez segundos.

Ahora siempre estas informado. Y nunca perdiste tiempo en el telefono para llegar ahi.

**CTA (55-60s):** Quieres el bloque de codigo exacto. Deja un comentario y lo comparto.

**Texto en pantalla:** "Noticias IA a Telegram cada manana" / "Solo 4 nodos" / "Despierta informado"

**Tipo de sonido:** Energia matutina, ligeramente calido y tranquilo, sin letra, sensacion lo-fi

---

### Script 4 — Automatiza tu pipeline de contenido con n8n y Notion

**Hook (0-3s):** Planeo mi contenido en Notion. Se publica en todos lados automaticamente. Aqui te cuento como.

**Setup (3-10s):** Esto es para creadores que hacen su contenido en lotes pero odian el trabajo manual de copiar y pegar despues.

**Contenido (10-55s):**
El flujo:
Escribes tu post en una base de datos de Notion. Cambias la propiedad "Estado" a "Listo para publicar." n8n detecta el cambio. Extrae el contenido. Lo formatea para cada plataforma. Lo programa en Buffer o lo publica directamente.

Como configurarlo:
Paso 1 — Nodo disparador de Notion. Observar filas donde Estado = "Listo para publicar."
Paso 2 — Nodo Set. Extraer Titulo, Cuerpo, URL de imagen de las propiedades de Notion.
Paso 3 — Nodo HTTP Request apuntando a la API de Buffer. Pasar el contenido como cuerpo del post.
Paso 4 — Actualizar el estado de la fila de Notion a "Publicado." Sin publicar dos veces.

Complemento opcional: agrega un nodo de IA en medio que reescriba el post para el tono de cada plataforma. La version de Twitter es mas corta. La de LinkedIn agrega contexto.

Un solo lugar para escribir. Todas las plataformas cubiertas. Cero trabajo manual.

**CTA (55-60s):** Sigueme para la plantilla de Notion que se conecta con este flujo.

**Texto en pantalla:** "Escribe una vez, publica en todas partes" / "Notion + n8n" / "Sin copia y pega manual"

**Tipo de sonido:** Enfocado y productivo, ritmo un poco rapido, fondo instrumental

---

### Script 5 — El flujo de n8n que me genera dinero mientras duermo

**Hook (0-3s):** Este flujo procesa ordenes, envia productos y manda recibos mientras estoy durmiendo.

**Setup (3-10s):** Si vendes productos digitales, este es el flujo mas importante que puedes construir.

**Contenido (10-55s):**
Lo que pasa cuando alguien compra tu producto en Gumroad:
Gumroad lanza un webhook.
n8n lo captura.
Registra la venta en Google Sheets.
Envia un correo personalizado de incorporacion con el link del producto.
Agrega al comprador a tu lista de correo en Brevo.
Te envia una notificacion de Telegram para que sepas que hubo una venta.

Toda esta secuencia corre en menos de 30 segundos.

Como construirlo:
Paso 1 — Nodo Webhook. Obtener la URL, pegarla en la configuracion de webhooks de Gumroad.
Paso 2 — Nodo de Google Sheets. Registrar nombre del comprador, correo, producto, fecha.
Paso 3 — Nodo Brevo. Agregar a tu lista de correo exclusiva para compradores.
Paso 4 — Nodo Gmail o SMTP. Enviar tu correo personalizado de bienvenida.
Paso 5 — Nodo Telegram. Enviarte "Nueva venta: [producto] de [correo]."

Seis nodos. Un flujo. Todo tu proceso de cumplimiento se maneja solo.

**CTA (55-60s):** Guarda esto. Cuando hagas tu primera venta, querras que esto ya este construido.

**Texto en pantalla:** "Gumroad + n8n = cumplimiento automatizado" / "6 nodos" / "Corre mientras duermes"

**Tipo de sonido:** Energia nocturna calmada, electronico suave de fondo, sensacion de "configurar y olvidar"
