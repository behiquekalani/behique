# Habitica Spanish Community. Infrastructure Plan
# Project: La Ceiba (working name)
# Owner: Kalani Andre Gomez Padin
# Created: 2026-03-19
# Status: PLANNING

---

## Vision

Build the best Spanish-speaking Habitica community. Not just another guild. A full ecosystem with automation, a Telegram hub, accountability systems, and content that feeds the Content Empire. Compete with and surpass "Habitica Ninja" by actually caring about the members and building real infrastructure.

Noble cause. Nonprofit angle. GF + friends as founding clan. Premium subscriptions for guild perks. Long-term funnel for other businesses.

---

## 1. Habitica API Reference (v3)

### Base URL & Authentication

```
Base URL: https://habitica.com/api/v3/
```

Every request needs these headers:

```
x-api-user: <User ID>
x-api-key: <API Token>
x-client: <UserID>-LaCeiba
Content-Type: application/json
```

Find your credentials at: Habitica > User Icon > Settings > API

### Rate Limits

- 30 points per minute
- Normal authenticated requests cost 1 point
- Registration/unauthenticated requests cost 5 points
- Response headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`
- Exceeding returns 429 with `Retry-After` header
- Automated background scripts: 30-second delay between calls (Habitica rule)

### Key Endpoints

#### User

| Method | Path | Description |
|--------|------|-------------|
| GET | `/user` | Get authenticated user profile |
| PUT | `/user` | Update user profile |
| POST | `/user/class/cast/:spellId` | Cast a skill |
| POST | `/user/purchase/:type/:key` | Purchase items |
| POST | `/user/buy-health-potion` | Buy health potion |
| POST | `/user/equip/:type/:key` | Equip/unequip item |
| POST | `/user/sleep` | Toggle rest in inn (pause damage) |
| POST | `/user/allocate` | Allocate stat point |
| POST | `/user/read-card/:cardType` | Read a card |
| DELETE | `/user/messages` | Delete private messages |
| POST | `/user/webhook` | Create a webhook |
| PUT | `/user/webhook/:id` | Edit a webhook |
| DELETE | `/user/webhook/:id` | Delete a webhook |

#### Tasks

| Method | Path | Description |
|--------|------|-------------|
| GET | `/tasks/user` | Get all user tasks |
| GET | `/tasks/user?type=habits` | Get habits only |
| GET | `/tasks/user?type=dailys` | Get dailies only |
| GET | `/tasks/user?type=todos` | Get todos only |
| GET | `/tasks/user?type=rewards` | Get rewards only |
| GET | `/tasks/user?type=completedTodos` | Get completed todos |
| GET | `/tasks/:taskId` | Get single task |
| POST | `/tasks/user` | Create new task |
| PUT | `/tasks/:taskId` | Update task |
| DELETE | `/tasks/:taskId` | Delete task |
| POST | `/tasks/:taskId/score/:direction` | Score task (up/down) |
| POST | `/tasks/:taskId/move/to/:position` | Reorder task |
| POST | `/tasks/:taskId/checklist` | Add checklist item |
| PUT | `/tasks/:taskId/checklist/:itemId` | Update checklist item |
| DELETE | `/tasks/:taskId/checklist/:itemId` | Delete checklist item |
| POST | `/tasks/:taskId/checklist/:itemId/score` | Score checklist item |

Task types: `habit`, `daily`, `todo`, `reward`

Difficulty multipliers: Trivial (0.1x), Easy (1x), Medium (1.5x), Hard (2x)

#### Groups (Party, Guilds)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/groups?type=party` | Get user's party |
| GET | `/groups?type=guilds` | Get user's guilds |
| GET | `/groups/:groupId` | Get specific group |
| POST | `/groups` | Create a group |
| PUT | `/groups/:groupId` | Update group |
| POST | `/groups/:groupId/join` | Join a group |
| POST | `/groups/:groupId/leave` | Leave a group |
| POST | `/groups/:groupId/remove/:memberId` | Remove member |
| GET | `/groups/:groupId/members` | Get group members |
| POST | `/groups/:groupId/invite` | Invite to group |

Use `party` as groupId shortcut for the user's current party.

#### Chat

