"""
OpenSea API client for Starchild skill scripts.

- Uses sc-proxy via core.http_client (proxied_get/proxied_post)
- Supports optional OPENSEA_API_KEY in env
- Requires SC-CALLER-ID for usage tracking
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional

from core.http_client import proxied_get, proxied_post

BASE_URL = "https://api.opensea.io"
DEFAULT_CALLER_ID = "chat:opensea-skill"


class OpenSeaClient:
    def __init__(self, caller_id: str = DEFAULT_CALLER_ID):
        self.base_url = BASE_URL
        self.api_key = os.environ.get("OPENSEA_API_KEY", "").strip()
        self.caller_id = caller_id or DEFAULT_CALLER_ID

    def _headers(self) -> Dict[str, str]:
        headers = {"SC-CALLER-ID": self.caller_id}
        if self.api_key:
            headers["X-API-KEY"] = self.api_key
        return headers

    def _url(self, path: str) -> str:
        if path.startswith("http://") or path.startswith("https://"):
            return path
        return f"{self.base_url}{path}"

    def get(self, path: str, params: Optional[Dict[str, Any]] = None, timeout: int = 20) -> Dict[str, Any]:
        response = proxied_get(
            self._url(path),
            headers=self._headers(),
            params=params or {},
            timeout=timeout,
        )
        if response.status_code >= 400:
            raise RuntimeError(f"OpenSea GET {path} failed: {response.status_code} {response.text}")
        try:
            return response.json()
        except Exception:
            return {"raw": response.text}

    def post(
        self,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        timeout: int = 25,
    ) -> Dict[str, Any]:
        response = proxied_post(
            self._url(path),
            headers=self._headers(),
            json=data or {},
            timeout=timeout,
        )
        if response.status_code >= 400:
            raise RuntimeError(f"OpenSea POST {path} failed: {response.status_code} {response.text}")
        try:
            return response.json()
        except Exception:
            return {"raw": response.text}
