# Habitica API v3 Wrapper
# Core API client for La Ceiba community automation
# Copyright 2026 Behike. All rights reserved.

import os
import time
import logging
from functools import wraps

import requests

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

HABITICA_BASE_URL = "https://habitica.com/api/v3"
RATE_LIMIT_MAX = 30          # 30 requests per minute
RATE_LIMIT_WINDOW = 60       # seconds
BACKGROUND_DELAY = 30        # seconds between automated background calls


class RateLimiter:
    """Token-bucket rate limiter for Habitica API (30 req/min)."""

    def __init__(self, max_calls: int = RATE_LIMIT_MAX, window: int = RATE_LIMIT_WINDOW):
        self.max_calls = max_calls
        self.window = window
        self.calls: list[float] = []

    def wait_if_needed(self):
        """Block until a request slot is available."""
        now = time.time()
        # Purge timestamps older than the window
        self.calls = [t for t in self.calls if now - t < self.window]

        if len(self.calls) >= self.max_calls:
            sleep_for = self.window - (now - self.calls[0]) + 0.1
            logger.info("Rate limit reached, sleeping %.1fs", sleep_for)
            time.sleep(sleep_for)

        self.calls.append(time.time())


class HabiticaAPIError(Exception):
    """Raised when the Habitica API returns an error."""

    def __init__(self, status_code: int, message: str, response: dict | None = None):
        self.status_code = status_code
        self.message = message
        self.response = response or {}
        super().__init__(f"[{status_code}] {message}")