| Method | Path | Description |
|--------|------|-------------|
| GET | `/groups/:groupId/chat` | Get chat messages |
| POST | `/groups/:groupId/chat` | Post message |
| DELETE | `/groups/:groupId/chat/:chatId` | Delete message |
| POST | `/groups/:groupId/chat/:chatId/like` | Like a message |
| POST | `/groups/:groupId/chat/seen` | Mark chat as read |
| POST | `/groups/:groupId/chat/:chatId/flag` | Report message |

#### Quests

| Method | Path | Description |
|--------|------|-------------|
| POST | `/groups/:groupId/quests/invite/:questKey` | Start/invite quest |
| POST | `/groups/:groupId/quests/accept` | Accept quest invite |
| POST | `/groups/:groupId/quests/reject` | Reject quest invite |
| POST | `/groups/:groupId/quests/force-start` | Force start quest |
| POST | `/groups/:groupId/quests/cancel` | Cancel quest |
| POST | `/groups/:groupId/quests/abort` | Abort active quest |
| POST | `/groups/:groupId/quests/leave` | Leave quest |

#### Challenges

| Method | Path | Description |
|--------|------|-------------|
| GET | `/challenges/user` | Get user's challenges |
| GET | `/challenges/groups/:groupId` | Get group challenges |
| GET | `/challenges/:challengeId` | Get specific challenge |
| POST | `/challenges` | Create challenge |
| PUT | `/challenges/:challengeId` | Update challenge |
| DELETE | `/challenges/:challengeId` | Delete challenge |
| POST | `/challenges/:challengeId/join` | Join challenge |
| POST | `/challenges/:challengeId/leave` | Leave challenge |

#### Skills (Casting)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/user/class/cast/:spellId` | Cast skill |

Healer: `heal` (Healing Light), `brightness` (Searing Brightness), `protectAura` (Protective Aura), `healAll` (Blessing)
Mage: `fireball` (Burst of Flames), `mpheal` (Ethereal Surge), `earth` (Earthquake), `frost` (Chilling Frost)
Rogue: `pickPocket` (Pickpocket), `backStab` (Backstab), `toolsOfTrade` (Tools of the Trade), `stealth` (Stealth)
Warrior: `smash` (Brutal Smash), `defensiveStance` (Defensive Stance), `valorousPresence` (Valorous Presence), `intimidate` (Intimidating Gaze)

### Webhooks

Webhooks are POST requests Habitica sends to your URL when events happen.

**Types:**

| Type | Fires When |
|------|-----------|
| `taskActivity` | Task created, updated, deleted, or scored |
| `groupChatReceived` | Message posted in a group you belong to |
| `userActivity` | User levels up or is invited to quest |
| `questActivity` | Quest started, finished, or invited |

**Create webhook via API:**

```json
POST /user/webhook
{
  "url": "https://your-server.com/webhook",
  "label": "LaCeiba Bot",
  "type": "taskActivity",
  "options": {
    "created": true,
    "updated": false,
    "deleted": false,
    "scored": true
  }
}
```

**Webhook payloads:**

taskActivity (scored):
```json
{
  "type": "scored",
  "direction": "up",
  "delta": 1.5,
  "task": { "_id": "...", "text": "...", "type": "daily", "value": 3.2 },
  "user": { "_id": "..." },
  "webhookType": "taskActivity"
}
```

questActivity (finished):
```json
{
  "type": "questFinished",
  "group": { "id": "...", "name": "La Ceiba" },
  "quest": { "key": "dilatory" },
  "user": { "_id": "..." },
  "webhookType": "questActivity"
}
```

groupChatReceived:
```json
{
  "chat": { "message": "...", "username": "..." },
  "group": { "id": "...", "name": "..." },
  "webhookType": "groupChatReceived"
}
```

---

## 2. Automation Scripts We Can Build

### Architecture Decision: Google Apps Script vs Python Server

**Google Apps Script (GAS)**
- Free, runs on Google servers
- Built-in time triggers (every 1, 5, 15, 60 min)
- Can receive webhooks as web app
- JavaScript-based
- Zero hosting cost
- Limitation: URL Fetch quotas, less control

**Python on Railway/Cobo (our approach)**
- Full control, integrates with BehiqueBot stack
- Can run on Railway alongside BehiqueBot
- Better error handling and logging
- Can bridge to Telegram directly
- Already have the infrastructure

**Decision:** Build core automation in Python. Use GAS only for member-facing scripts they set up themselves (like autoheal for their own accounts).

