# Como Construi un Empleado de IA: La Guia Completa del Sistema

**Por Behike**

*El plano de un estudiante de ingenieria de computadoras para construir un sistema de agentes de IA multi-maquina que trabaja mientras duermes. Tres computadoras, cero costo mensual, apalancamiento infinito.*

---

## Tabla de Contenidos

1. [Introduccion: La Historia](#1-introduccion-la-historia)
2. [La Arquitectura](#2-la-arquitectura)
3. [Requisitos de Hardware](#3-requisitos-de-hardware)
4. [Stack de Software](#4-stack-de-software)
5. [Configurando Tu Primera Maquina (HQ)](#5-configurando-tu-primera-maquina-hq)
6. [Agregando Nodos de Trabajo](#6-agregando-nodos-de-trabajo)
7. [Comunicacion Entre Maquinas](#7-comunicacion-entre-maquinas)
8. [Configuracion de Agentes](#8-configuracion-de-agentes)
9. [Framework de Delegacion de Tareas](#9-framework-de-delegacion-de-tareas)
10. [Construyendo Tu Primera Automatizacion](#10-construyendo-tu-primera-automatizacion)
11. [Monitoreo y Mantenimiento](#11-monitoreo-y-mantenimiento)
12. [Desglose de Costos](#12-desglose-de-costos)
13. [Resolucion de Problemas](#13-resolucion-de-problemas)
14. [Que Sigue: Escalando Mas Alla de 3 Maquinas](#14-que-sigue-escalando-mas-alla-de-3-maquinas)

---

## 1. Introduccion: La Historia

Soy estudiante de ingenieria de computadoras en Puerto Rico. No trabajo para una empresa de tecnologia. No tengo un rack de servidores en mi closet. No pago por computacion en la nube. Lo que si tengo son tres computadoras, una red local y un sistema que ejecuta tareas por mi mientras estoy en clase, mientras ceno y mientras duermo.

El sistema se llama Behique. Nombrado en honor a los sanadores espirituales y guardianes del conocimiento del pueblo taino, la civilizacion indigena del Caribe. Un behique era la persona en la comunidad que entendia sistemas que otros no podian ver. Me parecio el nombre correcto para lo que estaba construyendo.

Esto es lo que Behique hace en un dia cualquiera:

- Procesa una cola de tareas de IA a traves de tres maquinas fisicas
- Dirige el trabajo al modelo mas barato disponible (inferencia local gratuita primero, APIs de pago solo cuando es necesario)
- Genera contenido de video corto usando text-to-speech, generacion de imagenes y FFmpeg
- Gestiona un pipeline de listings de eBay que investiga productos, escribe descripciones y formatea publicaciones
- Corre un bot de accountability en Telegram que clasifica mis ideas, rastrea mi progreso y guarda todo en Notion
- Sincroniza archivos entre todas las maquinas automaticamente
- Acumula conocimiento en un sistema de memoria persistente que hace cada tarea futura mas inteligente

El costo mensual total de correr este sistema es cero dolares.

Construi esto en el transcurso de varias semanas, empezando desde cero. No porque sea un genio, sino porque las herramientas existen y nadie esta hablando de como conectarlas. Cada tutorial que encontre online era sobre una herramienta aislada. "Como usar Ollama." "Como configurar n8n." "Como usar Claude." Nadie estaba escribiendo sobre como hacer que todas funcionen juntas como un solo organismo distribuido en multiples maquinas.

Para eso es esta guia.

Al final de este documento, vas a tener un plano completo para construir tu propio empleado de IA. No un chatbot. No un solo script. Un sistema distribuido y autonomo que corre en hardware que probablemente ya tienes, no cuesta nada por mes y se vuelve mas inteligente con el tiempo.

Te voy a mostrar exactamente como construi el mio. Cada herramienta, cada archivo de configuracion, cada decision que tome y por que. Donde falle. Que haria diferente. Y como puedes construir el tuyo en un fin de semana.

Vamos a ello.

---

## 2. La Arquitectura

Antes de instalar nada, necesitas entender la forma del sistema. Cada decision que tome fluye de esta arquitectura. Si entiendes la forma, puedes adaptar todo lo demas a tu propio hardware y caso de uso.

### El Layout de Tres Maquinas

```
                    ┌──────────────────────────────────┐
                    │           TU (Humano)             │
                    │     Telegram / Terminal / Web     │
                    └───────────────┬──────────────────┘
                                    │
                           (interfaz principal)
                                    │
                    ┌───────────────▼──────────────────┐
                    │       CEIBA (Maquina HQ)         │
                    │    Mac M4, 16GB, 192.168.X.100   │
                    │                                   │
                    │  - Claude Code CLI (cerebro)      │
                    │  - Agent Kernel (orquestador)     │
                    │  - Cola de tareas (inbox/active/done) │
                    │  - Sistema de memoria (knowledge DB)  │
                    │  - Ollama (qwen2.5:7b local)     │
                    │  - Pipeline de reels (TTS + SD)   │
                    └──────┬──────────────┬────────────┘
                           │              │
              ┌────────────┘              └────────────┐
              │  Syncthing (sync de archivos)           │
              │  HTTP Bridge (despacho de tareas)       │
              │                                        │
    ┌─────────▼──────────────┐         ┌───────────────▼──────────┐
    │     COBO (Worker #1)   │         │    HUTIA (Worker #2)     │
    │  Windows, GTX 1080 Ti  │         │    Nodo Siempre-On       │
    │  192.168.X.101         │         │    192.168.X.102          │
    │                        │         │                           │
    │  - Ollama (inferencia) │         │  - Tareas en background   │
    │  - n8n (automatizaciones)│       │  - Cron jobs              │
    │  - Bridge server       │         │  - Monitoreo             │
    │  - 11GB VRAM para GPU  │         │  - Siempre disponible    │
    │    inferencia           │         │                           │
    └────────────────────────┘         └───────────────────────────┘
```

### El Concepto Central: Pensar, Dirigir, Ejecutar

El sistema completo sigue un patron:

1. Una tarea entra al sistema (de ti, de un cron job, de otra tarea)
2. La maquina HQ decide que modelo y que maquina debe manejarla
3. La tarea se dirige al nodo apropiado
4. El resultado regresa, se almacena y puede generar nuevas tareas

Eso es todo. Todo lo demas es detalle de implementacion.

### Tres Carriles de Ruteo

Cada tarea en el sistema pasa por uno de tres carriles:

| Carril | Modelo | Maquina | Costo | Caso de Uso |
|--------|--------|---------|-------|-------------|
| FAST | Ollama (qwen2.5:7b) | Cobo o Ceiba | Gratis | Resumir, clasificar, formatear, extraer |
| WORKER | GPT-4o / LLM Pesado | Cobo | Pago (opcional) | Generacion de codigo, investigacion profunda, debugging |
| BRAIN | Claude Code | Ceiba | Incluido con CLI | Arquitectura, planificacion, sintesis final |

El carril FAST maneja 70-80% de todas las tareas. Por eso el sistema no cuesta nada. La mayoria del trabajo de IA no requiere GPT-4 o Claude. Requiere un modelo de 7B parametros que pueda seguir instrucciones. Esos corren gratis en hardware de consumidor.

### Cola de Tareas Basada en Archivos

No uso Redis. No uso RabbitMQ. No uso Kafka. La cola de tareas son archivos JSON en carpetas.

```
ai_cluster/
  tasks/
    inbox/      <-- Las tareas nuevas caen aqui
    active/     <-- Actualmente siendo procesadas
    done/       <-- Completadas con resultados
  memory/
    knowledge/  <-- Hechos que el sistema ha aprendido
    experiments/<-- Que funciono y que fallo
    projects/   <-- Contexto especifico de proyectos
    skills/     <-- Documentacion de comportamiento de skills
  kernel/
    agent_kernel.py   <-- El orquestador
  skills/
    registry.json     <-- Todas las capacidades registradas
```

Por que archivos en vez de una base de datos? Porque los archivos se sincronizan con Syncthing. Porque los archivos son legibles por humanos. Porque cuando algo se rompe a las 2 AM, puedo abrir una carpeta y ver exactamente que paso. Porque archivos JSON en una carpeta es la cola mas simple posible, y la simplicidad es lo que permite que una sola persona gestione un sistema distribuido.

---

## 3. Requisitos de Hardware

### Lo Que Realmente Uso

| Maquina | Rol | Specs | Costo |
|---------|-----|-------|-------|
| Ceiba (Mac M4) | HQ, cerebro, orquestador | Chip M4, 16GB RAM unificada, 256GB SSD | ~$1,200 |
| Cobo (PC Windows) | Worker GPU, bridge | GTX 1080 Ti (11GB VRAM), 16GB RAM | ~$600 usado |
| Hutia (Comp 3) | Background siempre-on | Specs basicas, siempre encendida | Ya la tenia |

Inversion total en hardware: las computadoras que ya tengas.

### Sistema Minimo Viable (1 Maquina)

Puedes empezar con una sola maquina. Honestamente, una computadora con 16GB de RAM puede correr el sistema completo menos la inferencia GPU. Aqui esta el minimo:

- **CPU:** Cualquier procesador moderno (M1+ Mac, Ryzen 5+, Intel i5+)
- **RAM:** 16GB minimo (8GB funciona pero lo vas a sentir)
- **Almacenamiento:** 50GB de espacio libre (los modelos ocupan espacio)
- **GPU:** Opcional pero util. Cualquier tarjeta NVIDIA con 6GB+ VRAM, o un Mac con Apple Silicon
- **Red:** Solo necesita llegar a internet para las descargas iniciales

### Build Economico (2 Maquinas, Menos de $400)

Si empiezas de cero:

- **Maquina 1 (HQ):** ThinkPad T480 usado o similar, $150-200. Corre el kernel, herramientas CLI y orquestacion.
- **Maquina 2 (Worker):** Desktop usado con GTX 1060 6GB o GTX 1070, $150-200. Corre Ollama para inferencia local.

Total: Menos de $400. Ambas maquinas en la misma red local.

### La Pregunta del GPU

No necesitas un GPU para empezar. Ollama corre en CPU. Es mas lento pero funciona. Un modelo de 7B en un CPU moderno genera aproximadamente 5-10 tokens por segundo. En un GPU, eso sube a 30-80 tokens por segundo.

Para referencia, esto es lo que diferentes GPUs pueden manejar:

| GPU | VRAM | Modelo Mas Grande | Tokens/seg (7B) |
|-----|------|-------------------|-----------------|
| GTX 1060 6GB | 6GB | 7B (justo) | ~25 |
| GTX 1080 Ti | 11GB | 13B comodo | ~35 |
| RTX 3060 12GB | 12GB | 13B comodo | ~40 |
| RTX 3090 | 24GB | 30B+ | ~50 |
| Mac M1/M2/M4 | Unificada | Depende del RAM | 20-40 |

Mi GTX 1080 Ti maneja qwen2.5:7b a unos 35 tokens por segundo. Eso es mas que suficiente para procesamiento de tareas en background.

### Nota sobre Apple Silicon

Si tienes un Mac con Apple Silicon (M1, M2, M3, M4), estas en buena posicion. La arquitectura de memoria unificada significa que tu GPU y CPU comparten el mismo pool de RAM. Un Mac M4 de 16GB puede correr modelos de 7B nativamente usando aceleracion Metal. Yo corro Ollama con qwen2.5:7b directamente en mi Mac como respaldo cuando Cobo esta offline.

Para generacion de imagenes, Apple Silicon soporta MLX Stable Diffusion, que genera imagenes localmente usando el GPU Metal 3. Sin necesidad de NVIDIA.

---

## 4. Stack de Software

Aqui esta cada pieza de software en el sistema, por que la escogi y a que se conecta.

### Modelos de IA e Inferencia

| Herramienta | Que Hace | Por Que La Escogi |
|-------------|----------|-------------------|
| **Ollama** | Servidor de inferencia LLM local | Gratis, simple, corre en cualquier lugar, REST API integrada |
| **qwen2.5:7b** | Modelo local principal | Mejor relacion calidad-tamano que he probado a 7B |
| **Claude Code CLI** | Motor de razonamiento principal | El mejor en planificacion compleja, arquitectura, generacion de codigo |
| **GPT-4o-mini** | Backend de BehiqueBot | API barata, bueno para clasificacion y respuestas cortas |

**Ollama** es la columna vertebral. Convierte cualquier maquina en un servidor de inferencia con un solo comando. Instalalo, descarga un modelo y tienes una REST API en `localhost:11434` que cualquier script puede llamar. Sin wrappers de Python necesarios, sin SDK, solo peticiones HTTP POST con JSON.

**Por que qwen2.5:7b?** Probe llama3.2, mistral, phi-3 y qwen2.5 en tamano 7B. Qwen2.5 produjo consistentemente el output mas estructurado y que mejor sigue instrucciones. Cuando tus tareas son automatizadas, necesitas un modelo que siga instrucciones de formato de manera confiable. Qwen2.5 hace eso.

### Automatizacion y Orquestacion

| Herramienta | Que Hace | Por Que La Escogi |
|-------------|----------|-------------------|
| **n8n** | Automatizacion visual de flujos de trabajo | Self-hosted, gratis, se conecta a todo |
| **Agent Kernel** | Orquestador de tareas en Python personalizado | Construido para exactamente mi caso de uso |
| **Shell scripts** | Despacho de tareas, cron jobs | Simples, portables, sin dependencias |
| **pm2** | Gestor de procesos | Mantiene los servicios vivos despues de crashes |

**n8n** corre en Cobo y maneja los flujos de trabajo que conectan servicios externos. Triggers de webhook, llamadas a API, transformaciones de datos. Es como Zapier pero self-hosted y gratis.

**El Agent Kernel** es un script de Python que yo escribi. Revisa una carpeta de inbox, dirige las tareas al modelo de IA correcto, procesa resultados y almacena aprendizajes en memoria. Unas 600 lineas de codigo. Te voy a mostrar el completo mas adelante.

### Capa de Comunicacion

| Herramienta | Que Hace | Por Que La Escogi |
|-------------|----------|-------------------|
| **Syncthing** | Sincronizacion de archivos | Gratis, peer-to-peer, sin nube, encriptado |
| **HTTP Bridge** | Ejecucion remota de comandos | Servidor Node.js personalizado con auth bearer |
| **Telegram Bot API** | Interfaz humana | Gratis, funciona en el telefono, soporta voz |
| **Cloudflare Tunnel** | Acceso externo | Gratis, seguro, sin port forwarding necesario |

**Syncthing** es el pegamento. Mantiene la carpeta `~/behique` sincronizada entre Ceiba y Cobo en tiempo real. Cuando Ceiba pone un archivo de tarea en la carpeta inbox, Syncthing lo copia a Cobo en segundos. Cuando Cobo escribe resultados, se sincronizan de vuelta. Sin servidor central requerido. Peer-to-peer, encriptado, y nunca me ha fallado.

**El HTTP Bridge** es un pequeno servidor de Node.js corriendo en Cobo. Acepta peticiones POST con un bearer token y ejecuta comandos de shell. Asi es como Ceiba envia comandos directos a Cobo sin esperar la sincronizacion de archivos.

### Produccion de Contenido

| Herramienta | Que Hace | Por Que La Escogi |
|-------------|----------|-------------------|
| **Kokoro TTS** | Narracion text-to-speech | Open source, corre localmente, formato ONNX |
| **MLX Stable Diffusion** | Generacion de imagenes en Mac | Nativo Apple Silicon, sin NVIDIA necesario |
| **FFmpeg** | Ensamblaje de video | Estandar de la industria, scripteable, gratis |

Mi pipeline de produccion de reels toma un archivo JSON de historia y produce un video terminado. Kokoro genera el audio de narracion. Stable Diffusion genera las imagenes. FFmpeg une todo con transiciones y timing. El pipeline completo corre en 3-4 minutos por reel a costo cero.

### Persistencia y Memoria

| Herramienta | Que Hace | Por Que La Escogi |
|-------------|----------|-------------------|
| **Notion** | Datos estructurados para BehiqueBot | Gran API, schema flexible, Ya en uso |
| **Memoria basada en archivos** | Persistencia de conocimiento de IA | Simple, sincronizable, legible por humanos |
| **Git** | Control de versiones e historial | Cada cambio esta rastreado y es reversible |

---

## 5. Configurando Tu Primera Maquina (HQ)

Este es el paso a paso para poner tu maquina principal a funcionar. Voy a asumir que estas en macOS o Linux. Las instrucciones de Windows son similares pero senalare las diferencias donde importen.

### Step 1: Instalar Ollama

```bash
# macOS / Linux
curl -fsSL https://ollama.com/install.sh | sh

# Verify installation
ollama --version
```

En Windows, descarga el instalador desde ollama.com.

### Step 2: Descargar Tu Primer Modelo

```bash
# Pull qwen2.5:7b (4.4 GB download)
ollama pull qwen2.5:7b

# Test it
ollama run qwen2.5:7b "What is 2+2? Reply in one word."
```

Si responde con "Four" o "4", tu inferencia local esta funcionando. Ahora tienes un modelo de IA gratis corriendo en tu maquina.

### Step 3: Hacer Ollama Accesible en Tu Red

Por defecto, Ollama solo escucha en localhost. Para que otras maquinas lo alcancen:

```bash
# macOS / Linux: Set environment variable
export OLLAMA_HOST=0.0.0.0

# Then restart Ollama
# On macOS, quit the Ollama app and reopen it
# On Linux:
systemctl restart ollama

# Verify it is accessible from another machine
# From another computer on your network:
curl http://YOUR_IP:11434/api/tags
```

Reemplaza `YOUR_IP` con la direccion IP local de tu maquina (como 192.168.X.100).

### Step 4: Configurar el Directorio del Proyecto

```bash
mkdir -p ~/behique
cd ~/behique

# Create the AI cluster directory structure
mkdir -p ai_cluster/tasks/{inbox,active,done}
mkdir -p ai_cluster/memory/{knowledge,experiments,projects,skills}
mkdir -p ai_cluster/kernel
mkdir -p ai_cluster/skills
mkdir -p bridge
mkdir -p tools

# Initialize git
git init
```

### Step 5: Instalar Dependencias de Python

```bash
# Create a virtual environment (optional but recommended)
python3 -m venv ~/.venvs/behique
source ~/.venvs/behique/bin/activate

# Install what the kernel needs
pip install requests
```

Eso es todo. El agent kernel solo necesita `requests` para llamadas HTTP. Mantengo las dependencias minimas a proposito.

### Step 6: Crear el Agent Kernel

Crea el archivo `ai_cluster/kernel/agent_kernel.py`. Aqui esta la estructura central:

```python
#!/usr/bin/env python3
"""
Agent Kernel - Distributed AI Task Orchestrator
Polls an inbox folder for JSON task files, routes them to
the appropriate AI model, and stores results.
"""

import os
import json
import time
import uuid
import re
import requests
from pathlib import Path
from datetime import datetime

# === CONFIG ===
ROOT = Path(__file__).resolve().parent.parent
TASK_INBOX = ROOT / "tasks" / "inbox"
TASK_ACTIVE = ROOT / "tasks" / "active"
TASK_DONE = ROOT / "tasks" / "done"
MEMORY_DIR = ROOT / "memory"

# AI endpoints - adjust these IPs to match your network
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:7b"

BRIDGE_URL = "http://192.168.X.101:9876"  # Worker machine
BRIDGE_TOKEN = os.getenv("BRIDGE_TOKEN", "")

POLL_INTERVAL = 3  # seconds


def generate_task_id():
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    short = uuid.uuid4().hex[:6]
    return f"{ts}-{short}"


def run_ollama(prompt):
    """Send prompt to Ollama. Free and fast."""
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    }
    try:
        r = requests.post(OLLAMA_URL, json=payload, timeout=120)
        return r.json().get("response", "")
    except Exception as e:
        return f"[OLLAMA ERROR] {e}"


def memory_search(query, limit=5):
    """Search memory files for relevant context."""
    results = []
    query_words = set(query.lower().split())

    for mem_dir in MEMORY_DIR.iterdir():
        if not mem_dir.is_dir():
            continue
        for f in mem_dir.glob("*.md"):
            try:
                text = f.read_text()
                score = sum(1 for w in query_words if w in text.lower())
                if score > 0:
                    results.append((score, text[:500], f.name))
            except Exception:
                pass

    results.sort(key=lambda x: x[0], reverse=True)
    return results[:limit]


def route_task(objective):
    """Decide which AI model handles this task."""
    obj = objective.lower()

    cheap_keywords = [
        "summarize", "format", "extract", "classify",
        "clean", "list", "count", "score", "simple", "quick"
    ]

    for kw in cheap_keywords:
        if kw in obj:
            return "ollama"

    return "ollama"  # Default to free. Change to "bridge" for paid.


def execute_task(task_data):
    """Build prompt, inject memory, route to AI, return output."""
    objective = task_data.get("objective", "")
    context = task_data.get("context", "")

    # Search memory for relevant context
    memories = memory_search(objective)
    memory_text = ""
    if memories:
        memory_text = "\nRelevant knowledge:\n"
        for score, text, name in memories:
            memory_text += f"- [{name}] {text}\n"

    prompt = f"""You are an AI worker in a distributed system.

Objective: {objective}
Context: {context}
{memory_text}

Respond in JSON:
{{
  "result": "your answer here",
  "memory_write": [],
  "spawn_tasks": []
}}

If you learn something useful, add to memory_write:
{{"type": "knowledge", "content": "what you learned"}}
"""

    route = route_task(objective)

    if route == "ollama":
        raw = run_ollama(prompt)
    else:
        raw = run_ollama(prompt)  # Fallback to Ollama

    # Parse response
    try:
        match = re.search(r'\{[\s\S]*\}', raw)
        if match:
            parsed = json.loads(match.group())
        else:
            parsed = {"result": raw}
    except Exception:
        parsed = {"result": raw}

    # Store memory writes
    for entry in parsed.get("memory_write", []):
        store_memory(entry)

    return parsed


def store_memory(entry):
    """Persist a knowledge entry to disk."""
    mem_type = entry.get("type", "knowledge")
    content = entry.get("content", "")
    if not content:
        return

    target = MEMORY_DIR / mem_type
    target.mkdir(parents=True, exist_ok=True)

    slug = re.sub(r'[^a-z0-9]+', '-', content[:50].lower()).strip('-')
    path = target / f"{slug}.md"
    path.write_text(content)


def main():
    """Main loop: poll inbox, process tasks, store results."""
    print(f"Agent Kernel started. Watching: {TASK_INBOX}")

    while True:
        tasks = sorted(TASK_INBOX.glob("*.json"))

        if not tasks:
            time.sleep(POLL_INTERVAL)
            continue

        task_file = tasks[0]
        print(f"Processing: {task_file.name}")

        # Move to active
        active_path = TASK_ACTIVE / task_file.name
        task_file.rename(active_path)

        # Load and execute
        task_data = json.loads(active_path.read_text())
        result = execute_task(task_data)

        # Save to done
        result["task_id"] = task_data.get("task_id", task_file.stem)
        result["completed"] = datetime.now().isoformat()

        done_path = TASK_DONE / task_file.name
        done_path.write_text(json.dumps(result, indent=2))

        # Clean up active
        if active_path.exists():
            active_path.unlink()

        print(f"Done: {result.get('result', '')[:100]}")
        print("---")


if __name__ == "__main__":
    main()
```

### Step 7: Probar el Kernel

```bash
# Submit a test task
cat > ~/behique/ai_cluster/tasks/inbox/test-001.json << 'EOF'
{
  "task_id": "test-001",
  "objective": "Summarize the benefits of local AI inference in 3 bullet points",
  "context": "This is a test task for the agent kernel",
  "model_preference": ["ollama"]
}
EOF

# Run the kernel
python3 ~/behique/ai_cluster/kernel/agent_kernel.py
```

Deberias ver el kernel recoger la tarea, dirigirla a Ollama y escribir el resultado en la carpeta `done`. Revisa `ai_cluster/tasks/done/test-001.json` para ver el output.

### Step 8: Crear el Script de Despacho

Este es un atajo rapido para enviar tareas a diferentes modelos de IA desde la linea de comandos:

```bash
cat > ~/behique/bridge/dispatch.sh << 'SCRIPT'
#!/bin/bash
# Quick dispatch to different AI lanes
# Usage: bash dispatch.sh <fast|worker|brain> <prompt>

OLLAMA_URL="http://localhost:11434/api/generate"

LANE="$1"
shift
PROMPT="$*"

if [ -z "$LANE" ] || [ -z "$PROMPT" ]; then
  echo "Usage: dispatch.sh <fast|worker|brain> <prompt>"
  exit 1
fi

case "$LANE" in
  fast)
    JSON=$(python3 -c "import json,sys; print(json.dumps({
      'model':'qwen2.5:7b',
      'prompt':sys.argv[1],
      'stream':False
    }))" "$PROMPT")
    curl -s -X POST "$OLLAMA_URL" \
      -H "Content-Type: application/json" \
      -d "$JSON" \
      | python3 -c "import sys,json; print(json.load(sys.stdin)['response'])"
    ;;
  worker)
    echo "[WORKER] Route to remote GPU node"
    echo "Prompt: $PROMPT"
    ;;
  brain)
    echo "[BRAIN] This stays on HQ for deep reasoning"
    echo "Prompt: $PROMPT"
    ;;
esac
SCRIPT

chmod +x ~/behique/bridge/dispatch.sh
```

Pruebalo:

```bash
bash ~/behique/bridge/dispatch.sh fast "What is the capital of France? One word."
```

Felicidades. Tienes un empleado de IA funcionando en una maquina. Puede aceptar tareas, dirigirlas a un modelo local, ejecutarlas y almacenar los resultados. Todo de aqui en adelante construye sobre este fundamento.

---

## 6. Agregando Nodos de Trabajo

Una maquina esta bien. Dos maquinas son un multiplicador de fuerza. Aqui esta como convertir una segunda computadora en un nodo de trabajo.

### Por Que Agregar una Segunda Maquina?

Tres razones:

1. **Ejecucion paralela.** Mientras tu maquina HQ esta haciendo planificacion compleja, el worker puede estar procesando una cola de tareas simples.
2. **Descarga de GPU.** Si tu worker tiene un GPU dedicado, maneja la inferencia mas rapido que tu CPU.
3. **Capacidad siempre-on.** Tu HQ podria ser tu laptop que cierras y cargas. Un worker de escritorio se queda corriendo 24/7.

### Configuracion del Worker (Linux o Windows)

#### Instalar Ollama en el Worker

Mismo proceso que el HQ:

```bash
# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Pull the model
ollama pull qwen2.5:7b

# Make it accessible on the network
export OLLAMA_HOST=0.0.0.0
```

En Windows, instala Ollama desde el sitio web. Se vincula a todas las interfaces por defecto.

Verifica desde tu maquina HQ:

```bash
curl http://WORKER_IP:11434/api/tags
```

#### Instalar n8n (Opcional pero Poderoso)

n8n te da automatizacion visual de flujos de trabajo. Instalalo con npm:

```bash
npm install -g n8n

# Run it
n8n start

# Or use pm2 to keep it alive
npm install -g pm2
pm2 start n8n
pm2 save
```

n8n estara disponible en `http://WORKER_IP:5678`. Puedes construir flujos de trabajo que se activen con webhooks, procesen datos, llamen APIs y alimenten resultados de vuelta a tu cola de tareas.

#### Configurar el Bridge Server

El bridge server es un servidor HTTP ligero que permite a tu maquina HQ ejecutar comandos en el worker remotamente. Aqui esta una implementacion minima en Node.js:

```javascript
// bridge-server.js
const http = require('http');
const { exec } = require('child_process');

const PORT = 9876;
const AUTH_TOKEN = process.env.BRIDGE_TOKEN || 'your-secret-token-here';

const server = http.createServer((req, res) => {
  // Only accept POST
  if (req.method !== 'POST') {
    res.writeHead(405);
    res.end('Method not allowed');
    return;
  }

  // Check auth
  const auth = req.headers['authorization'];
  if (auth !== `Bearer ${AUTH_TOKEN}`) {
    res.writeHead(401);
    res.end('Unauthorized');
    return;
  }

  let body = '';
  req.on('data', chunk => body += chunk);
  req.on('end', () => {
    try {
      const { command } = JSON.parse(body);

      exec(command, { timeout: 300000 }, (error, stdout, stderr) => {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
          stdout: stdout || '',
          stderr: stderr || '',
          exitCode: error ? error.code : 0
        }));
      });
    } catch (e) {
      res.writeHead(400);
      res.end(JSON.stringify({ error: e.message }));
    }
  });
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`Bridge server running on port ${PORT}`);
});
```

Correlo:

```bash
# Set a secure token
export BRIDGE_TOKEN="generate-a-random-string-here"

# Start with pm2
pm2 start bridge-server.js --name bridge
pm2 save
```

**Nota de seguridad:** Este bridge server ejecuta comandos arbitrarios. Solo correlo en una red local de confianza. El bearer token provee autenticacion basica. Para uso en produccion, agrega HTTPS y whitelist de IPs.

#### Probar el Bridge

Desde tu maquina HQ:

```bash
curl -s -X POST http://WORKER_IP:9876 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-secret-token-here" \
  -d '{"command": "ollama list"}'
```

Deberias ver una respuesta JSON con el output del comando. Si funciona, tu HQ ahora puede ejecutar comandos en el worker.

### Agregando Hutia (El Nodo Siempre-On)

Mi tercera maquina, Hutia, sirve un proposito diferente a Cobo. No es una potencia de GPU. Simplemente esta siempre encendida. Esto es lo que te da el siempre-on:

- **Cron jobs que realmente corren.** Las tareas programadas necesitan una maquina que no duerma.
- **Monitoreo.** Health checks en otras maquinas, alertas cuando algo se cae.
- **Procesamiento en background.** Tareas de larga duracion que toman horas.
- **Hosting del bot de Telegram.** Tu bot siempre es alcanzable.

La configuracion es identica a un nodo worker. Instala Ollama (incluso un modelo pequeno es util), configura Syncthing y configuralo como un ejecutor de tareas en background.

---

## 7. Comunicacion Entre Maquinas

Esta es la parte que la mayoria de la gente hace mal. Intentan construir una arquitectura compleja de microservicios con colas de mensajes y descubrimiento de servicios. No necesitas nada de eso. Necesitas dos cosas: sincronizacion de archivos y un bridge HTTP.

### Syncthing: La Columna Vertebral

Syncthing mantiene carpetas sincronizadas entre maquinas en tiempo real. Sin servidor en la nube, sin cuenta, peer-to-peer, encriptado. Instalalo en cada maquina de tu flota.

#### Instalacion

```bash
# macOS
brew install syncthing

# Linux (Debian/Ubuntu)
sudo apt install syncthing

# Windows
# Download from syncthing.net
```

#### Configuracion

1. Inicia Syncthing en cada maquina. Abre una interfaz web en `http://localhost:8384`.
2. En cada maquina, anota el Device ID (una cadena larga en Settings > Show ID).
3. En la Maquina A, agrega la Maquina B como dispositivo remoto usando su Device ID.
4. En la Maquina B, acepta la conexion de la Maquina A.
5. Comparte la carpeta `~/behique` entre ambas maquinas.

Esa es toda la configuracion. Ahora cuando pones un archivo en `~/behique/ai_cluster/tasks/inbox/` en tu Mac, aparece en tu PC Windows en segundos.

#### Lo Que Sincronizo

```
~/behique/           <-- The entire project folder
  ai_cluster/        <-- Task queue, memory, kernel
  bridge/            <-- Dispatch scripts, task specs
  tools/             <-- Shared tools and pipelines
  Ceiba/             <-- Knowledge vault
```

#### Lo Que NO Sincronizo

Archivos grandes de modelos, outputs temporales, entornos virtuales. Agrega un archivo `.stignore`:

```
# .stignore
.venv
__pycache__
*.pyc
node_modules
*.onnx
*.bin
output/
.git
```

### El HTTP Bridge: Comandos Directos

La sincronizacion de archivos es genial para trabajo asincrono. Pero a veces necesitas una respuesta ahora. Para eso es el bridge.

El bridge server (mostrado en el capitulo anterior) corre en tu nodo worker y acepta peticiones HTTP. Tu maquina HQ envia comandos y recibe resultados de vuelta inmediatamente.

Asi es como el script de despacho usa ambos canales:

```bash
# FAST lane: Direct Ollama call to worker's GPU
bash dispatch.sh fast "Classify this product: Nike Air Max 90"

# Response comes back in ~2 seconds via HTTP
```

Versus la cola basada en archivos:

```bash
# Submit task to inbox (async, processed whenever)
cat > ai_cluster/tasks/inbox/classify-001.json << 'EOF'
{
  "task_id": "classify-001",
  "objective": "Classify these 50 products into categories",
  "context": "See products.csv in the project folder"
}
EOF

# Syncthing delivers it to the worker
# Kernel picks it up and processes it
# Result appears in tasks/done/ via Syncthing
```

### Relay del Bot de Telegram

BehiqueBot corre en Railway (nivel gratuito) y actua como mi interfaz humana al sistema. Le envio un mensaje de voz mientras camino a clase, y el:

1. Transcribe el audio usando OpenAI Whisper
2. Clasifica la idea (CREATIVE, BUSINESS, KNOWLEDGE, PERSONAL, TECHNICAL)
3. Le pone un tag de pilar de vida (salud, riqueza, relaciones, general)
4. Guarda un registro semilla en Notion
5. Me envia una confirmacion

Tambien le puedo enviar comandos de texto que se dirigen al agent kernel. El bot es el puente entre mi telefono y el sistema distribuido.

### Cloudflare Tunnel (Opcional)

Si quieres acceder a tu sistema desde fuera de tu red casera (para webhooks, monitoreo remoto o acceso movil), Cloudflare Tunnel te da una URL publica segura gratis:

```bash
# Install cloudflared
brew install cloudflared  # or apt install cloudflared

# Create a named tunnel
cloudflared tunnel create behique-bridge

# Route traffic
cloudflared tunnel route dns behique-bridge bridge.yourdomain.com

# Run it
cloudflared tunnel run --url http://localhost:9876 behique-bridge
```

Ahora `https://bridge.yourdomain.com` dirige a tu bridge server local con HTTPS completo. Sin port forwarding, sin IPs expuestas.

---

## 8. Configuracion de Agentes

Un "agente" en este sistema no es un ser autonomo magico. Es una plantilla de prompt mas una regla de ruteo mas un conjunto de herramientas que puede acceder. Asi es como se configuran.

### El Protocolo de Tareas (AI-TASK v1)

Cada tarea en el sistema sigue este schema JSON:

```json
{
  "task_id": "20260315-143022-a8f3c1",
  "parent_task": null,
  "objective": "What needs to be done, in one clear sentence",
  "context": "Background information the model needs",
  "model_preference": ["ollama", "gpt4o", "claude"],
  "spawn_allowed": true,
  "deliverables": ["analysis", "code", "summary"]
}
```

**task_id** se genera automaticamente (timestamp + hex aleatorio). **parent_task** vincula subtareas a su padre para tracking. **model_preference** le dice al kernel que IA probar primero. **spawn_allowed** controla si la tarea puede crear tareas hijas autonomamente.

### Configurando el Ruteo de Modelos

El kernel dirige tareas basado en dos cosas: preferencia explicita y coincidencia de palabras clave.

```python
# Keywords that trigger free (Ollama) routing
CHEAP_KEYWORDS = [
    "summarize", "format", "extract", "classify", "clean",
    "list", "count", "evaluate", "score", "review output",
    "simple", "quick", "translate", "rewrite"
]

# Keywords that trigger heavy (paid API) routing
HEAVY_KEYWORDS = [
    "design", "architect", "debug", "implement", "code",
    "build", "analyze deeply", "research", "create module",
    "write function", "fix bug", "refactor", "plan"
]
```

Puedes personalizar estas listas para que coincidan con tus patrones de uso. Si encuentras que Ollama maneja tareas de codigo lo suficientemente bien para tus necesidades, mueve "code" a la lista barata. El objetivo es usar el modelo mas barato que produzca output aceptable.

### Personas de Agentes

Para diferentes tipos de trabajo, configuro diferentes system prompts. Estos no son agentes separados. Son plantillas de prompt que el kernel selecciona basado en el tipo de tarea.

```python
PERSONAS = {
    "researcher": """You are a thorough researcher. Find specific,
    actionable information. Cite sources when possible. Focus on
    practical applications, not theory.""",

    "coder": """You are a senior developer. Write clean, working code.
    Include error handling. Keep functions small. Add comments only
    where the logic is not obvious.""",

    "analyst": """You are a data analyst. Extract patterns from data.
    Present findings in structured formats. Flag anomalies. Be specific
    about numbers.""",

    "writer": """You are a content writer. Match the specified tone.
    Keep sentences short. Use active voice. Every paragraph should
    advance the argument.""",
}
```

El kernel selecciona una persona basado en palabras clave en el objetivo:

```python
def select_persona(objective):
    obj = objective.lower()
    if any(w in obj for w in ["research", "find", "discover", "investigate"]):
        return PERSONAS["researcher"]
    if any(w in obj for w in ["code", "implement", "build", "fix", "debug"]):
        return PERSONAS["coder"]
    if any(w in obj for w in ["analyze", "data", "metrics", "pattern"]):
        return PERSONAS["analyst"]
    if any(w in obj for w in ["write", "draft", "content", "copy"]):
        return PERSONAS["writer"]
    return ""  # No persona, generic prompt
```

### El Registro de Skills

Los skills son capacidades reutilizables que el sistema rastrea y mejora con el tiempo. El registro es un simple archivo JSON:

```json
{
  "skills": [
    {
      "name": "product_research",
      "description": "Research eBay/Amazon products and generate listings",
      "version": 2,
      "score": 0.78
    },
    {
      "name": "content_writing",
      "description": "Generate social media posts and long-form content",
      "version": 1,
      "score": 0.85
    },
    {
      "name": "code_generation",
      "description": "Write Python scripts and shell automation",
      "version": 3,
      "score": 0.72
    }
  ]
}
```

El campo score (0 a 1) rastrea que tan bien rinde cada skill. Los skills con puntaje bajo se priorizan para mejora. Este es un proceso manual por ahora. Reviso outputs, ajusto el puntaje e itero en las plantillas de prompt. Lo importante es que el tracking exista. Sin medicion, no puedes mejorar.

---

## 9. Framework de Delegacion de Tareas

Saber como configurar agentes es una cosa. Saber que delegar y como estructurar la delegacion es donde la mayoria de la gente falla. Aqui esta mi framework.

### El Arbol de Decision de Delegacion

Antes de crear una tarea, me hago tres preguntas:

1. **Puede Ollama manejar esto?** Si si, dirigela al carril gratis. La mayoria de las tareas son mas simples de lo que piensas.
2. **Necesita datos externos?** Si si, podria necesitar una llamada a API o acceso web, lo que cambia el ruteo.
3. **El output necesita ser perfecto, o solo lo suficientemente bueno?** Perfecto va a Claude. Lo suficientemente bueno va a Ollama.

### Descomposicion de Tareas

La habilidad mas importante para delegar a IA es descomponer tareas grandes en pequenas. Un agente de IA no puede "construyeme un sitio web." Pero si puede:

1. Generar una lista de paginas necesarias para el sitio
2. Escribir el HTML para el componente de header
3. Escribir el CSS para la paleta de colores
4. Generar copy para la landing page
5. Crear el markup del formulario de contacto

Cada una de esas es una tarea unica y clara que un modelo de 7B puede manejar.

### La Plantilla de Tareas

Cada tarea que creo sigue este patron:

```
OBJECTIVE: [One sentence. What needs to be done.]
CONTEXT: [What the model needs to know to do it well.]
FORMAT: [Exactly how the output should be structured.]
CONSTRAINTS: [What to avoid, length limits, style rules.]
```

Ejemplo:

```json
{
  "task_id": "listing-042",
  "objective": "Write an eBay product description for Nike Air Max 90",
  "context": "Product is used, size 10, white/black colorway, 8/10 condition. Selling for $85. Target audience is sneaker collectors.",
  "model_preference": ["ollama"],
  "deliverables": ["title", "description", "bullet_points"]
}
```

### Procesamiento por Lotes

El verdadero poder de este sistema es el procesamiento por lotes. En vez de hacer una pregunta a la vez, creo 10, 20 o 50 tareas y las pongo todas en el inbox. El kernel las procesa secuencialmente (o en paralelo si corres multiples instancias del kernel).

```bash
# Generate 20 product research tasks
for product in "Nike Air Max" "Vintage Levi's" "Pokemon Cards" "AirPods Pro"; do
  cat > ai_cluster/tasks/inbox/research-$(date +%s%N | md5 | head -c6).json << EOF
  {
    "objective": "Research $product on eBay. Find avg selling price, demand level, best listing keywords.",
    "model_preference": ["ollama"],
    "context": "Product research for dropshipping evaluation."
  }
EOF
done
```

Veinte tareas, enviadas en segundos, procesadas sin que yo toque nada.

### Generacion de Subtareas

El kernel soporta creacion autonoma de subtareas. Cuando la respuesta de una tarea incluye un array `spawn_tasks`, el kernel crea nuevas tareas automaticamente:

```json
{
  "result": "Identified 5 high-demand product categories",
  "spawn_tasks": [
    {
      "objective": "Deep-dive research on vintage denim market",
      "model_preference": ["ollama"]
    },
    {
      "objective": "Analyze Pokemon card grading requirements",
      "model_preference": ["ollama"]
    }
  ]
}
```

La tarea padre termina, y dos tareas hijas aparecen en el inbox. Asi es como una tarea se convierte en un arbol de investigacion sin intervencion humana.

Pon `spawn_allowed: true` en la tarea padre para habilitar esto. Recomiendo ser conservador con la generacion al principio. Una IA que puede crear sus propias tareas puede crear muchas muy rapido si no tienes cuidado.

---

## 10. Construyendo Tu Primera Automatizacion

Vamos a construir algo real. Te voy a guiar a crear un pipeline de contenido automatizado que toma un tema, lo investiga, escribe un post de redes sociales y guarda el resultado. Todo corriendo localmente, todo gratis.

### El Pipeline de Generacion de Contenido

Esto es lo que estamos construyendo:

```
Topic (input)
    -> Research task (Ollama)
        -> Writing task (Ollama)
            -> Formatting task (Ollama)
                -> Final output (saved to disk)
```

### Step 1: Crear el Script del Pipeline

```python
#!/usr/bin/env python3
"""
content_pipeline.py - Automated content generation
Takes a topic, researches it, writes a post, formats it.
"""

import json
import time
import requests
from pathlib import Path
from datetime import datetime

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:7b"
OUTPUT_DIR = Path.home() / "behique" / "output" / "content"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def ask_ollama(prompt):
    """Send a prompt to Ollama and return the response."""
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
    }
    r = requests.post(OLLAMA_URL, json=payload, timeout=120)
    return r.json().get("response", "")


def research(topic):
    """Step 1: Generate research notes on the topic."""
    prompt = f"""Research the following topic and provide 5 key facts
that would be interesting for a social media audience.

Topic: {topic}

Format your response as a numbered list. Focus on surprising,
counterintuitive, or practical information. No fluff."""

    print(f"[1/3] Researching: {topic}")
    return ask_ollama(prompt)


def write_post(topic, research_notes):
    """Step 2: Write a social media post using the research."""
    prompt = f"""Write an Instagram caption about this topic.

Topic: {topic}
Research notes:
{research_notes}

Rules:
- Start with a hook (question or bold statement)
- Keep it under 200 words
- Include 3-5 relevant hashtags at the end
- Conversational tone, not corporate
- End with a call to action"""

    print("[2/3] Writing post...")
    return ask_ollama(prompt)


def format_output(topic, research_notes, post):
    """Step 3: Package everything into a clean output."""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    slug = topic.lower().replace(" ", "-")[:30]

    output = {
        "topic": topic,
        "research": research_notes,
        "post": post,
        "generated_at": timestamp,
        "model": MODEL,
        "cost": "$0.00"
    }

    filename = f"{timestamp}-{slug}.json"
    output_path = OUTPUT_DIR / filename

    output_path.write_text(json.dumps(output, indent=2))
    print(f"[3/3] Saved to: {output_path}")

    return output_path


def run_pipeline(topic):
    """Run the full content pipeline."""
    start = time.time()

    notes = research(topic)
    post = write_post(topic, notes)
    path = format_output(topic, notes, post)

    elapsed = time.time() - start
    print(f"\nDone in {elapsed:.1f} seconds. Cost: $0.00")
    print(f"Output: {path}")

    return path


if __name__ == "__main__":
    import sys
    topic = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "local AI inference"
    run_pipeline(topic)
```

### Step 2: Correlo

```bash
python3 content_pipeline.py "how to build an AI employee for free"
```

Output:

```
[1/3] Researching: how to build an AI employee for free
[2/3] Writing post...
[3/3] Saved to: /Users/you/behique/output/content/20260315-143022-how-to-build-an-ai-employee.json

Done in 24.3 seconds. Cost: $0.00
```

### Step 3: Procesalo por Lotes

```bash
# Run 5 topics in sequence
topics=(
  "why local AI beats cloud AI"
  "the $0 startup toolkit"
  "how I automated my side hustle"
  "building an AI agent with Python"
  "the future of personal AI assistants"
)

for topic in "${topics[@]}"; do
  python3 content_pipeline.py "$topic"
  echo ""
done
```

Cinco piezas de contenido, generadas en aproximadamente dos minutos, completamente gratis. Ahora imagina corriendo esto cada manana como un cron job. Para cuando te despiertas, cinco posts nuevos estan esperandote para revisar y publicar.

### Step 4: Agregalo al Kernel

Para hacer esto un skill adecuado en el sistema, envuelvelo como un handler de tareas:

```bash
# Submit as a kernel task
cat > ~/behique/ai_cluster/tasks/inbox/content-batch-001.json << 'EOF'
{
  "task_id": "content-batch-001",
  "objective": "Generate social media content about local AI inference benefits",
  "context": "Target audience: developers and tech entrepreneurs. Platform: Instagram. Tone: conversational, educational.",
  "model_preference": ["ollama"],
  "spawn_allowed": true
}
EOF
```

---

## 11. Monitoreo y Mantenimiento

Un sistema distribuido necesita monitoreo. No monitoreo nivel enterprise de Datadog. Checks simples y practicos que te digan si algo esta roto.

### Script de Health Check

```bash
#!/bin/bash
# health_check.sh - Check all nodes in the fleet

echo "=== Behique Fleet Health Check ==="
echo "Time: $(date)"
echo ""

# Check Ceiba (local)
echo "[Ceiba - HQ]"
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
  echo "  Ollama: UP"
else
  echo "  Ollama: DOWN"
fi

# Check Cobo (worker)
echo "[Cobo - Worker]"
if curl -s --connect-timeout 3 http://192.168.X.101:11434/api/tags > /dev/null 2>&1; then
  echo "  Ollama: UP"
else
  echo "  Ollama: DOWN"
fi

if curl -s --connect-timeout 3 http://192.168.X.101:9876 > /dev/null 2>&1; then
  echo "  Bridge: UP"
else
  echo "  Bridge: DOWN"
fi

if curl -s --connect-timeout 3 http://192.168.X.101:5678 > /dev/null 2>&1; then
  echo "  n8n: UP"
else
  echo "  n8n: DOWN"
fi

# Check Hutia (always-on)
echo "[Hutia - Background]"
if ping -c 1 -W 2 192.168.X.102 > /dev/null 2>&1; then
  echo "  Network: UP"
else
  echo "  Network: DOWN"
fi

# Task queue status
echo ""
echo "[Task Queue]"
INBOX=$(ls ~/behique/ai_cluster/tasks/inbox/*.json 2>/dev/null | wc -l)
ACTIVE=$(ls ~/behique/ai_cluster/tasks/active/*.json 2>/dev/null | wc -l)
DONE=$(ls ~/behique/ai_cluster/tasks/done/*.json 2>/dev/null | wc -l)
echo "  Inbox:  $INBOX"
echo "  Active: $ACTIVE"
echo "  Done:   $DONE"

# Disk space
echo ""
echo "[Disk Space]"
df -h / | tail -1 | awk '{print "  Used: " $5 " of " $2}'
```

Correlo manualmente o agregalo a un cron job:

```bash
# Check health every 30 minutes
crontab -e
# Add: */30 * * * * bash ~/behique/tools/health_check.sh >> ~/behique/logs/health.log 2>&1
```

### Rotacion de Logs

El kernel y la cola de tareas generan archivos. Sin control, la carpeta `done` se llena. Limpia tareas viejas periodicamente:

```bash
# Archive tasks older than 7 days
find ~/behique/ai_cluster/tasks/done -name "*.json" -mtime +7 \
  -exec mv {} ~/behique/ai_cluster/tasks/archive/ \;
```

### Monitoreo de Syncthing

Syncthing tiene una interfaz web integrada en `http://localhost:8384`. Revisala periodicamente para asegurarte de que todas las maquinas esten conectadas y sincronizadas. El problema mas comun es una maquina desconectandose y acumulando un backlog de sincronizacion. Cuando vuelve a conectarse, Syncthing maneja la sincronizacion automaticamente, pero backlogs grandes pueden tomar unos minutos.

### Gestion de Procesos con pm2

En maquinas corriendo servicios (bridge server, n8n, Ollama en Linux), usa pm2 para mantenerlos vivos:

```bash
# Check all managed processes
pm2 status

# Restart a crashed service
pm2 restart bridge

# View logs
pm2 logs bridge --lines 50

# Auto-start on system boot
pm2 startup
pm2 save
```

### El Dashboard (Opcional)

Construi un dashboard HTML simple que muestra el estado de todas las maquinas. Se sirve con el servidor HTTP integrado de Python:

```bash
cd ~/behique/Ceiba/faces && python3 -m http.server 8091 --bind 0.0.0.0
```

Accesible en `http://192.168.X.100:8091` desde cualquier dispositivo en la red. Muestra estado de agentes, conteos de la cola de tareas y completaciones recientes. Esto es opcional pero util cuando quieres revisar el sistema desde tu telefono.

---

## 12. Desglose de Costos

Esta es la seccion de la que estoy mas orgulloso. Aqui estan los numeros reales.

### Costos Operativos Mensuales

| Servicio | Costo | Notas |
|----------|-------|-------|
| Inferencia Ollama | $0 | Corre en tu hardware |
| Sync con Syncthing | $0 | Peer-to-peer, sin nube |
| Automatizacion n8n | $0 | Self-hosted |
| Agent Kernel | $0 | Script de Python |
| Bridge server | $0 | Node.js en tu maquina |
| Telegram Bot API | $0 | Nivel gratuito |
| Cloudflare Tunnel | $0 | Nivel gratuito |
| Electricidad | ~$5-15 | Depende de tus maquinas |
| **Total** | **~$5-15** | **Solo electricidad** |

### Lo Que Pago (Opcional)

| Servicio | Costo | Por Que |
|----------|-------|---------|
| Claude Code CLI | $20/mes | Motor de razonamiento principal, vale cada centavo |
| Railway (BehiqueBot) | $0 (nivel gratuito) | Hosting del bot, uso minimo |
| Notion | $0 (nivel gratuito) | Base de datos para BehiqueBot |
| Nombre de dominio | ~$10/ano | Para el tunnel de Cloudflare |

La suscripcion de Claude Code es el unico gasto real, y es opcional. Puedes construir el sistema completo usando solo Ollama para inferencia. Claude Code es mi multiplicador de fuerza para tareas complejas, pero el sistema funciona sin el.

### Comparacion con Alternativas en la Nube

Si corriera esta misma carga de trabajo en servicios de nube:

| Servicio | Costo Mensual Estimado |
|----------|----------------------|
| AWS EC2 (instancia GPU) | $200-800 |
| API de OpenAI (uso equivalente) | $50-200 |
| Zapier (automatizacion de flujos) | $20-50 |
| Almacenamiento en nube | $5-10 |
| Hosting de bot gestionado | $10-25 |
| **Total** | **$285-1,085/mes** |

Mi sistema hace el mismo trabajo por $5-15/mes en electricidad. En un ano, eso es un ahorro de $3,000 a $12,000. El hardware se paga solo en el primer mes.

### El Costo Real: Tu Tiempo

Voy a ser honesto. El costo real de este sistema es el tiempo que toma construirlo y mantenerlo. Pase semanas haciendo que todo funcione. Ese es tiempo que podria haber pasado en otras cosas.

Pero aqui esta la diferencia. Ese tiempo lo gaste una vez. El sistema corre todos los dias. Los servicios de nube cuestan dinero cada mes para siempre. Mi sistema cuesta tiempo por adelantado y luego corre gratis.

Si sigues esta guia, puedes reducir ese tiempo de configuracion a un fin de semana para lo basico. Una semana si quieres la flota completa.

---

## 13. Resolucion de Problemas

Aqui estan los problemas que encontre y como los arregle.

### Ollama No Arranca

**Sintoma:** `ollama serve` se cuelga o crashea.

**Solucion:** Verifica si otra instancia ya esta corriendo.

```bash
# Kill existing instances
pkill ollama

# Check if the port is in use
lsof -i :11434

# Start fresh
ollama serve
```

En macOS, la app de Ollama corre un servicio en background. Si tambien estas tratando de correr `ollama serve` manualmente, van a tener conflicto. Usa uno o el otro.

### Modelo Demasiado Grande para la RAM

**Sintoma:** Ollama dice "out of memory" o el sistema se vuelve irresponsivo.

**Solucion:** Usa un modelo mas pequeno o cuantizacion.

```bash
# Instead of the full model, try a quantized version
ollama pull qwen2.5:7b-q4_0

# Or use a smaller model entirely
ollama pull phi-3:mini
```

Los modelos de 7B necesitan aproximadamente 4-8GB de RAM dependiendo de la cuantizacion. Si solo tienes 8GB en total, cierra otras aplicaciones mientras corres inferencia.

### Syncthing No Sincroniza

**Sintoma:** Los archivos en una maquina no aparecen en la otra.

**Soluciones:**

1. Revisa que ambas maquinas esten online en la interfaz de Syncthing (`http://localhost:8384`)
2. Verifica que la ruta de la carpeta compartida sea correcta en ambas maquinas
3. Revisa que `.stignore` no este excluyendo los archivos que esperas sincronizar
4. Reinicia Syncthing en ambas maquinas

```bash
# Restart on macOS
brew services restart syncthing

# Restart on Linux
systemctl restart syncthing@$USER
```

### Bridge Server Conexion Rechazada

**Sintoma:** `curl: (7) Failed to connect to 192.168.X.101 port 9876`

**Soluciones:**

1. Verifica que el bridge server este corriendo: `pm2 status`
2. Revisa el firewall en la maquina worker:

```bash
# Windows (PowerShell, run as admin)
New-NetFirewallRule -DisplayName "Bridge" -Direction Inbound -Port 9876 -Protocol TCP -Action Allow

# Linux
sudo ufw allow 9876/tcp
```

3. Verifica que la direccion IP no haya cambiado (DHCP puede reasignar IPs)

### Tarea Atorada en Active

**Sintoma:** Un archivo de tarea se queda en `tasks/active/` para siempre.

**Solucion:** El kernel crasheo mientras procesaba. Muevelo de vuelta al inbox:

```bash
mv ~/behique/ai_cluster/tasks/active/stuck-task.json \
   ~/behique/ai_cluster/tasks/inbox/stuck-task.json
```

Luego reinicia el kernel. Considera agregar un timeout al procesamiento de tareas de tu kernel.

### Ollama Lento en CPU

**Sintoma:** La inferencia toma 30+ segundos para prompts cortos.

**Soluciones:**

1. Usa un modelo mas pequeno: `qwen2.5:3b` en vez de `7b`
2. Reduce la longitud del prompt (menos contexto = mas rapido)
3. Pon un limite de tokens en tu llamada a Ollama:

```python
payload = {
    "model": "qwen2.5:7b",
    "prompt": prompt,
    "stream": False,
    "options": {
        "num_predict": 256  # Limit output tokens
    }
}
```

4. Considera conseguir un GPU. Incluso una GTX 1060 6GB usada en eBay por $100 hace una diferencia masiva.

### Memoria Baja en macOS

**Sintoma:** El sistema se pone lento, las apps empiezan a crashear.

**Soluciones:**

1. Revisa lo que Ollama esta usando: `ps aux | grep ollama`
2. Descarga el modelo cuando no lo estes usando:

```bash
# Ollama unloads models after 5 minutes of inactivity by default
# To force unload:
curl -X POST http://localhost:11434/api/generate \
  -d '{"model": "qwen2.5:7b", "keep_alive": 0}'
```

3. Cierra aplicaciones innecesarias
4. Pon `OLLAMA_MAX_LOADED_MODELS=1` para prevenir que multiples modelos se queden en memoria

### Fallos en Flujos de Trabajo de n8n

**Sintoma:** Los flujos dejan de ejecutarse o dan errores.

**Soluciones:**

1. Revisa los logs de n8n: `pm2 logs n8n`
2. Verifica que las URLs de webhook sean correctas y accesibles
3. Revisa que los servicios externos (APIs, bases de datos) sean alcanzables desde la maquina worker
4. Reinicia n8n: `pm2 restart n8n`

### Conflictos de Git por Syncthing

**Sintoma:** Syncthing crea archivos `.sync-conflict`.

Esto pasa cuando dos maquinas editan el mismo archivo al mismo tiempo. Syncthing no puede hacer merge, asi que mantiene ambas versiones.

**Solucion:**

```bash
# Find conflict files
find ~/behique -name "*.sync-conflict*"

# Manually resolve (keep the version you want)
# Then delete the conflict file
```

**Prevencion:** Designa una maquina como la "escritora" para cada archivo. Ceiba escribe `primer.md`. Cobo escribe sus propios logs. No escriben en los mismos archivos.

---

## 14. Que Sigue: Escalando Mas Alla de 3 Maquinas

La arquitectura que te he mostrado escala. Aqui es a donde va de aqui.

### Agregando Maquina 4, 5, 6...

Cada nueva maquina sigue el mismo patron:

1. Instalar Ollama
2. Instalar Syncthing, unirse al cluster
3. Opcionalmente instalar el bridge server
4. Actualizar el script de health check

Al kernel no le importa cuantas maquinas existan. Dirige a endpoints de Ollama. Agrega un nuevo endpoint, agrega una nueva maquina.

```python
# Multi-node Ollama routing
OLLAMA_NODES = [
    "http://192.168.X.100:11434",  # Ceiba
    "http://192.168.X.101:11434",  # Cobo
    "http://192.168.X.102:11434",  # Hutia
    "http://192.168.0.153:11434",  # Future node
]

def get_available_node():
    """Find the first responsive Ollama node."""
    for url in OLLAMA_NODES:
        try:
            r = requests.get(f"{url}/api/tags", timeout=2)
            if r.status_code == 200:
                return url
        except Exception:
            continue
    return None
```

### Nodos Especializados

Conforme agregues maquinas, especializalas:

- **Nodo de inferencia:** GPU potente, corre modelos grandes
- **Nodo de flujos de trabajo:** Corre n8n, maneja integraciones
- **Nodo de almacenamiento:** Disco duro grande, sirve archivos
- **Nodo siempre-on:** Bajo consumo, corre cron jobs y monitoreo

### Mejor Ruteo de Tareas

El ruteo actual basado en palabras clave es simple. El ruteo de siguiente nivel usa embeddings:

```python
# Future: Semantic task routing
# Embed the task objective, compare to skill embeddings,
# route to the best-matching skill automatically.
```

Esto esta en mi roadmap. El kernel ya tiene la infraestructura de busqueda de memoria. Agregar ruteo basado en embeddings es el siguiente paso natural.

### Interfaz Voice-First

Mi vision a largo plazo es completamente controlado por voz. Entrar al cuarto, decir "Behique, investiga productos en tendencia en la categoria de ropa vintage y genera cinco borradores de listings." El sistema captura la voz, la transcribe, la descompone en tareas, las dirige a traves de la flota y me envia los resultados en Telegram cuando estan listos.

BehiqueBot ya maneja mensajes de voz. La pieza que falta es la descomposicion automatica de tareas desde lenguaje natural. Ese es un problema resolvible con el prompt engineering correcto.

### Vendiendo el Sistema

Si construyes esto para ti mismo y funciona, puedes venderlo. No el codigo. La instalacion. Hay negocios que pagarian $2,000-5,000 por que alguien les configure un sistema de IA autonomo que corra en su hardware existente con cero costo mensual. Lo se porque estoy construyendo ese servicio ahora mismo.

La propuesta de valor es simple: "Tienes computadoras ociosas. Yo las voy a convertir en una fuerza de trabajo de IA que opera 24/7 por el costo de la electricidad."

### El Panorama Mas Grande

Lo que estamos construyendo no es solo un conjunto de scripts. Es una infraestructura personal de IA. El tipo de sistema que las grandes empresas de tecnologia tienen versiones internas, construido en hardware de consumidor por una sola persona.

Cada tarea que el sistema procesa hace la memoria mas inteligente. Cada automatizacion que construyes se acumula sobre las anteriores. Cada maquina que agregas multiplica tu capacidad.

La mayoria de las personas van a leer sobre agentes de IA y pensar "eso suena cool, tal vez algun dia." Tu ahora eres una de las personas que realmente puede construir uno. Las herramientas existen. El hardware es barato. La arquitectura esta probada.

La unica pregunta es: que le vas a poner a hacer primero a tu empleado de IA?

---

## Apendice A: Estructura Completa de Archivos

```
~/behique/
  ai_cluster/
    kernel/
      agent_kernel.py        # The orchestrator
    tasks/
      inbox/                 # New tasks
      active/                # Currently processing
      done/                  # Completed results
      archive/               # Old results
    memory/
      knowledge/             # Accumulated facts
      experiments/           # What worked/failed
      projects/              # Project context
      skills/                # Skill documentation
    skills/
      registry.json          # All registered skills
  bridge/
    dispatch.sh              # Quick task dispatch
    bridge-server.js         # HTTP command server
    wake.sh                  # Wake worker node
    sleep.sh                 # Sleep worker node
  tools/
    health_check.sh          # Fleet health monitoring
    content_pipeline.py      # Content generation
    reel-pipeline/
      make_reel.py           # Video production
      stories/               # Story JSON files
      output/                # Generated videos
    ebay-listing-assistant/
      core/
        pipeline.py          # Listing generation
  Ceiba/
    VAULT_INDEX.md           # Knowledge graph index
    projects/                # Project documentation
    faces/                   # Web dashboards
  primer.md                  # Live system state
  .stignore                  # Syncthing exclusions
```

## Apendice B: Tarjeta de Referencia Rapida

### Iniciar el Sistema

```bash
# Start Ollama (macOS - just open the app)
# Start Ollama (Linux)
ollama serve &

# Start the agent kernel
python3 ~/behique/ai_cluster/kernel/agent_kernel.py &

# Start the bridge server (on worker)
pm2 start bridge-server.js --name bridge

# Start n8n (on worker)
pm2 start n8n

# Start the dashboard
cd ~/behique/Ceiba/faces && python3 -m http.server 8091 --bind 0.0.0.0 &
```

### Enviar Tareas

```bash
# Quick dispatch
bash ~/behique/bridge/dispatch.sh fast "Your prompt here"

# Kernel task
cat > ~/behique/ai_cluster/tasks/inbox/task-$(date +%s).json << 'EOF'
{
  "objective": "Your task description",
  "model_preference": ["ollama"]
}
EOF
```

### Revisar Estado

```bash
# Fleet health
bash ~/behique/tools/health_check.sh

# Task queue
python3 ~/behique/ai_cluster/kernel/agent_kernel.py status

# Syncthing
open http://localhost:8384

# n8n
open http://192.168.X.101:5678
```

### Comandos Comunes de Ollama

```bash
ollama list                    # Show installed models
ollama pull qwen2.5:7b        # Download a model
ollama rm model-name           # Remove a model
ollama ps                      # Show running models
ollama show qwen2.5:7b        # Show model details
```

---

## Apendice C: Checklist de Seguridad

Antes de exponer cualquier cosa a internet, pasa por esta lista:

- [ ] El bridge server usa un bearer token fuerte y aleatorio (32+ caracteres)
- [ ] Syncthing esta configurado con autenticacion de dispositivos (no abierto a todos)
- [ ] El tunnel de Cloudflare es el unico punto de acceso externo (sin port forwarding)
- [ ] n8n tiene autenticacion habilitada (Settings > Security)
- [ ] Ningun API key o token esta hardcoded en scripts (usa variables de entorno)
- [ ] Las maquinas worker estan en una red local de confianza
- [ ] Las reglas de firewall solo abren los puertos necesarios (11434, 9876, 5678, 8384)
- [ ] Actualizaciones regulares del OS en todas las maquinas
- [ ] Autenticacion por SSH key en vez de contrasenas (si usas SSH)

---

## Palabras Finales

Escribi esta guia porque no la pude encontrar cuando la necesitaba. Todo lo que aprendi vino de unir documentacion de 15 herramientas diferentes, fallar, debuggear a las 2 AM y lentamente construir algo que funciona.

El sistema no es perfecto. El ruteo basado en palabras clave es primitivo. La busqueda de memoria es basica. El monitoreo es minimo. Pero funciona. Procesa tareas mientras duermo. Genera contenido mientras estoy en clase. No me cuesta nada correrlo.

No necesitas permiso de una empresa para construir infraestructura de IA. No necesitas un presupuesto de servidores. No necesitas un titulo en ciencias de la computacion (aunque estoy trabajando en uno). Necesitas una computadora, una conexion a internet y la disposicion de construir algo que no existe todavia.

Si construyes tu propia version de este sistema, me encantaria saber de ti. Escribeme en Telegram o Instagram. Muestrame lo que construiste. Dime que mejoraste. Todo el punto de poner esto en el mundo es que alguien lo lleve mas lejos de lo que yo lo hice.

Ahora ve a construir tu empleado de IA.

-- Behike
Puerto Rico, 2026
