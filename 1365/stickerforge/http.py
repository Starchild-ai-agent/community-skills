"""HTTP helper — works inside the platform (SC-Proxy) and standalone."""

import os
import requests

# Try to use the platform's proxied HTTP client (SC-Proxy injects credentials).
# When running standalone (outside the server process), fall back to plain
# requests with OPENROUTER_API_KEY from the environment.

try:
    from core.http_client import proxied_post as _platform_post, is_proxy_enabled
    _HAS_PROXY = is_proxy_enabled()
except ImportError:
    _HAS_PROXY = False
    _platform_post = None


def post(url: str, headers: dict = None, json: dict = None, timeout: int = 30) -> requests.Response:
    """POST request that routes through SC-Proxy when available."""
    if _HAS_PROXY:
        return _platform_post(url, headers=headers, json=json, timeout=timeout)

    # Standalone fallback — inject OPENROUTER_API_KEY ourselves
    headers = dict(headers or {})
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    return requests.post(url, headers=headers, json=json, timeout=timeout)