### Script 1: Auto-Accept Quest Invites

For party members who opt in. Runs as a webhook listener.

```python
import requests
import time

HABITICA_BASE = "https://habitica.com/api/v3"

def get_headers(user_id, api_token):
    return {
        "x-api-user": user_id,
        "x-api-key": api_token,
        "x-client": f"{user_id}-LaCeiba",
        "Content-Type": "application/json"
    }

def accept_quest(user_id, api_token):
    """Accept pending quest invitation for a user."""
    headers = get_headers(user_id, api_token)
    url = f"{HABITICA_BASE}/groups/party/quests/accept"
    resp = requests.post(url, headers=headers)
    time.sleep(30)  # respect rate limits
    return resp.json()

def check_pending_quest(user_id, api_token):
    """Check if user has a pending quest invite."""
    headers = get_headers(user_id, api_token)
    url = f"{HABITICA_BASE}/groups/party"
    resp = requests.get(url, headers=headers)
    data = resp.json()
    quest = data.get("data", {}).get("quest", {})
    if quest.get("key") and not quest.get("active"):
        # Quest is pending, check if user hasn't responded
        members = quest.get("members", {})
        if members.get(user_id) is None:
            return True
    return False
```

### Script 2: Auto-Heal Party

For the designated healer account. Checks party health every 15 minutes.

```python
def auto_heal_party(healer_id, healer_token):
    """Cast healing spells if party members need HP."""
    headers = get_headers(healer_id, healer_token)

    # Get healer stats
    user_resp = requests.get(f"{HABITICA_BASE}/user", headers=headers)
    user_data = user_resp.json()["data"]
    mana = user_data["stats"]["mp"]
    time.sleep(30)

    # Get party members
    members_resp = requests.get(
        f"{HABITICA_BASE}/groups/party/members",
        headers=headers
    )
    members = members_resp.json()["data"]
    time.sleep(30)

    # Check if anyone needs healing
    needs_healing = any(m["stats"]["hp"] < 40 for m in members)

    if needs_healing and mana >= 25:
        # Cast Blessing (healAll) - heals entire party
        cast_resp = requests.post(
            f"{HABITICA_BASE}/user/class/cast/healAll",
            headers=headers
        )
        time.sleep(30)
        return {"cast": "healAll", "result": cast_resp.json()}

    # Individual heal if only one person is low
    for member in members:
        if member["stats"]["hp"] < 30 and mana >= 15:
            cast_resp = requests.post(
                f"{HABITICA_BASE}/user/class/cast/heal",
                headers=headers,
                json={"targetId": member["_id"]}
            )
            mana -= 15
            time.sleep(30)

    return {"status": "healed"}
```

### Script 3: Auto Force-Start Quests

After X hours of waiting, force-start the quest so the party keeps moving.

```python
import datetime

QUEST_WAIT_HOURS = 4  # force start after 4 hours

def auto_force_start(leader_id, leader_token):
    """Force-start quest if it's been pending too long."""
    headers = get_headers(leader_id, leader_token)

    party_resp = requests.get(f"{HABITICA_BASE}/groups/party", headers=headers)
    party = party_resp.json()["data"]
    quest = party.get("quest", {})

    if quest.get("key") and not quest.get("active"):
        # Quest is pending. Check how long.
        # Note: Habitica doesn't expose quest invite timestamp directly.
        # We track this ourselves in our database.
        pending_since = get_quest_pending_time(party["_id"])  # our DB
        hours_waiting = (datetime.datetime.now() - pending_since).total_seconds() / 3600

        if hours_waiting >= QUEST_WAIT_HOURS:
            time.sleep(30)
            resp = requests.post(
                f"{HABITICA_BASE}/groups/party/quests/force-start",
                headers=headers
            )
            return {"forced": True, "result": resp.json()}

    return {"forced": False}
```

### Script 4: Quest Rotation (Auto-Invite Next Quest)

When a quest finishes, automatically invite the party to the next one from a rotation.