def _retry(max_retries: int = 3, backoff: float = 2.0):
    """Decorator: retry on transient HTTP errors (429, 5xx)."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except HabiticaAPIError as exc:
                    last_exc = exc
                    if exc.status_code == 429:
                        # Respect Retry-After header if available
                        retry_after = exc.response.get("retry_after", backoff * (attempt + 1))
                        logger.warning("429 rate limited. Retrying in %ss (attempt %d/%d)",
                                       retry_after, attempt + 1, max_retries)
                        time.sleep(float(retry_after))
                    elif exc.status_code >= 500:
                        wait = backoff * (attempt + 1)
                        logger.warning("Server error %d. Retrying in %ss (attempt %d/%d)",
                                       exc.status_code, wait, attempt + 1, max_retries)
                        time.sleep(wait)
                    else:
                        raise
                except requests.RequestException as exc:
                    last_exc = exc
                    wait = backoff * (attempt + 1)
                    logger.warning("Network error: %s. Retrying in %ss (attempt %d/%d)",
                                   exc, wait, attempt + 1, max_retries)
                    time.sleep(wait)
            raise last_exc  # type: ignore[misc]
        return wrapper
    return decorator


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------

class HabiticaClient:
    """Synchronous client for the Habitica v3 API.

    Auth is pulled from env vars by default:
        HABITICA_USER_ID
        HABITICA_API_TOKEN

    You can also pass them explicitly.
    """

    def __init__(
        self,
        user_id: str | None = None,
        api_token: str | None = None,
        base_url: str = HABITICA_BASE_URL,
    ):
        self.user_id = user_id or os.environ["HABITICA_USER_ID"]
        self.api_token = api_token or os.environ["HABITICA_API_TOKEN"]
        self.base_url = base_url.rstrip("/")
        self._limiter = RateLimiter()
        self._session = requests.Session()
        self._session.headers.update(self._headers())

    def _headers(self) -> dict:
        return {
            "x-api-user": self.user_id,
            "x-api-key": self.api_token,
            "x-client": f"{self.user_id}-LaCeiba",
            "Content-Type": "application/json",
        }

    # -- low-level request --------------------------------------------------

    @_retry(max_retries=3)
    def _request(self, method: str, path: str, **kwargs) -> dict:
        """Make a rate-limited, retried request and return the JSON body."""
        self._limiter.wait_if_needed()
        url = f"{self.base_url}/{path.lstrip('/')}"
        resp = self._session.request(method, url, **kwargs)

        if resp.status_code == 429:
            raise HabiticaAPIError(
                429,
                "Rate limited",
                {"retry_after": resp.headers.get("Retry-After", "5")},
            )

        try:
            data = resp.json()
        except ValueError:
            data = {}

        if not resp.ok:
            msg = data.get("message", resp.reason or "Unknown error")
            raise HabiticaAPIError(resp.status_code, msg, data)

        return data

    def _get(self, path: str, **kwargs) -> dict:
        return self._request("GET", path, **kwargs)

    def _post(self, path: str, **kwargs) -> dict:
        return self._request("POST", path, **kwargs)

    def _put(self, path: str, **kwargs) -> dict:
        return self._request("PUT", path, **kwargs)

    def _delete(self, path: str, **kwargs) -> dict:
        return self._request("DELETE", path, **kwargs)

    # -- User ---------------------------------------------------------------

    def get_user(self) -> dict:
        """Get the authenticated user's full profile."""
        return self._get("/user")

    def get_user_stats(self) -> dict:
        """Get just the stats block (hp, mp, xp, lvl, class, gp)."""
        data = self.get_user()
        stats = data["data"]["stats"]
        profile = data["data"]["profile"]
        return {
            "name": profile.get("name", "Unknown"),
            "hp": round(stats["hp"], 1),
            "maxHealth": stats["maxHealth"],
            "mp": round(stats["mp"], 1),
            "maxMP": stats["maxMP"],
            "exp": stats["exp"],
            "toNextLevel": stats["toNextLevel"],
            "lvl": stats["lvl"],
            "gp": round(stats["gp"], 1),
            "class": stats.get("class", "warrior"),
        }

    # -- Tasks --------------------------------------------------------------

    def get_tasks(self, task_type: str | None = None) -> list[dict]:
        """Get user tasks. Optional filter: habits, dailys, todos, rewards."""
        params = {}
        if task_type:
            params["type"] = task_type
        data = self._get("/tasks/user", params=params)
        return data["data"]

    def get_habits(self) -> list[dict]:
        return self.get_tasks("habits")

    def get_dailies(self) -> list[dict]:
        return self.get_tasks("dailys")

    def get_todos(self) -> list[dict]:
        return self.get_tasks("todos")

    def score_task(self, task_id: str, direction: str = "up") -> dict:
        """Score a task up or down. Returns updated user stats delta."""
        if direction not in ("up", "down"):
            raise ValueError("direction must be 'up' or 'down'")
        return self._post(f"/tasks/{task_id}/score/{direction}")

    def create_task(self, task_data: dict) -> dict:
        """Create a new task.

        task_data must include at minimum:
            text (str), type (habit|daily|todo|reward)
        Optional: priority (0.1, 1, 1.5, 2), notes, tags, etc.
        """
        required = {"text", "type"}
        if not required.issubset(task_data.keys()):
            raise ValueError(f"task_data must include: {required}")
        return self._post("/tasks/user", json=task_data)

    def get_task(self, task_id: str) -> dict:
        """Get a single task by ID."""
        return self._get(f"/tasks/{task_id}")

    def update_task(self, task_id: str, updates: dict) -> dict:
        """Update fields on an existing task."""
        return self._put(f"/tasks/{task_id}", json=updates)

    def delete_task(self, task_id: str) -> dict:
        """Delete a task."""
        return self._delete(f"/tasks/{task_id}")

    # -- Groups / Party -----------------------------------------------------

    def get_party(self) -> dict:
        """Get the user's current party."""
        return self._get("/groups/party")

    def get_party_members(self) -> list[dict]:
        """Get all members of the user's party."""
        data = self._get("/groups/party/members")
        return data["data"]

    def get_group(self, group_id: str) -> dict:
        """Get a specific group by ID."""
        return self._get(f"/groups/{group_id}")

    def get_group_chat(self, group_id: str = "party") -> list[dict]:
        """Get chat messages for a group. Defaults to party."""
        data = self._get(f"/groups/{group_id}/chat")
        return data["data"]

    def post_chat(self, message: str, group_id: str = "party") -> dict:
        """Post a message to group chat."""
        return self._post(f"/groups/{group_id}/chat", json={"message": message})

    # -- Quests -------------------------------------------------------------

    def get_quest_progress(self) -> dict | None:
        """Get current quest progress from party data."""
        party = self.get_party()
        quest = party["data"].get("quest", {})
        if not quest.get("key"):
            return None
        return quest

    def accept_quest(self, group_id: str = "party") -> dict:
        return self._post(f"/groups/{group_id}/quests/accept")

    def force_start_quest(self, group_id: str = "party") -> dict:
        return self._post(f"/groups/{group_id}/quests/force-start")

    def invite_quest(self, quest_key: str, group_id: str = "party") -> dict:
        return self._post(f"/groups/{group_id}/quests/invite/{quest_key}")

    # -- Skills -------------------------------------------------------------

    def cast_skill(self, spell_id: str, target_id: str | None = None) -> dict:
        """Cast a class skill. target_id needed for single-target spells."""
        kwargs: dict = {}
        if target_id:
            kwargs["json"] = {"targetId": target_id}
        return self._post(f"/user/class/cast/{spell_id}", **kwargs)


# ---------------------------------------------------------------------------
# Convenience: module-level singleton
# ---------------------------------------------------------------------------

_default_client: HabiticaClient | None = None


def get_client(**kwargs) -> HabiticaClient:
    """Get or create a module-level default client."""
    global _default_client
    if _default_client is None:
        _default_client = HabiticaClient(**kwargs)
    return _default_client
