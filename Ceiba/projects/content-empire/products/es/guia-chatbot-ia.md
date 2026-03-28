# Como Agregar un Chatbot de IA a Tu Sitio Web en 30 Minutos

**Por Behike**

---

Copyright 2026 Behike. Todos los derechos reservados. Spanish Edition.

Ninguna parte de esta guia puede ser reproducida, distribuida o transmitida de ninguna forma sin el permiso escrito previo del autor.

**Aviso sobre IA:** Esta guia fue escrita con la asistencia de herramientas de IA. Todo el codigo ha sido probado y verificado en hardware real. El sistema descrito en esta guia fue construido y desplegado por el autor antes de escribir esta guia. Estas recibiendo una configuracion probada y funcional.

---

## Capitulo 1: Lo Que Vas a Construir

Al terminar esta guia, vas a tener una burbuja de chat flotante en tu sitio web que responde preguntas de clientes usando IA. Se ve como los widgets de chat que ves en productos SaaS profesionales, los que se deslizan desde la esquina de la pantalla.

Esto es lo que lo hace diferente de todos los otros tutoriales de chatbots.

Este corre en TU computadora. No en los servidores de OpenAI. No en un servicio de chatbot de $50/mes. Tu maquina, tus datos, tu IA. El costo mensual despues del setup es $0.

El sistema tiene tres partes:

1. **Ollama** corre el modelo de IA en tu computadora.
2. **Un servidor Python** conecta tu sitio web con Ollama.
3. **Un widget JavaScript** le da a tus visitantes una interfaz de chat limpia.

Funciona con cualquier sitio web. WordPress, Shopify, Squarespace, un archivo HTML plano, cualquier cosa donde puedas agregar un script tag. Si puedes pegar codigo antes de `</body>`, puedes correr esto.

Tus visitantes escriben una pregunta. El widget la envia a tu servidor. Tu servidor le pregunta a la IA. La IA responde. La respuesta aparece en el chat. Todo el viaje de ida y vuelta toma 2-5 segundos dependiendo de tu hardware.

---

## Capitulo 2: Prerrequisitos

Antes de empezar, asegurate de tener esto:

**Hardware:**
- Una computadora con al menos 8GB de RAM (16GB recomendado)
- Mac, Linux o Windows, todos funcionan
- Al menos 5GB de espacio libre en disco para el modelo de IA

**Software:**
- Python 3.8 o mas reciente (verifica con `python3 --version`)
- Una terminal (Terminal en Mac, PowerShell en Windows, cualquier terminal en Linux)
- Un editor de texto (VS Code, Notepad++, el que uses)

**Acceso:**
- Un sitio web del cual puedas editar el HTML
- La capacidad de agregar un tag `<script>` a tus paginas

**Opcional pero util:**
- Familiaridad basica con la linea de comandos
- Node.js (solo si quieres usar PM2 para deployment despues)

NO necesitas:
- Una API key de OpenAI
- Un servidor en la nube
- Ninguna experiencia previa con IA

---

## Capitulo 3: Instalar Ollama

Ollama es el motor que corre modelos de IA en tu computadora. Una instalacion, un comando, y tienes una IA local lista para usar.

### Mac

Abre Terminal y ejecuta:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