```python
QUEST_ROTATION = [
    "dilatory",        # Boss: The Dread Drag'on of Dilatory
    "stressbeast",     # Boss: The Stress Beast
    "burnout",         # Boss: Burnout
    "dysheartener",    # Boss: The Dysheartener
    "atom1",           # Collection quest
]

def auto_invite_next_quest(leader_id, leader_token, last_quest_key):
    """Invite party to next quest in rotation."""
    headers = get_headers(leader_id, leader_token)

    # Find next quest in rotation
    try:
        idx = QUEST_ROTATION.index(last_quest_key)
        next_quest = QUEST_ROTATION[(idx + 1) % len(QUEST_ROTATION)]
    except ValueError:
        next_quest = QUEST_ROTATION[0]

    # Check if we have the scroll
    user_resp = requests.get(f"{HABITICA_BASE}/user", headers=headers)
    items = user_resp.json()["data"]["items"]["quests"]
    time.sleep(30)

    if items.get(next_quest, 0) > 0:
        resp = requests.post(
            f"{HABITICA_BASE}/groups/party/quests/invite/{next_quest}",
            headers=headers
        )
        return {"invited": next_quest, "result": resp.json()}
    else:
        return {"error": f"No scroll for {next_quest}"}
```

### Script 5: Party Dashboard / Leaderboard Generator

```python
def get_party_leaderboard(user_id, api_token):
    """Generate party leaderboard data."""
    headers = get_headers(user_id, api_token)

    members_resp = requests.get(
        f"{HABITICA_BASE}/groups/party/members",
        headers=headers
    )
    members = members_resp.json()["data"]

    leaderboard = []
    for m in members:
        leaderboard.append({
            "name": m["profile"]["name"],
            "level": m["stats"]["lvl"],
            "class": m["stats"]["class"],
            "hp": round(m["stats"]["hp"], 1),
            "mp": round(m["stats"]["mp"], 1),
            "xp": m["stats"]["exp"],
        })

    # Sort by level descending
    leaderboard.sort(key=lambda x: x["level"], reverse=True)
    return leaderboard
```

### Script 6: Member GAS Templates (for members to self-install)

We provide Google Apps Script templates that members copy to their own Google account. Pre-configured for La Ceiba party.

**Auto-accept quest (GAS version for members):**
```javascript
// La Ceiba - Auto Accept Quest
// Paste your Habitica credentials below
const USER_ID = "PASTE_YOUR_USER_ID";
const API_TOKEN = "PASTE_YOUR_API_TOKEN";
const BASE_URL = "https://habitica.com/api/v3";

function acceptQuest() {
  var options = {
    method: "post",
    headers: {
      "x-api-user": USER_ID,
      "x-api-key": API_TOKEN,
      "x-client": USER_ID + "-LaCeiba",
      "Content-Type": "application/json"
    }
  };

  try {
    var response = UrlFetchApp.fetch(BASE_URL + "/groups/party/quests/accept", options);
    Logger.log("Quest accepted: " + response.getContentText());
  } catch (e) {
    Logger.log("No quest to accept or error: " + e.message);
  }
}

function install() {
  ScriptApp.newTrigger("acceptQuest")
    .timeBased()
    .everyMinutes(15)
    .create();
}

function uninstall() {
  var triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(function(trigger) {
    ScriptApp.deleteTrigger(trigger);
  });
}
```

---

## 3. Telegram Bot Architecture

### Bot Name: @LaCeibaBot (or @CeibaHabiticaBot)

### Stack

- Python (python-telegram-bot library, same as BehiqueBot)
- Railway hosting (same platform as BehiqueBot)
- SQLite or Notion for persistence
- Habitica API v3 for game data
- Webhooks from Habitica for real-time events

### Core Features

#### 3.1 Habitica-Telegram Bridge

Bridges party chat from Habitica to a Telegram group and vice versa.

```
Habitica Party Chat <--webhook--> Bot Server <--Telegram API--> Telegram Group
```

- Habitica `groupChatReceived` webhook fires when someone posts in party chat
- Bot forwards message to Telegram group with username attribution
- Telegram messages from group get posted back to Habitica party chat via API
- Two-way sync. Members can chat from either platform.

#### 3.2 Command List (all in Spanish)

**Informacion:**
- `/estado` - Ver estado de tu personaje (HP, MP, nivel, clase)
- `/equipo` - Ver estado de todos los miembros del party
- `/quest` - Ver progreso de la quest actual (boss HP, items collected)
- `/ranking` - Leaderboard del party por nivel
- `/estadisticas` - Stats semanales (tareas completadas, rachas, XP ganado)

