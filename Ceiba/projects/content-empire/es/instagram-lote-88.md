# Instagram ES Lote 88
## Marca Behike | Voz ES | LATAM/España
## 5 Carruseles | Tema: Automatizar tu negocio con n8n (guía para principiantes)

---

## Carrusel 1: Qué es n8n y por qué deberías usarlo si tienes un negocio digital

**Slide 1 (Hook):**
Estás repitiendo manualmente tareas que una herramienta gratuita podría hacer por ti.
Cada copia, cada email manual, cada actualización de hoja de cálculo.
Eso se llama tiempo desperdiciado. Y tiene solución.

**Slide 2:**
¿Qué es n8n?

n8n es una herramienta de automatización de flujos de trabajo.
Conecta tus aplicaciones y hace tareas automáticamente sin que tú estés presente.

Piénsalo así: si esto pasa, haz aquello.
- Si alguien llena tu formulario, agrégalo a tu CRM y mándale un email
- Si publicas en Instagram, guarda el post en una hoja de cálculo
- Si alguien compra tu producto, envíale una secuencia de bienvenida

**Slide 3:**
n8n vs. Zapier: la comparación honesta

Zapier:
- Más fácil de usar al inicio
- Límite de operaciones por precio
- Código cerrado, no personalizable

n8n:
- Curva de aprendizaje un poco mayor
- Sin límite de operaciones (gratis en self-hosted)
- Código abierto, puedes personalizarlo
- Puedes correr código JavaScript dentro del flujo

Para un solopreneur que quiere control y sin límites de volumen: n8n gana.

**Slide 4:**
¿Para quién es n8n?

Para ti si:
- Tienes una lista de email y la actualizas manualmente
- Respondes los mismos mensajes repetidamente
- Copias datos entre plataformas a mano
- Publicas en redes manualmente sin sistema

No necesitas ser programador. La interfaz visual hace el 90% del trabajo.

**Slide 5 (CTA):**
¿Qué tarea estás haciendo manualmente hoy que podrías automatizar esta semana? Escríbela en los comentarios. Te ayudo a pensar si tiene solución en n8n.

---

**Caption:**
n8n es la herramienta que más tiempo me ha devuelto en los últimos 12 meses. No porque sea la más fácil, sino porque es la más flexible. Sin límites de uso, sin código cerrado, sin depender de que una empresa decida qué integra y qué no. Si tienes un negocio digital, aunque sea pequeño, hay tareas que podrías estar delegando a un sistema ahora mismo en lugar de hacerlas tú. Este carrusel es el primer paso.

**Hashtags:**
#n8n #automatizacion #negociodigital #emprendimientodigital #herramientasdigitales #solopreneur #productividad #marketingdigital #negociosonline #emprendedorlatino #automatizaciondigital #nocode #flujodetrabajo #herramientasIA #estrategiadigital

---

## Carrusel 2: Las 5 automatizaciones que todo solopreneur debería tener activas

**Slide 1 (Hook):**
Si tienes un negocio digital y haces estas 5 cosas manualmente,
estás trabajando más de lo necesario.
Aquí están las 5 automatizaciones con mayor retorno de tiempo.

**Slide 2:**
Automatización 1: Captura de leads a CRM

Cuando alguien llena tu formulario de contacto o descarga tu lead magnet, n8n:
- Crea el contacto en tu CRM automáticamente
- Lo etiqueta según el formulario que llenó
- Dispara la secuencia de emails de bienvenida

Tiempo ahorrado: 15-30 minutos por cada nuevo lead. Multiplicado por todos los leads del mes.

**Slide 3:**
Automatización 2: Repurposing de contenido

Escribes un post para una plataforma. n8n lo reformatea y lo programa para las demás.
Twitter a LinkedIn. Newsletter a Instagram. Una entrada, múltiples salidas.

Automatización 3: Resumen semanal de métricas

Cada domingo, n8n extrae los datos de tu email marketing, tus ventas, y tus redes. Genera un resumen limpio y lo manda a tu Telegram o inbox. Sabes tus números sin abrir ninguna plataforma.

**Slide 4:**
Automatización 4: Seguimiento de clientes

Cuando alguien compra tu producto, n8n:
- Registra la venta en una hoja de cálculo
- Programa una tarea de seguimiento a los 3 días
- Envía un email de check-in si no ha dejado reseña