O descarga la app desde [ollama.com](https://ollama.com) y arrastralaa Applications.

### Linux

El mismo one-liner:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Windows

Descarga el instalador desde [ollama.com](https://ollama.com) y ejecutalo. Sigue las instrucciones.

### Descargar un Modelo

Ahora descarga el modelo de IA. Abre una terminal y ejecuta:

```bash
ollama pull llama3.2
```

Esto descarga el modelo llama3.2 (~2GB). Es el mejor balance entre velocidad y calidad para uso de chatbot.

**Si tu computadora es lenta o tiene menos de 8GB de RAM**, usa el modelo mas pequeno:

```bash
ollama pull tinyllama
```

Tinyllama es mas rapido pero menos preciso. Suficiente para preguntas simples de clientes.

### Probarlo

Asegurate de que Ollama este corriendo, luego prueba con curl:

```bash
curl http://localhost:11434/api/chat -d '{
  "model": "llama3.2",
  "messages": [{"role": "user", "content": "Say hello"}],
  "stream": false
}'
```

Deberias ver una respuesta JSON con la respuesta de la IA. Si recibes un error de "connection refused", Ollama no esta corriendo. En Mac, abre la app de Ollama. En Linux, ejecuta `ollama serve` en una ventana de terminal separada.

**Salida esperada:**

```json
{
  "model": "llama3.2",
  "message": {
    "role": "assistant",
    "content": "Hello! How can I help you today?"
  }
}
```

Si ves algo asi, todo bien. Sigue adelante.

---

## Capitulo 4: Construir la API de Chat

Este servidor Python se sienta entre tu sitio web y Ollama. Tu sitio web envia preguntas a este servidor. Este servidor le pregunta a Ollama. Ollama responde. El servidor envia la respuesta de vuelta a tu sitio web.

### Instalar Dependencias

```bash
pip install fastapi uvicorn httpx slowapi
```

### Crear el Servidor

Crea un nuevo archivo llamado `chat_api.py` y pega este bloque de codigo completo:

```python
import httpx
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone

app = FastAPI(title="Chat API")

# Rate limiting: 10 requests per minute per visitor
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"error": "Too many requests. Try again in a minute."}
    )

# CORS - allows your website to talk to this server
# Replace "*" with your domain in production (e.g. "https://yoursite.com")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ollama settings
OLLAMA_URL = "http://localhost:11434"
MODEL = "llama3.2"  # Change to "tinyllama" if using weaker hardware

# ============================================
# CUSTOMIZE THIS SYSTEM PROMPT FOR YOUR BUSINESS
# ============================================
SYSTEM_PROMPT = """You are a helpful customer service assistant for [YOUR BUSINESS NAME].

You help customers with questions about [YOUR PRODUCTS/SERVICES].

Key information:
- [Product 1]: [Price] - [One sentence description]
- [Product 2]: [Price] - [One sentence description]
- [Product 3]: [Price] - [One sentence description]

Rules:
- Keep responses short (2-3 sentences max).
- Be helpful and direct. No filler.
- If you do not know the answer, say so honestly.
- Never make up information.
"""

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = []

class ChatResponse(BaseModel):
    response: str
    timestamp: str

@app.get("/health")
async def health():
    """Health check. Hit this URL to verify the server is running."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(f"{OLLAMA_URL}/api/tags")
            if r.status_code == 200:
                return {"status": "ok", "model": MODEL}
    except Exception:
        pass
    return {"status": "degraded", "note": "Ollama may be unavailable"}

@app.post("/chat", response_model=ChatResponse)
@limiter.limit("10/minute")
async def chat(request: Request, body: ChatRequest):
    """Main chat endpoint. Receives a message, returns an AI response."""

    # Build the conversation for Ollama
    ollama_messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for msg in (body.history or []):
        ollama_messages.append({"role": msg.role, "content": msg.content})

    ollama_messages.append({"role": "user", "content": body.message})

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(
                f"{OLLAMA_URL}/api/chat",
                json={
                    "model": MODEL,
                    "messages": ollama_messages,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 200,
                    }
                }
            )
            r.raise_for_status()
            data = r.json()
            reply = data.get("message", {}).get("content", "Sorry, something went wrong.")

    except httpx.TimeoutException:
        reply = "I'm taking a moment to think. Please try again."
    except Exception:
        reply = "Something went wrong. Please try again later."

    return ChatResponse(
        response=reply,
        timestamp=datetime.now(timezone.utc).isoformat()
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9877)
```

### Iniciar el Servidor

```bash
python chat_api.py
```

Deberias ver una salida como:

```
INFO:     Uvicorn running on http://0.0.0.0:9877
```

Pruebalo:

```bash
curl -X POST http://localhost:9877/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What products do you sell?", "history": []}'
```

Si recibes una respuesta JSON con la respuesta de la IA, tu servidor esta funcionando. Dejalo corriendo y pasa al siguiente capitulo.

---

## Capitulo 5: Agregar el Widget de Chat

Este es el codigo JavaScript que crea la burbuja de chat flotante en tu sitio web. Maneja la interfaz, envia mensajes a tu servidor y muestra las respuestas.

### El Codigo del Widget

Crea un archivo llamado `chat-widget.js` y pega este codigo:

```javascript
(function() {
  // ============================================
  // CONFIGURE THESE THREE THINGS
  // ============================================
  const API_URL = 'http://localhost:9877';  // Your server address
  const GREETING = "Hey! Ask me anything."; // First message visitors see
  const BOT_NAME = "AI Assistant";          // Name shown in chat header

  const RATE_LIMIT_MS = 2000;
  const SESSION_KEY = 'chat-history';
  let isOpen = false;
  let lastSendTime = 0;
  let isWaiting = false;

  function loadHistory() {
    try {
      const saved = sessionStorage.getItem(SESSION_KEY);
      return saved ? JSON.parse(saved) : [{ role: 'assistant', content: GREETING }];
    } catch (e) {
      return [{ role: 'assistant', content: GREETING }];
    }
  }

  function saveHistory(messages) {
    try { sessionStorage.setItem(SESSION_KEY, JSON.stringify(messages)); } catch (e) {}
  }

  let messages = loadHistory();

  function createWidget() {
    const widget = document.createElement('div');
    widget.id = 'ai-chat';
    widget.innerHTML = `
      <style>
        #ai-chat-toggle {
          position: fixed; bottom: 24px; right: 24px; z-index: 9999;
          width: 48px; height: 48px; border-radius: 50%;
          background: #0A84FF; border: none; cursor: pointer;
          display: flex; align-items: center; justify-content: center;
          font-size: 22px; box-shadow: 0 4px 20px rgba(0,0,0,0.4);
          transition: transform 0.2s;
        }
        #ai-chat-toggle:hover { transform: scale(1.1); }
        #ai-chat-panel {
          position: fixed; bottom: 84px; right: 24px; z-index: 9998;
          width: 320px; height: 450px;
          background: rgba(20,20,20,0.95);
          backdrop-filter: blur(20px);
          border-radius: 16px;
          border: 1px solid rgba(255,255,255,0.1);
          box-shadow: 0 8px 40px rgba(0,0,0,0.6);
          display: none; flex-direction: column; overflow: hidden;
        }
        #ai-chat-panel.open { display: flex; }
        .chat-header {
          display: flex; align-items: center; justify-content: space-between;
          padding: 14px 16px;
          border-bottom: 1px solid rgba(255,255,255,0.08);
        }
        .chat-header-title {
          font-size: 15px; font-weight: 600; color: #F5F5F7;
          font-family: -apple-system, sans-serif;
        }
        .chat-close {
          background: none; border: none; color: #86868B;
          font-size: 18px; cursor: pointer; padding: 2px 6px;
          border-radius: 6px;
        }
        .chat-messages {
          flex: 1; overflow-y: auto; padding: 16px;
          display: flex; flex-direction: column; gap: 12px;
        }
        .chat-msg {
          max-width: 85%; padding: 10px 14px; border-radius: 14px;
          font-size: 13px; line-height: 1.5;
          font-family: -apple-system, sans-serif; word-wrap: break-word;
        }
        .chat-msg.assistant {
          background: rgba(255,255,255,0.08); color: #F5F5F7;
          align-self: flex-start; border-bottom-left-radius: 4px;
        }
        .chat-msg.user {
          background: #0A84FF; color: #fff;
          align-self: flex-end; border-bottom-right-radius: 4px;
        }
        .chat-msg.error {
          background: rgba(255,59,48,0.15); color: #FF6961;
          align-self: flex-start;
        }
        .chat-typing { display: none; gap: 4px; padding: 10px 14px;
          background: rgba(255,255,255,0.08); border-radius: 14px;
          align-self: flex-start; }
        .chat-typing.visible { display: flex; }
        .chat-typing-dot {
          width: 6px; height: 6px; background: #86868B;
          border-radius: 50%; animation: bounce 1.2s infinite;
        }
        .chat-typing-dot:nth-child(2) { animation-delay: 0.2s; }
        .chat-typing-dot:nth-child(3) { animation-delay: 0.4s; }
        @keyframes bounce {
          0%,60%,100% { transform: translateY(0); opacity: 0.4; }
          30% { transform: translateY(-4px); opacity: 1; }
        }
        .chat-input-area {
          display: flex; gap: 8px; padding: 12px 16px;
          border-top: 1px solid rgba(255,255,255,0.08);
        }
        .chat-input {
          flex: 1; padding: 10px 14px;
          background: rgba(255,255,255,0.06);
          border: 1px solid rgba(255,255,255,0.1);
          border-radius: 980px; color: #F5F5F7; font-size: 13px;
          outline: none; font-family: -apple-system, sans-serif;
        }
        .chat-input::placeholder { color: #86868B; }
        .chat-input:focus { border-color: #0A84FF; }
        .chat-send {
          background: #0A84FF; border: none; color: #fff;
          width: 36px; height: 36px; border-radius: 50%;
          cursor: pointer; display: flex; align-items: center;
          justify-content: center;
        }
        .chat-send:disabled { opacity: 0.4; cursor: default; }
        .chat-send svg { width: 16px; height: 16px; fill: #fff; }
        @media (max-width: 480px) {
          #ai-chat-panel { left: 12px; right: 12px; bottom: 78px;
            width: auto; height: 400px; }
        }
      </style>
      <button id="ai-chat-toggle">💬</button>
      <div id="ai-chat-panel">
        <div class="chat-header">
          <span class="chat-header-title">${BOT_NAME}</span>
          <button class="chat-close">&times;</button>
        </div>
        <div class="chat-messages" id="chatMessages"></div>
        <div class="chat-typing" id="chatTyping">
          <div class="chat-typing-dot"></div>
          <div class="chat-typing-dot"></div>
          <div class="chat-typing-dot"></div>
        </div>
        <div class="chat-input-area">
          <input type="text" class="chat-input" id="chatInput"
            placeholder="Ask something..." autocomplete="off">
          <button class="chat-send" id="chatSend">
            <svg viewBox="0 0 24 24">
              <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
            </svg>
          </button>
        </div>
      </div>`;
    document.body.appendChild(widget);

    const toggle = document.getElementById('ai-chat-toggle');
    const panel = document.getElementById('ai-chat-panel');
    const closeBtn = panel.querySelector('.chat-close');
    const messagesEl = document.getElementById('chatMessages');
    const typingEl = document.getElementById('chatTyping');
    const inputEl = document.getElementById('chatInput');
    const sendBtn = document.getElementById('chatSend');

    function renderMessages() {
      messagesEl.innerHTML = '';
      messages.forEach(m => appendDOM(m.role, m.content));
      scrollBottom();
    }
    function appendDOM(role, content) {
      const div = document.createElement('div');
      div.className = 'chat-msg ' + role;
      div.textContent = content;
      messagesEl.appendChild(div);
    }
    function scrollBottom() { messagesEl.scrollTop = messagesEl.scrollHeight; }
    function showTyping(show) {
      typingEl.classList.toggle('visible', show);
      if (show) { messagesEl.appendChild(typingEl); scrollBottom(); }
    }

    async function sendMessage() {
      const text = inputEl.value.trim();
      if (!text || isWaiting) return;
      if (Date.now() - lastSendTime < RATE_LIMIT_MS) return;
      lastSendTime = Date.now();

      messages.push({ role: 'user', content: text });
      appendDOM('user', text);
      inputEl.value = '';
      scrollBottom();
      saveHistory(messages);

      isWaiting = true;
      sendBtn.disabled = true;
      showTyping(true);

      try {
        const res = await fetch(API_URL + '/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: text, history: messages.slice(0, -1) })
        });
        if (!res.ok) throw new Error('Server error');
        const data = await res.json();
        const reply = data.response || 'Sorry, something went wrong.';
        messages.push({ role: 'assistant', content: reply });
        showTyping(false);
        appendDOM('assistant', reply);
      } catch (e) {
        showTyping(false);
        messages.push({ role: 'error', content: 'Chat is offline. Try again later.' });
        appendDOM('error', 'Chat is offline. Try again later.');
      }
      scrollBottom();
      saveHistory(messages);
      isWaiting = false;
      sendBtn.disabled = false;
      inputEl.focus();
    }

    toggle.addEventListener('click', () => {
      isOpen = !isOpen;
      panel.classList.toggle('open', isOpen);
      if (isOpen) { inputEl.focus(); scrollBottom(); }
    });
    closeBtn.addEventListener('click', () => {
      isOpen = false; panel.classList.remove('open');
    });
    sendBtn.addEventListener('click', sendMessage);
    inputEl.addEventListener('keydown', e => {
      if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
    });
    document.addEventListener('click', e => {
      if (isOpen && !panel.contains(e.target) && !toggle.contains(e.target)) {
        isOpen = false; panel.classList.remove('open');
      }
    });
    renderMessages();
  }

  document.addEventListener('DOMContentLoaded', createWidget);
})();
```

### Agregarlo a Tu Sitio Web

Abre el archivo HTML de tu sitio web. Busca el tag `</body>`. Pega esta linea justo antes:

```html
<script src="chat-widget.js"></script>
```

Si tu servidor no esta en la misma maquina que tu sitio web, necesitas cambiar `API_URL` en el codigo del widget para que apunte a la direccion IP y puerto de tu servidor. Por ejemplo: `http://192.168.0.100:9877`.

### Que Hace Cada Parte

- **API_URL**: A donde el widget envia los mensajes. Cambia esto a la direccion de tu servidor.
- **GREETING**: El primer mensaje que los visitantes ven al abrir el chat.
- **BOT_NAME**: El nombre que se muestra en el encabezado del chat.
- **RATE_LIMIT_MS**: Tiempo minimo entre mensajes (previene spam).
- **sessionStorage**: Guarda el historial del chat para que persista mientras la pestana este abierta.

El widget crea un circulo azul flotante en la esquina inferior derecha. Haz clic y un panel de chat se desliza hacia arriba. Los mensajes aparecen en burbujas. Hay un indicador de escritura con puntos animados mientras la IA piensa.

---

## Capitulo 6: Personalizar para Tu Negocio

La personalizacion mas importante es el system prompt. Esta es la instruccion que le das a la IA para decirle quien es, que sabe y como comportarse. Un buen system prompt es la diferencia entre un chatbot util y uno inutil.

### Como Escribir un Buen System Prompt

Sigue esta formula:

1. **Identidad**: Dile a la IA quien es ("Eres el bot de soporte al cliente de...")
2. **Conocimiento**: Lista la informacion especifica que debe saber (productos, precios, politicas)
3. **Reglas**: Dile como comportarse (respuestas cortas, nunca inventar cosas, etc.)

Mientras mas informacion especifica pongas, mejores seran las respuestas.

### Ejemplo 1: Tienda de Ecommerce

```python
SYSTEM_PROMPT = """You are the helpful assistant for GlowSkin Beauty.

Products we sell:
- Vitamin C Serum ($24.99) - Brightening serum for all skin types
- Retinol Night Cream ($34.99) - Anti-aging cream, use at night only
- SPF 50 Daily Moisturizer ($19.99) - Lightweight, no white cast
- Hydrating Face Mask ($12.99) - Use 2-3 times per week

Shipping: Free over $50. Standard shipping is $4.99, takes 3-5 business days.
Returns: 30-day return policy, item must be unopened.

Rules:
- Keep responses to 2-3 sentences.
- Always mention the exact price when discussing a product.
- If someone asks about ingredients, tell them to check the product page.
- Never recommend products for medical conditions.
"""
```

### Ejemplo 2: Portafolio de Freelancer

```python
SYSTEM_PROMPT = """You are the assistant on Alex Rivera's portfolio website.

Alex is a freelance web designer based in Austin, TX. He builds websites for small businesses and startups.

Services:
- Landing Page Design ($1,500) - Single page, mobile responsive, 2-week turnaround
- Full Website (from $3,000) - Multi-page site, CMS included, 4-6 week turnaround
- Brand Identity Package ($2,000) - Logo, colors, typography, brand guide

Availability: Currently booking projects for next month.
Contact: alex@example.com

Rules:
- Be professional but friendly.
- If someone asks for a quote, tell them to email Alex with project details.
- Keep responses short and helpful.
"""
```

### Ejemplo 3: Restaurante

```python
SYSTEM_PROMPT = """You are the virtual assistant for Casa Luna, a Mexican restaurant in Miami.

Hours: Tuesday-Sunday 11am-10pm. Closed Mondays.
Location: 1234 Coral Way, Miami, FL 33145
Phone: (305) 555-0199
Reservations: Call or book on OpenTable.

Popular dishes: Birria tacos ($14), Mole enchiladas ($16), Churros ($8)
We do catering for groups of 20+. Contact us for custom menus.
Parking: Free lot behind the building.

Rules:
- Keep answers short and helpful.
- Always mention hours if someone asks about visiting.
- For dietary restrictions, tell them to call ahead so the chef can prepare.
"""
```

### Agregar Mas Conocimiento

La IA solo puede responder preguntas sobre lo que pongas en el system prompt. Si los clientes siguen preguntando sobre algo y el bot no puede responder, agrega esa informacion a tu system prompt y reinicia el servidor.

Tambien puedes incluir entradas estilo FAQ:

```
Common questions:
Q: Do you ship internationally? A: Not yet, US only for now.
Q: Can I cancel my order? A: Yes, within 1 hour of placing it. Email us.
Q: Do you offer discounts? A: Sign up for our newsletter for 10% off your first order.
```

---

## Capitulo 7: Desplegarlo

Tienes tres opciones para mantener tu chatbot corriendo.

### Opcion A: Correr en Tu Propia Computadora

Mejor para: pruebas, negocios locales, o si tu computadora esta siempre encendida.

Solo manten la ventana de terminal abierta con `python chat_api.py` corriendo. La desventaja es que si tu computadora se duerme, se apaga o se reinicia, el chatbot se desconecta.

Para una configuracion mas confiable en Mac/Linux, usa un administrador de procesos:

```bash
# Install PM2 (requires Node.js)
npm install -g pm2

# Start the server with PM2
pm2 start chat_api.py --interpreter python3 --name chatbot

# Make it survive reboots
pm2 startup
pm2 save
```

Ahora tu chatbot se reinicia automaticamente si se cae o tu computadora se reinicia.

### Opcion B: Correr en un VPS Barato

Mejor para: confiabilidad, servir clientes 24/7.

Consigue un VPS en DigitalOcean o Hetzner ($5-10/mes). Conectate por SSH y ejecuta:

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull the model
ollama pull llama3.2

# Install Python dependencies
pip install fastapi uvicorn httpx slowapi

# Upload your chat_api.py file (use scp or paste it)
scp chat_api.py user@your-server-ip:~/

# Create a systemd service so it runs forever
sudo tee /etc/systemd/system/chatbot.service > /dev/null <<EOF
[Unit]
Description=AI Chatbot API
After=network.target

[Service]
User=$USER
WorkingDirectory=/home/$USER
ExecStart=/usr/bin/python3 /home/$USER/chat_api.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable chatbot
sudo systemctl start chatbot
```

Actualiza `API_URL` en tu widget para que apunte a la IP de tu VPS: `http://YOUR_SERVER_IP:9877`.

Para produccion, pon Cloudflare o nginx al frente para HTTPS.

### Opcion C: Correr en una Laptop Vieja

Tienes una laptop vieja acumulando polvo? Conviertela en un servidor de IA dedicado. Instalale Linux, sigue los mismos pasos de la Opcion B, y apunta tu widget a su direccion IP local.

Para una guia completa sobre como convertir hardware viejo en un sistema de IA multi-maquina, revisa la **Guia del Empleado IA ($19.99)** que cubre toda la configuracion de infraestructura, acceso SSH, administracion de servicios y escalamiento a multiples maquinas.

---

## Capitulo 8: Solucion de Problemas

### "Connection refused" al probar Ollama

Ollama no esta corriendo. Inicialo:

- **Mac**: Abre la app de Ollama desde Aplicaciones
- **Linux**: Ejecuta `ollama serve` en una terminal separada
- **Windows**: Abre Ollama desde el Menu de Inicio

### "Port already in use" al iniciar el servidor

Algo mas esta usando el puerto 9877. Matalo o usa un puerto diferente:

```bash
# Find what is using the port
lsof -i :9877

# Or just use a different port
python -c "import uvicorn; uvicorn.run('chat_api:app', host='0.0.0.0', port=9878)"
```

Recuerda actualizar `API_URL` en el widget si cambias el puerto.

### Errores CORS en la consola del navegador

Tu sitio web no puede alcanzar el servidor. Verifica tres cosas:

1. El servidor esta corriendo
2. `API_URL` en el widget coincide exactamente con la direccion de tu servidor
3. El middleware CORS en `chat_api.py` incluye el dominio de tu sitio web

### Respuestas lentas (10+ segundos)

El modelo de IA es muy grande para tu hardware. Cambia a tinyllama:

```bash
ollama pull tinyllama
```

Luego cambia `MODEL = "tinyllama"` en `chat_api.py` y reinicia el servidor.

### El widget no aparece en la pagina

Asegurate de que el tag `<script>` este antes de `</body>`, no dentro de `<head>`. El widget necesita que el body de la pagina exista antes de poder agregarse.

---

## Que Sigue?

Ahora tienes un chatbot de IA funcionando en tu sitio web. Gratis. Corriendo en tu propio hardware.

Si quieres ir mas profundo y construir un sistema completo de IA multi-maquina con hardware dedicado, orquestacion de agentes y automatizacion, revisa la **Guia del Empleado IA** en behike.store.

---

*Construido por Behike. Mas herramientas en behike.store.*
