# Habitica Tools - La Ceiba Community

Herramientas de automatizacion para la comunidad hispanohablante de Habitica.

Copyright 2026 Behike. All rights reserved.

## Archivos

| Archivo | Descripcion |
|---------|-------------|
| `habitica_api.py` | Wrapper del API de Habitica v3. Rate limiting, retries, auth. |
| `habitica_bot.py` | Bot de Telegram con comandos en espanol para el party. |
| `habitica_automations.py` | Automatizaciones programadas: recordatorios, rachas, reportes. |

## Requisitos

```
pip install python-telegram-bot requests apscheduler
```

Python 3.10+

## Variables de entorno

```bash
# Habitica (Settings > API en habitica.com)
export HABITICA_USER_ID="tu-user-id"
export HABITICA_API_TOKEN="tu-api-token"

# Telegram
export TELEGRAM_BOT_TOKEN="token-de-BotFather"
export TELEGRAM_CHAT_ID="id-del-grupo-de-telegram"
```

## Uso rapido

### Solo el API wrapper

```python
from habitica_api import HabiticaClient

client = HabiticaClient()
stats = client.get_user_stats()
print(f"Nivel {stats['lvl']}, HP: {stats['hp']}")

dailies = client.get_dailies()
for d in dailies:
    if not d["completed"]:
        print(f"Pendiente: {d['text']}")
```

### Bot de Telegram

```bash
python habitica_bot.py
```

Comandos disponibles:
- `/stats` - Ver tus stats (HP, XP, Oro, Nivel, Clase)
- `/habits` - Listar habitos con botones + y -
- `/dailies` - Dailies de hoy con estado de completado
- `/todos` - Todos ordenados por prioridad
- `/complete [tarea]` - Completar tarea por nombre (busqueda aproximada)
- `/party` - Info del party y progreso de quest
- `/motivacion` - Frase motivacional random
- `/reto` - Sugerencia de reto diario

### Automatizaciones

```python
import asyncio
from habitica_automations import setup_scheduler

# Con scheduler (se ejecuta en background)
scheduler = setup_scheduler()
scheduler.start()

# O manual
from habitica_automations import daily_reminder
asyncio.run(daily_reminder())
```

Tareas programadas:
- 7:00 AM AST - Recordatorio de dailies pendientes
- 8:00 AM AST - Celebracion de rachas (3, 7, 14, 30 dias)
- Domingo 8:00 PM AST - Reporte semanal
- Cada 3 horas - Alerta de dano de boss (HP bajo)

## Rate Limits

El API de Habitica permite 30 requests por minuto. El wrapper maneja esto automaticamente con un rate limiter interno. Para scripts de background, Habitica recomienda 30 segundos entre llamadas.

## Estructura del proyecto

```
tools/habitica/
  habitica_api.py           # Core API wrapper
  habitica_bot.py           # Telegram bot
  habitica_automations.py   # Scheduled automations
  README.md                 # Este archivo
```

## Deploy

El bot esta disenado para correr en Railway junto con BehiqueBot. Usa el mismo stack: Python + python-telegram-bot.

```
# Procfile
web: python habitica_bot.py
```