**Acciones:**
- `/curar` - Pedir al healer que castee heal (notifica al healer)
- `/quest_siguiente` - Votar por la proxima quest
- `/motivar @usuario` - Enviar motivacion a un miembro
- `/reporte` - Reporte semanal del grupo

**Accountability:**
- `/meta <texto>` - Registrar meta del dia
- `/logro <texto>` - Registrar un logro
- `/racha` - Ver tu racha de dias activos
- `/checkin` - Check-in diario (el bot pregunta como vas)

**Admin:**
- `/vincular <habitica_user_id>` - Vincular cuenta Habitica con Telegram
- `/desvincular` - Desvincular cuenta
- `/config` - Configurar notificaciones
- `/admin_quest <quest_key>` - Forzar invitar quest (solo admins)

#### 3.3 Automated Messages

- **Morning message (8:00 AM AST):** "Buenos dias, guerreros. Recuerden marcar sus dailies. Quest actual: [boss name] - [HP restante]"
- **Quest completion:** "QUEST COMPLETADA. [quest name] derrotado. Recompensas: [loot]. Siguiente quest en 30 minutos."
- **Weekly recap (Sunday 8 PM):** Stats de la semana, MVP, rachas mas largas, XP total del grupo
- **Low HP alert:** "ALERTA. [username] esta en peligro. HP: [hp]/50. Healers, a curar."
- **Boss damage report:** After cron, report how much damage the party dealt and took

#### 3.4 Data Flow

```
Member links Telegram to Habitica
    |
    v
Bot stores mapping: telegram_id <-> habitica_user_id
    |
    v
Habitica webhooks fire -> Bot receives -> processes -> sends to Telegram
    |
    v
Telegram commands -> Bot processes -> calls Habitica API -> responds in Telegram
```

#### 3.5 Database Schema (SQLite)

```sql
CREATE TABLE members (
    id INTEGER PRIMARY KEY,
    telegram_id TEXT UNIQUE,
    telegram_username TEXT,
    habitica_user_id TEXT,
    habitica_api_token TEXT,  -- encrypted
    joined_at TIMESTAMP,
    role TEXT DEFAULT 'member',  -- member, admin, leader
    streak_days INTEGER DEFAULT 0,
    total_tasks_scored INTEGER DEFAULT 0
);

CREATE TABLE daily_checkins (
    id INTEGER PRIMARY KEY,
    member_id INTEGER,
    date TEXT,
    mood TEXT,
    goal TEXT,
    completed BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (member_id) REFERENCES members(id)
);

CREATE TABLE quest_history (
    id INTEGER PRIMARY KEY,
    quest_key TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    participants TEXT  -- JSON array of member IDs
);

CREATE TABLE weekly_stats (
    id INTEGER PRIMARY KEY,
    member_id INTEGER,
    week_start TEXT,
    tasks_scored INTEGER,
    xp_gained INTEGER,
    damage_dealt FLOAT,
    streak_maintained BOOLEAN,
    FOREIGN KEY (member_id) REFERENCES members(id)
);
```

---

## 4. Community Launch Plan

### Name Options (Taino-themed, Spanish)

- **La Ceiba** (the sacred tree, same as the AI. Full circle.)
- **Los Guerreros de Boriken** (Boriken = Taino name for Puerto Rico)
- **Tribu Taino** (Taino Tribe)
- **La Bohio** (Taino word for communal house)

### Phase 0: Foundation (Week 1)

- [ ] Create Habitica accounts for founding members (Kalani, GF, friends)
- [ ] Create the Party in Habitica (max 30 members)
- [ ] Create the Guild in Habitica (unlimited members, public-facing)
- [ ] Set up Telegram group and invite founding members
- [ ] Write guild description in Spanish (mission, rules, vibe)
- [ ] Kalani gets premium subscription (unlocks party quests)

### Phase 1: Inner Circle (Weeks 2-3)

- [ ] 5-10 founding members active
- [ ] Deploy basic Telegram bot with /estado, /equipo, /quest commands
- [ ] Set up auto-accept quest scripts (GAS templates for members)
- [ ] Run first quest together
- [ ] Establish daily check-in routine in Telegram
- [ ] Create community rules document in Spanish
- [ ] Set up challenge: "7 Dias de Habitos" (7 Day Habit Challenge)

### Phase 2: Automation Layer (Weeks 3-5)