Retención mejorada sin que tengas que recordarlo tú.

Automatización 5: Asistente de investigación

Mandas una URL o keyword a Telegram. n8n hace el scraping, resume el contenido con IA, y te devuelve el resumen en 30 segundos. Investigación sin salir de tu flujo de trabajo.

**Slide 5 (CTA):**
¿Cuál de estas 5 automatizaciones activarías primero? Elige una y esa es tu tarea de esta semana.

---

**Caption:**
Estas 5 automatizaciones no son proyectos de meses. La más sencilla se puede construir en 30 minutos con n8n si sigues las instrucciones correctas. El objetivo no es automatizar todo de golpe, es identificar cuál de tus tareas repetitivas consume más tiempo y atacarla primero. Cada automatización activa te devuelve tiempo que puedes dedicar a lo que realmente requiere tu cerebro: crear, estrategia, y ventas.

**Hashtags:**
#n8n #automatizacion #solopreneur #negociodigital #herramientasdigitales #productividad #emprendimientodigital #negociosonline #marketingdigital #emprendedorlatino #automatizaciondigital #nocode #flujodetrabajo #herramientasIA #estrategiadigital

---

## Carrusel 3: Cómo construir tu primer flujo en n8n (paso a paso)

**Slide 1 (Hook):**
El primer flujo en n8n siempre parece complicado.
No lo es.
En 5 slides te explico cómo construir el más útil para empezar.

**Slide 2:**
El flujo más simple para empezar: formulario a hoja de cálculo

Objetivo: cada vez que alguien llena tu formulario de contacto, guardar automáticamente nombre, email, y mensaje en Google Sheets.

Por qué empezar con este:
- Aprende cómo funcionan los triggers
- Aprende cómo fluye la data entre nodos
- Aprende cómo conectar servicios externos
- Tiene utilidad real desde el primer día

**Slide 3:**
Los 3 nodos que necesitas

Nodo 1 (Trigger): Webhook — recibe la data de tu formulario
Nodo 2 (Proceso): Set node — selecciona y formatea los campos que quieres guardar
Nodo 3 (Acción): Google Sheets — añade una fila nueva con los datos

Tiempo total de construcción: 15-20 minutos la primera vez.

**Slide 4:**
Una vez que funciona, lo extiendes así:

Añade un nodo de Email (Gmail/SendGrid) para mandar confirmación automática al que llenó el formulario.

Añade un nodo condicional para enrutar formularios urgentes a un mensaje de Telegram.

Añade un nodo de CRM (HubSpot, Notion, Airtable) para crear el contacto automáticamente.

Empiezas simple. Construyes capas. El flujo crece con tu negocio.

**Slide 5 (CTA):**
Si quieres el flujo pre-construido para importar directamente a tu instancia de n8n, escribe "flujo" en los comentarios y te lo mando. Sin costo, sin trampa.

---

**Caption:**
La curva de aprendizaje de n8n existe, pero es más corta de lo que parece. El primer flujo que construyas te enseña el 80% de lo que necesitas saber para construir el segundo. Y el segundo es tres veces más rápido. Lo que parece complicado en el tutorial de YouTube se convierte en natural después de haberlo construido una vez con tus propias manos. Este carrusel es el mapa para construir ese primer flujo con la menor fricción posible.

**Hashtags:**
#n8n #tutorialn8n #automatizacion #negociodigital #herramientasdigitales #solopreneur #nocode #flujodetrabajo #emprendimientodigital #negociosonline #productividad #marketingdigital #emprendedorlatino #automatizaciondigital #herramientasIA

---

## Carrusel 4: Los errores más comunes al empezar con n8n (y cómo evitarlos)

**Slide 1 (Hook):**
La mayoría de las personas que intentan n8n lo abandonan en la primera semana.
No porque sea demasiado difícil.
Porque cometen los mismos 4 errores que hacen todo más complicado.

**Slide 2:**
Error 1: Intentar automatizar algo demasiado complejo al inicio

El primer flujo debe ser simple. No un pipeline de 15 nodos. Un trigger, un proceso, una acción.

Error 2: No entender la estructura de la data

n8n trabaja con objetos JSON. Si no entiendes cómo ver la data que sale de un nodo, vas a estar adivinando en cada paso. La solución: usa el panel de ejecución para ver qué data produce cada nodo antes de conectar el siguiente.

