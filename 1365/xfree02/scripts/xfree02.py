#!/usr/bin/env python3
"""xfree02 CLI — query sponsored Nansen on-chain intelligence endpoints.

The sponsor pays; the user needs no wallet and signs nothing.  Daily quotas
apply per caller (XFREE02_API_KEY) and globally across all callers.

Environment:
    XFREE02_BASE_URL   Base URL of the xfree02 gateway.
                       Default: https://1365-xfree02-gateway.community.iamstarchild.com
    XFREE02_API_KEY    OPTIONAL. When set to a recognised key, spend is
                       billed to that key's own daily quota bucket instead of
                       the anonymous per-IP bucket. The gateway is open: calls
                       succeed with no key at all.

Subcommands:
    catalog [--sponsored-only] [--max-price N]
    show <path>
    call <path> [--body '<json>' | --body-file <file>]
    health
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_BASE_URL = "https://1365-xfree02-gateway.community.iamstarchild.com"
SCRIPT_DIR = Path(__file__).resolve().parent
CATALOG_PATH = SCRIPT_DIR.parent / "references" / "catalog.json"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_catalog() -> dict:
    with open(CATALOG_PATH) as f:
        return json.load(f)


def _find_endpoint(catalog: dict, path: str) -> dict | None:
    """Match with or without leading slash."""
    for ep in catalog["endpoints"]:
        if ep["path"] == path or ep["path"] == "/" + path.lstrip("/"):
            return ep
    return None


def _warn_base_default() -> None:
    """No-op: DEFAULT_BASE_URL is the live public gateway, not a placeholder."""
    return


# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------

def cmd_catalog(args: argparse.Namespace) -> None:
    catalog = _load_catalog()
    rows = []
    for ep in catalog["endpoints"]:
        price = float(ep["price_usd"])
        if args.sponsored_only and price > 0.01:
            continue
        if args.max_price is not None and price > float(args.max_price):
            continue
        rows.append((ep["path"], ep["price_usd"], ep["label"]))

    if not rows:
        print("No endpoints match the given filters.")
        return

    col_w = [
        max(len(r[0]) for r in rows),
        max(len(str(r[1])) for r in rows),
        max(len(r[2]) for r in rows),
    ]
    fmt = "  ".join(f"{{:<{w}}}" for w in col_w)
    print(fmt.format("PATH", "PRICE_USD", "LABEL"))
    print(fmt.format("-" * col_w[0], "-" * col_w[1], "-" * col_w[2]))
    for path, price, label in rows:
        print(fmt.format(path, str(price), label))


def cmd_show(args: argparse.Namespace) -> None:
    catalog = _load_catalog()
    ep = _find_endpoint(catalog, args.path)
    if ep is None:
        sys.exit(f"ERROR: endpoint not found: {args.path}")
    print(f"Path:           {ep['path']}")
    print(f"Price (USD):    {ep['price_usd']}")
    print(f"Label:          {ep['label']}")
    print(f"Sponsored:      {ep['price_usd'] <= 0.01}")
    print(f"Required fields: {ep['required_fields']}")
    print(f"Fields:")
    for fld in ep.get("fields") or []:
        req = "required" if fld.get("required") else "optional"
        print(f"  - {fld['name']} ({fld.get('type', '?')}, {req}): {fld.get('description', '')}")
    print(f"Example body:   {json.dumps(ep.get('example_body') or {})}")


def cmd_call(args: argparse.Namespace) -> None:
    # Open gateway: a key is optional. With one, spend is billed to that key's
    # bucket; without one, to an anonymous per-IP bucket.
    api_key = os.environ.get("XFREE02_API_KEY")

    base_url = os.environ.get("XFREE02_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    if base_url == DEFAULT_BASE_URL:
        _warn_base_default()

    catalog = _load_catalog()
    ep = _find_endpoint(catalog, args.path)
    if ep is None:
        sys.exit(f"ERROR: endpoint not found: {args.path}")

    # Resolve body.
    if args.body is not None:
        body = json.loads(args.body)
    elif args.body_file is not None:
        with open(args.body_file) as f:
            body = json.load(f)
    else:
        body = ep.get("example_body") or {}
        blank = [
            f for f in (ep.get("required_fields") or [])
            if f not in body or body[f] in ({}, [], "", None)
        ]
        if blank:
            print(
                f"ERROR: the catalog example body for {ep['path']} leaves required "
                f"field(s) {blank} empty, so the upstream would reject it.\n"
                f"       Supply a real body:  xfree02 call {ep['path']} --body '{{...}}'\n"
                f"       Inspect the schema:  xfree02 show {ep['path']}",
                file=sys.stderr,
            )
            sys.exit(2)

    url = base_url + "/v1" + ep["path"]
    data = json.dumps(body).encode() if body else b"{}"
    req = urllib.request.Request(
        url,
        data=data,
        headers=(
            {"Content-Type": "application/json", "X-API-Key": api_key}
            if api_key
            else {"Content-Type": "application/json"}
        ),
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as resp:
            resp_body = json.loads(resp.read().decode())
            print(json.dumps(resp_body, indent=2))
            # Footer on stderr so it doesn't pollute stdout pipelines.
            sc = resp.headers.get("X-Sponsored-Cents")
            cr = resp.headers.get("X-Caller-Remaining-Cents")
            if sc is not None or cr is not None:
                parts = []
                if sc is not None:
                    parts.append(f"sponsored_cents={sc}")
                if cr is not None:
                    parts.append(f"caller_remaining_cents={cr}")
                print("[ " + " ".join(parts) + " ]", file=sys.stderr)
    except urllib.error.HTTPError as exc:
        err_body = exc.read().decode()
        try:
            parsed = json.loads(err_body)
        except (json.JSONDecodeError, ValueError):
            parsed = {}
        code = exc.code
        if code == 402:
            print("ERROR: sponsorship exhausted.", file=sys.stderr)
            if isinstance(parsed, dict):
                if "retry_after_utc_date" in parsed:
                    print(f"  retry_after_utc_date: {parsed['retry_after_utc_date']}", file=sys.stderr)
                if "direct_url" in parsed:
                    print(f"  direct_url (pay yourself): {parsed['direct_url']}", file=sys.stderr)
        elif code == 403 and parsed.get("error") == "not_sponsored":
            print(
                f"ERROR: endpoint not sponsored; price_usd={parsed.get('price_usd')}.",
                file=sys.stderr,
            )
        elif code == 404:
            print("ERROR: unknown endpoint.", file=sys.stderr)
        else:
            print(f"ERROR: HTTP {code} — {err_body}", file=sys.stderr)
        sys.exit(1)


def cmd_health(args: argparse.Namespace) -> None:
    base_url = os.environ.get("XFREE02_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    if base_url == DEFAULT_BASE_URL:
        _warn_base_default()
    url = base_url + "/health"
    try:
        with urllib.request.urlopen(url) as resp:
            print(json.dumps(json.loads(resp.read().decode()), indent=2))
    except urllib.error.HTTPError as exc:
        print(f"ERROR: HTTP {exc.code}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:  # pragma: no cover
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(
        prog="xfree02",
        description="Query sponsored Nansen on-chain intelligence endpoints.",
    )
    sub = ap.add_subparsers(dest="command", required=True)

    # catalog
    p_cat = sub.add_parser("catalog", help="List available endpoints")
    p_cat.add_argument("--sponsored-only", action="store_true",
                       help="Show only sponsored endpoints (price_usd <= 0.01)")
    p_cat.add_argument("--max-price", type=str,
                       help="Maximum price_usd to include")

    # show
    p_show = sub.add_parser("show", help="Show details for one endpoint")
    p_show.add_argument("path", help="Endpoint path, e.g. /api/v1/perp-screener")

    # call
    p_call = sub.add_parser("call", help="Call an endpoint (POST)")
    p_call.add_argument("path", help="Endpoint path")
    body_grp = p_call.add_mutually_exclusive_group()
    body_grp.add_argument("--body", type=str, help="JSON body string")
    body_grp.add_argument("--body-file", type=str, help="File containing JSON body")

    # health
    sub.add_parser("health", help="Gateway health check")

    args = ap.parse_args()

    if args.command == "catalog":
        cmd_catalog(args)
    elif args.command == "show":
        cmd_show(args)
    elif args.command == "call":
        cmd_call(args)
    elif args.command == "health":
        cmd_health(args)


if __name__ == "__main__":
    main()
