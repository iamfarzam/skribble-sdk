from __future__ import annotations

import json
import time
from threading import Lock
from typing import Any, Optional, Protocol, runtime_checkable

import requests
from skribble.config import SkribbleConfig
from skribble.exceptions import SkribbleAuthError
from skribble.exceptions import SkribbleHTTPError


@runtime_checkable
class TokenCache(Protocol):
    """Minimal cache interface used for storing access tokens."""

    def get(self, key: str) -> Optional[bytes]:
        ...

    def setex(self, key: str, ttl_seconds: int, value: Any) -> None:
        ...


class _InMemoryTokenCache:
    """
    Lightweight in-memory cache to avoid a hard Redis dependency.

    Stores values with an expiry timestamp and mirrors the Redis API surface
    used by TokenManager (get/setex).
    """

    def __init__(self) -> None:
        self._data: dict[str, tuple[float, bytes]] = {}
        self._lock = Lock()

    def get(self, key: str) -> Optional[bytes]:
        with self._lock:
            entry = self._data.get(key)
            if not entry:
                return None
            expires_at, value = entry
            if expires_at < time.time():
                self._data.pop(key, None)
                return None
            return value

    def setex(self, key: str, ttl_seconds: int, value: Any) -> None:
        # Redis stores bytes; mirror that to keep TokenManager logic consistent.
        payload = value if isinstance(value, (bytes, bytearray)) else str(value).encode("utf-8")
        with self._lock:
            self._data[key] = (time.time() + ttl_seconds, payload)


class TokenManager:
    """
    Handles obtaining and caching Skribble access tokens (JWTs) in a cache backend.

    - Logs in via POST /access/login with username + api-key
    - Caches access token with TTL from config (default 20 minutes)
    - Uses Redis if provided, otherwise falls back to an in-memory cache
    """

    def __init__(
            self,
            *,
            username: str,
            api_key: str,
            http_session: requests.Session,
            config: SkribbleConfig,
            redis_client: Optional[TokenCache] = None,
            token_cache: Optional[TokenCache] = None,
            tenant_id: Optional[str] = None,
    ) -> None:
        self._username = username
        self._api_key = api_key
        self._session = http_session
        self._cfg = config
        self._cache: TokenCache = token_cache or redis_client or _InMemoryTokenCache()
        self._tenant_id = tenant_id

    @property
    def _cache_key(self) -> str:
        base = f"{self._cfg.cache_key_prefix}:token:{self._username}"
        if self._tenant_id:
            return f"{base}:{self._tenant_id}"
        return base

    def get_access_token(self, *, force_refresh: bool = False) -> str:
        """
        Returns a valid access token, refreshing it via /access/login if needed.
        """
        if not force_refresh:
            cached = self._cache.get(self._cache_key)
            if cached:
                return cached.decode("utf-8")

        token = self._login()
        # Store token with configured TTL (docs: ~20 minutes)
        self._cache.setex(self._cache_key, self._cfg.access_token_ttl_seconds, token)
        return token

    def _login(self) -> str:
        """
        Performs POST /access/login and returns the JWT access token.
        """
        url = f"{self._cfg.api_base_url}/access/login"
        payload = {
            "username": self._username,
            "api-key": self._api_key,
        }

        try:
            resp = self._session.post(
                url,
                json=payload,
                timeout=self._cfg.timeout,
                verify=self._cfg.verify_ssl,
            )
        except requests.RequestException as exc:
            raise SkribbleAuthError(f"Failed to call Skribble login endpoint: {exc}") from exc

        if resp.status_code != 200:
            text = resp.text
            try:
                data = resp.json()
                msg = data.get("message") or data.get("error") or text
            except json.JSONDecodeError:
                data = None
                msg = text
            raise SkribbleHTTPError(
                resp.status_code,
                f"Login failed: {msg}",
                response_json=data,
                response_text=text,
            )

        # The Postman collection stores the JWT in AUTH_ACCESS_TOKEN environment var.
        # Here, we assume the API returns the JWT directly as a string or in a JSON field.
        content_type = resp.headers.get("Content-Type", "")
        if "application/json" in content_type:
            data = resp.json()
            # Common patterns: {"token": "..."} or {"access_token": "..."} or string
            token = (
                    data.get("access_token")
                    or data.get("token")
                    or data.get("jwt")
                    or data.get("AUTH_ACCESS_TOKEN")
            )
            if not token:
                # Try plain JSON string
                if isinstance(data, str):
                    token = data
            if not token:
                raise SkribbleAuthError("Login succeeded but no access token found in response JSON.")
        else:
            # Some implementations may return raw token text
            token = resp.text.strip()

        if not token:
            raise SkribbleAuthError("Login succeeded but access token is empty.")

        return token