**Slide 3:**
Error 3: Conectar credenciales mal desde el inicio

Cada vez que conectas una aplicación (Gmail, Google Sheets, etc.) necesitas configurar las credenciales correctamente. Si saltas este paso o lo haces mal, el flujo fallará silenciosamente. Dedica 5 minutos a probar cada credencial por separado antes de construir el flujo.

Error 4: No activar el flujo después de construirlo

Un flujo en modo borrador no corre en producción. Tienes que activarlo manualmente. Parece obvio pero es el error más frecuente.

**Slide 4:**
El mindset correcto para aprender n8n

No lo trates como una herramienta que debes dominar de golpe. Trátalo como un set de bloques: aprendes cómo funciona cada bloque por separado, luego combinas los bloques que necesitas para tu caso específico.

La pregunta correcta no es "¿cómo funciona n8n?" sino "¿qué tarea específica quiero automatizar y qué bloques necesito para eso?"

**Slide 5 (CTA):**
¿Cuál de estos 4 errores reconoces? Cuéntame dónde te has atascado con n8n o con otras herramientas de automatización. Eso me ayuda a saber qué contenido crear después.

---

**Caption:**
n8n no es difícil. Es diferente. Tiene una lógica propia que al principio se siente extraña y en la tercera semana se vuelve natural. Los errores de esta lista los cometen casi todos al empezar porque nadie los advierte de antemano. Evitarlos desde el inicio reduce la frustración y acelera el aprendizaje real. Guarda este carrusel para consultarlo cuando te atasques.

**Hashtags:**
#n8n #automatizacion #errorescomunes #negociodigital #herramientasdigitales #solopreneur #nocode #aprendizaje #emprendimientodigital #negociosonline #productividad #emprendedorlatino #flujodetrabajo #automatizaciondigital #herramientasIA

---

## Carrusel 5: n8n para negocios de contenido: casos de uso reales

**Slide 1 (Hook):**
No necesitas un equipo de tecnología para tener un sistema de automatización real.
Con n8n y 2 horas de configuración inicial,
puedes tener un backend automatizado que funciona solo.

**Slide 2:**
Caso 1: El pipeline de newsletter automatizado

- Escribes el borrador en Notion
- n8n detecta el estado "listo para enviar"
- Formatea el contenido para Beehiiv o ConvertKit
- Programa el envío en el horario óptimo
- Registra el envío en tu base de datos de contenido

Un flujo. Zero copia y pega manual.

**Slide 3:**
Caso 2: El sistema de distribución de contenido

- Publicas un post largo en un blog o newsletter
- n8n extrae el texto y se lo manda a un nodo de IA (ChatGPT o Claude)
- El nodo de IA genera versiones para Twitter, LinkedIn, Instagram
- n8n programa cada versión en la plataforma correspondiente

Un contenido original. Tres plataformas. Sin trabajo manual.

**Slide 4:**
Caso 3: El panel de métricas automático

Cada lunes, n8n:
- Extrae datos de tu plataforma de email (tasa de apertura, clics)
- Extrae ventas de Gumroad o Stripe
- Extrae métricas de YouTube o Instagram vía API
- Genera un resumen formateado
- Lo envía a tu canal de Telegram

Sabes exactamente cómo fue la semana sin abrir ningún dashboard.

**Slide 5 (CTA):**
¿Qué parte de tu negocio de contenido consume más tiempo ahora mismo? Escríbelo en los comentarios. Con gusto te digo si es automatizable con n8n y cómo.

---

**Caption:**
La promesa de la automatización no es eliminar el trabajo creativo. Es eliminar el trabajo operativo que roba tiempo al creativo. Cuando tienes un sistema que distribuye, registra, y analiza automáticamente, cada hora que antes se iba en operaciones se convierte en una hora disponible para crear mejor. Estos tres casos de uso son reales, aplicables esta semana, y construibles en n8n sin ser programador. El único requisito es tomarte las dos horas de configuración inicial.

**Hashtags:**
#n8n #automatizacion #negociodecontenido #creadordigital #herramientasdigitales #solopreneur #nocode #productividad #emprendimientodigital #negociosonline #marketingdigital #emprendedorlatino #flujodetrabajo #automatizaciondigital #estrategiadigital
