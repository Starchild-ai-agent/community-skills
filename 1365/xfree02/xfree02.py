#!/usr/bin/env python3
"""xFREE02 — Nansen x402 thin client — catalog lookup + pay-and-call.

The user pays from THEIR OWN wallet via the Starchild marketplace proxy.
This script holds no keys and no sponsor wallet.

  python3 xfree02.py catalog                     # list all 54 endpoints
  python3 xfree02.py catalog --search perp       # filter
  python3 xfree02.py show /api/v1/perp-screener  # example body + fields
  python3 xfree02.py call /api/v1/perp-screener --json '{"date":{"from":"2026-08-01","to":"2026-08-12"}}'
"""
import argparse
import json
import os
import subprocess
import sys

SERVICE_ID = "f17f7f91-a576-407c-bead-1eea320f7523"
PROXY_BASE = f"https://community.iamstarchild.com/proxy/{SERVICE_ID}"
HERE = os.path.dirname(os.path.abspath(__file__))
CATALOG = os.path.join(HERE, "references", "catalog.json")
BUY = os.path.join(os.path.dirname(HERE), "x402", "scripts", "buy.py")


def load():
    with open(CATALOG) as f:
        return json.load(f)["endpoints"]


def norm(p):
    return p if p.startswith("/") else "/" + p


def find(path):
    path = norm(path)
    for e in load():
        if e["path"] == path:
            return e
    return None


def cmd_catalog(a):
    rows = load()
    if a.search:
        q = a.search.lower()
        rows = [e for e in rows
                if q in e["path"].lower() or q in (e["label"] or "").lower()]
    if a.max_price is not None:
        rows = [e for e in rows if e["price_usd"] <= a.max_price]
    if a.json:
        print(json.dumps(rows, indent=1))
        return
    print(f"{len(rows)} endpoint(s)   [$ = price per call, body = example available]")
    for e in sorted(rows, key=lambda x: (x["price_usd"], x["path"])):
        flag = "ok " if e["body_source"] != "none" else "GAP"
        print(f"  ${e['price_usd']:<5.2f} {flag} {e['path']}")
        print(f"          {(e['label'] or '')[:88]}")


def cmd_show(a):
    e = find(a.path)
    if not e:
        print(f"not in catalog: {norm(a.path)}", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(e, indent=1))


def cmd_call(a):
    e = find(a.path)
    if not e:
        print(f"not in catalog: {norm(a.path)}", file=sys.stderr)
        sys.exit(1)
    body = a.json
    if body is None:
        if e["body_source"] == "none":
            print(f"no example body known for {e['path']} — pass --json explicitly",
                  file=sys.stderr)
            sys.exit(1)
        body = json.dumps(e["example_body"])
        print(f"# using catalog example body: {body}", file=sys.stderr)

    cap = a.max_usd if a.max_usd is not None else e["price_usd"]
    if e["price_usd"] > cap:
        print(f"price ${e['price_usd']:.2f} exceeds cap ${cap:.2f} — raise --max-usd",
              file=sys.stderr)
        sys.exit(2)

    if not os.path.exists(BUY):
        print("missing dependency: the `x402` skill is not installed.\n"
              "  install it, then run: bash skills/x402/setup.sh", file=sys.stderr)
        sys.exit(3)

    cmd = [sys.executable, BUY, "--url", PROXY_BASE + e["path"],
           "--method", "POST", "--json", body, "--max-usd", str(cap)]
    if a.network:
        cmd += ["--network", a.network]
    r = subprocess.run(cmd, capture_output=True, text=True)
    sys.stdout.write(r.stdout)
    if r.stderr:
        sys.stderr.write(r.stderr)
    sys.exit(r.returncode)


def main():
    p = argparse.ArgumentParser(description="xFREE02 — Nansen on-chain intelligence via x402")
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("catalog", help="list/search endpoints")
    c.add_argument("--search")
    c.add_argument("--max-price", type=float)
    c.add_argument("--json", action="store_true")
    c.set_defaults(fn=cmd_catalog)

    s = sub.add_parser("show", help="show one endpoint's schema + example body")
    s.add_argument("path")
    s.set_defaults(fn=cmd_show)

    k = sub.add_parser("call", help="pay and call an endpoint")
    k.add_argument("path")
    k.add_argument("--json", help="request body JSON (default: catalog example)")
    k.add_argument("--max-usd", type=float, help="spend cap (default: listed price)")
    k.add_argument("--network", help="CAIP-2, e.g. eip155:8453")
    k.set_defaults(fn=cmd_call)

    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
