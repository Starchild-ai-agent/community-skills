"""Shared HTTP client for Meta DEX Aggregator.

Single session with connection pooling, retry/backoff, and consistent timeouts.
All modules should use `get(url, ...)` and `post(url, ...)` instead of raw requests.
"""

import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

_session = None

DEFAULT_TIMEOUT = (2.0, 10.0)  # (connect, read)

def _get_session():
    global _session
    if _session is None:
        _session = requests.Session()
        retry = Retry(
            total=2,
            connect=1,
            read=1,
            backoff_factor=0.3,
            status_forcelist=(429, 502, 503, 504),
            allowed_methods=("GET", "POST"),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry, pool_connections=20, pool_maxsize=40)
        _session.mount("https://", adapter)
        _session.mount("http://", adapter)
        _session.headers.update({"User-Agent": "meta-dex-aggregator/4.1"})
    return _session


def get(url, timeout=DEFAULT_TIMEOUT, **kwargs):
    """Session-pooled GET. Returns requests.Response."""
    return _get_session().get(url, timeout=timeout, **kwargs)


def post(url, timeout=DEFAULT_TIMEOUT, **kwargs):
    """Session-pooled POST. Returns requests.Response."""
    return _get_session().post(url, timeout=timeout, **kwargs)