- [ ] Deploy webhook server on Railway
- [ ] Enable Habitica-to-Telegram chat bridge
- [ ] Enable quest completion notifications
- [ ] Enable party damage alerts
- [ ] Auto force-start quests after 4 hours
- [ ] Auto quest rotation
- [ ] Deploy auto-heal for designated healer
- [ ] Weekly leaderboard generation

### Phase 3: Growth (Weeks 5-8)

- [ ] Open guild to public recruitment
- [ ] Post in Habitica Tavern (global chat) in Spanish
- [ ] Create recurring challenges with gem prizes
- [ ] Build onboarding flow: new member joins Telegram, bot walks them through setup
- [ ] Create "Guia del Guerrero" (Warrior's Guide). Habitica tutorial in Spanish
- [ ] Launch Instagram content about the community (ties to Content Empire)

### Phase 4: Scale (Month 2+)

- [ ] Multiple parties (overflow when first hits 30)
- [ ] Guild-level events and cross-party competitions
- [ ] Monthly MVP awards
- [ ] Partner with other Spanish guilds
- [ ] Premium tier: advanced automation, custom challenges
- [ ] n8n workflows for automated content from community stats

### Community Rules (Borrador / Draft)

1. Respeto siempre. Sin excepciones.
2. Activa tus dailies. Si no puedes, avisa al grupo o usa la posada.
3. Acepta las quests. No dejes al equipo esperando.
4. Habla en espanol. Ingles permitido pero el espanol es la base.
5. Cero toxicidad. Esto es para crecer juntos.
6. Reporta problemas a los admins, no al chat publico.
7. Diviertete. Esto es un juego. Si no te diviertes, algo esta mal.

### What Makes Us Better Than Habitica Ninja

1. **Real automation.** Not just a guild. Scripts, webhooks, a Telegram bot.
2. **Real leadership.** Kalani cares. This is passion, not clout.
3. **Accountability system.** Daily check-ins, weekly recaps, streak tracking.
4. **Bilingual resources.** Everything in Spanish first, but technical docs in both.
5. **Content creation.** The community itself becomes content for the brand.
6. **No ego.** Nonprofit vibe. Community over individual.

---

## 5. Content Empire Connection

### How the Community Feeds Content

1. **Reels / TikToks about Habitica in Spanish**
   - "Como uso un RPG para dejar de procrastinar"
   - "Mis habitos me dan XP. Asi funciona Habitica"
   - Tutorial series: Habitica para principiantes (en espanol)
   - Boss fight reactions / quest completion celebrations
   - Before/after: "30 dias en Habitica cambiaron mi vida"

2. **Community highlights**
   - Weekly MVP spotlight
   - Quest completion montages
   - Member testimonials (real stories, real habit changes)
   - "Dia en la vida de un guerrero de Habitica"

3. **Automation/tech content**
   - "Automatice mi vida con Habitica + Telegram"
   - Tutorial: como configurar los scripts
   - Behind the scenes: building the bot
   - This positions Kalani as a tech builder, not just a gamer

4. **Funnel flow**
   ```
   Viewer sees Habitica reel
       -> Joins Telegram community
       -> Gets value from automation + accountability
       -> Sees Kalani's other content (AI, business, tech)
       -> Follows personal brand
       -> Eventually discovers courses/services/products
   ```

5. **Data for content**
   - Community stats become infographics
   - Quest data becomes storytelling
   - Member growth becomes social proof
   - Everything is content if you track it

---

## 6. Implementation Phases (Technical)

### Phase 1: Skeleton Bot (3-4 hours)

Build the minimal Telegram bot that can:

1. Link Habitica accounts (/vincular)
2. Fetch and display user stats (/estado)
3. Show party info (/equipo)
4. Show quest progress (/quest)

**Files:**
```
habitica-bot/
  main.py              # Telegram bot entry point
  habitica_api.py      # Habitica API wrapper
  database.py          # SQLite operations
  handlers/
    info.py            # /estado, /equipo, /quest, /ranking
    account.py         # /vincular, /desvincular
    admin.py           # admin commands
  config.py            # env vars, constants
  Procfile             # Railway deployment
  requirements.txt
```

**Requirements:**
```
python-telegram-bot>=20.0
requests
cryptography  # for encrypting API tokens
aiosqlite     # async SQLite
```

### Phase 2: Webhook Receiver (2-3 hours)

Add Flask/FastAPI endpoint to receive Habitica webhooks:

```python
from fastapi import FastAPI, Request
from telegram import Bot

app = FastAPI()
bot = Bot(token=TELEGRAM_TOKEN)

@app.post("/webhook/habitica")
async def habitica_webhook(request: Request):
    data = await request.json()
    webhook_type = data.get("webhookType")

    if webhook_type == "questActivity":
        if data["type"] == "questFinished":
            await bot.send_message(
                chat_id=GROUP_CHAT_ID,
                text=f"QUEST COMPLETADA. {data['quest']['key']} terminada."
            )

    elif webhook_type == "groupChatReceived":
        msg = data["chat"]["message"]
        user = data["chat"]["username"]
        await bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=f"[Habitica] {user}: {msg}"
        )

    elif webhook_type == "taskActivity":
        if data["type"] == "scored":
            # Track for leaderboard
            await update_member_stats(data["user"]["_id"], data["delta"])

    return {"ok": True}
```

### Phase 3: Automation Engine (3-4 hours)

Add scheduled jobs:

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

# Morning message at 8 AM AST
scheduler.add_job(send_morning_message, "cron", hour=8, minute=0)

# Check party health every 15 min
scheduler.add_job(auto_heal_check, "interval", minutes=15)

# Force-start stale quests every hour
scheduler.add_job(auto_force_start_check, "interval", hours=1)

# Weekly recap Sunday 8 PM
scheduler.add_job(send_weekly_recap, "cron", day_of_week="sun", hour=20)

scheduler.start()
```

### Phase 4: Polish + Content Integration (ongoing)

- Leaderboard graphics (auto-generated images)
- Integration with n8n for content pipeline triggers
- BehiqueBot cross-posting (Kalani's personal tasks feed community stats)
- Dashboard HTML page in Ceiba/faces/ for visual tracking

---

## 7. Existing n8n Habitica Node

There is an n8n community node for Habitica: `n8n-nodes-habitica`
GitHub: https://github.com/umanamente/n8n-nodes-habitica

It supports: tasks, user, chat, inbox, quests, groups, skills, content, cron.

Since Kalani already has n8n running on Cobo, this could handle some automation without custom code:
- Scheduled quest management workflows
- Content generation triggers (quest completed -> generate social post)
- Member stat collection for dashboards

Install on Cobo's n8n instance: `npm install n8n-nodes-habitica`

---

## 8. Competitive Landscape (Spanish Habitica)

Existing Spanish guilds found:
- Various small guilds with low activity
- "Habitica Ninja" (the main competitor, bad leadership per Kalani)
- No guild currently offers Telegram integration or automation scripts
- No guild has a content presence on Instagram/TikTok

This is a wide-open opportunity. The Spanish Habitica community is underserved.

---

## 9. Cost Estimate

| Item | Cost | Notes |
|------|------|-------|
| Habitica Premium (Kalani) | $5/mo or $48/yr | Unlocks party quests, gems |
| Railway hosting (bot) | $0-5/mo | Could share with BehiqueBot dyno |
| Telegram Bot API | Free | |
| Google Apps Script | Free | For member-facing scripts |
| Domain (optional) | $12/yr | laceiba.community or similar |
| Gem prizes for challenges | Variable | Can earn gems in-game too |
| **Total minimum** | **$5/mo** | Just the premium subscription |

---

## 10. Risk Factors

1. **API rate limits.** 30 req/min is tight with many members. Batch and cache.
2. **Member API tokens.** Storing Habitica tokens requires encryption. Never expose.
3. **Habitica TOS.** Automation is allowed but scripts causing issues get blocked. Follow API guidelines.
4. **Community management.** Kalani needs at least 1-2 trusted admins (GF is one).
5. **Sustainability.** Start small. Don't over-engineer before there are 10 active members.

---

## Next Steps (Immediate)

1. [ ] Create Habitica party with GF and friends
2. [ ] Write guild description in Spanish
3. [ ] Scaffold the Telegram bot (reuse BehiqueBot patterns)
4. [ ] Build `habitica_api.py` wrapper with the endpoints above
5. [ ] Deploy basic /estado and /equipo commands
6. [ ] First quest as a group
7. [ ] First reel about the community (Content Empire feed)

---

*This plan connects to: Content Empire (content from community), BehiqueBot (shared accountability framework), n8n workflows (automation), personal brand (Kalani as builder/leader).*
