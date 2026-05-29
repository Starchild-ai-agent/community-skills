#!/usr/bin/env bash
# Deploy the Starchild TEE agent to Phala Cloud (dstack / Intel TDX).
#
# Usage:  bash deploy.sh [cvm-name]
# Assumes cwd = project root (containing app.py, compose/, dashboard/).
#
# Required env vars (read from /data/workspace/.env):
#   PHALA_CLOUD_API_KEY    Phala Cloud API token (Settings → API Tokens)
#   LLM_PROVIDER           openai | anthropic | near_ai | venice  (string tag)
#   LLM_API_KEY            API key for the chosen provider
#   LLM_MODEL              model id, e.g. gpt-4o-mini, claude-sonnet-4.5
#   LLM_BASE_URL           (optional) OpenAI-compatible base URL
#
# Output:
#   .cvm_url               Public HTTPS endpoint of the deployed CVM
#   dashboard/cvm.js       window.CVM_URL = "<url>"  (for the chat UI)
#   compose/docker-compose.yml  Generated compose with app.py base64-embedded

set -euo pipefail

PROJECT_DIR="$(pwd)"
NAME="${1:-${CVM_NAME:-starchild-tee-agent}}"

# --- 0. Sanity ---------------------------------------------------------------
if [ ! -f /data/workspace/.env ]; then
  echo "❌ /data/workspace/.env not found (need PHALA_CLOUD_API_KEY + LLM_*)"
  exit 1
fi
if [ ! -f app.py ]; then
  echo "❌ app.py missing in $(pwd) — did the project dir get set up?"
  exit 1
fi

# Load env (shellcheck-safe)
set -a
# shellcheck disable=SC1091
source /data/workspace/.env
set +a

for v in PHALA_CLOUD_API_KEY LLM_PROVIDER LLM_API_KEY LLM_MODEL; do
  if [ -z "${!v:-}" ]; then
    echo "❌ missing required env var: $v"
    exit 1
  fi
done

# --- 1. Install phala CLI locally (idempotent) -------------------------------
PHALA="./node_modules/.bin/phala"
if [ ! -x "$PHALA" ]; then
  echo "▶ Installing phala CLI (one-time, ~30s)…"
  if [ ! -f package.json ]; then echo '{"private":true}' > package.json; fi
  npm install --silent --no-fund --no-audit phala
fi

# --- 2. Bake app.py → docker-compose.yml -------------------------------------
mkdir -p compose
echo "▶ Re-baking compose/docker-compose.yml with current app.py"
python3 - <<'PY'
import base64, hashlib
from pathlib import Path
src = Path("app.py").read_bytes()
b64 = base64.b64encode(src).decode()
sha = hashlib.sha256(src).hexdigest()
compose = f"""# Starchild TEE Agent — Phala Cloud / dstack docker-compose
# Source sha256: {sha}
# app.py is base64-embedded so the compose hash captures the exact agent
# code → Intel TDX attestation binds to this code.

services:
  agent:
    image: python:3.11-slim
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      LLM_PROVIDER: ${{LLM_PROVIDER}}
      LLM_API_KEY:  ${{LLM_API_KEY}}
      LLM_MODEL:    ${{LLM_MODEL}}
      LLM_BASE_URL: ${{LLM_BASE_URL}}
      SYSTEM_PROMPT: ${{SYSTEM_PROMPT:-}}
      WORKSPACE_DIR: /data/workspace
      DSTACK_SOCK:   /var/run/dstack.sock
      APP_PY_B64: |
{chr(10).join('        ' + b64[i:i+76] for i in range(0, len(b64), 76))}
      APP_PY_SHA256: "{sha}"
    volumes:
      - /var/run/dstack.sock:/var/run/dstack.sock
      - workspace:/data/workspace
    command:
      - bash
      - -c
      - |
        set -euo pipefail
        echo "[boot] decoding agent code (expected sha256: $${{APP_PY_SHA256}})"
        printf '%s' "$$APP_PY_B64" | tr -d ' \\n' | base64 -d > /app.py
        actual=$$(sha256sum /app.py | awk '{{print $$1}}')
        if [ "$$actual" != "$$APP_PY_SHA256" ]; then
          echo "[boot] FATAL: app.py sha mismatch $$actual vs $$APP_PY_SHA256"; exit 1;
        fi
        echo "[boot] sha256 verified ✔  installing deps…"
        pip install --quiet --no-cache-dir 'fastapi==0.115.0' 'uvicorn[standard]==0.30.6' 'httpx==0.27.2' 'pydantic==2.9.2'
        mkdir -p /data/workspace
        echo "[boot] starting uvicorn on :8000"
        cd / && exec uvicorn app:app --host 0.0.0.0 --port 8000 --log-level info

volumes:
  workspace:
"""
Path("compose/docker-compose.yml").write_text(compose)
print(f"  app.py: {len(src)} bytes, sha256: {sha[:16]}…")
PY

# --- 3. Refresh compose/.env.deploy (only LLM_* vars, NEVER Phala token) -----
python3 - <<'PY'
from pathlib import Path
keep = ["LLM_PROVIDER", "LLM_API_KEY", "LLM_MODEL", "LLM_BASE_URL", "SYSTEM_PROMPT"]
out = {}
for ln in Path("/data/workspace/.env").read_text().splitlines():
    if "=" in ln and not ln.startswith("#"):
        k, _, v = ln.partition("=")
        if k.strip() in keep:
            out[k.strip()] = v
Path("compose/.env.deploy").write_text("\n".join(f"{k}={v}" for k, v in out.items()) + "\n")
PY

# --- 4. Deploy to Phala ------------------------------------------------------
echo ""
echo "▶ Deploying to Phala Cloud (name=$NAME, type=tdx.small)"
"$PHALA" deploy \
  -n "$NAME" \
  -c compose/docker-compose.yml \
  -e compose/.env.deploy \
  -t tdx.small \
  --wait \
  -j

# --- 5. Capture public URL + write into dashboard ----------------------------
echo ""
echo "▶ Resolving public URL…"
CVM_URL=$("$PHALA" cvms get --cvm-id "$NAME" -j | python3 -c "
import sys, json
d = json.load(sys.stdin)
for ep in d.get('endpoints', []):
    if 'app' in ep:
        print(ep['app'])
        break
")

if [ -z "${CVM_URL:-}" ]; then
  echo "⚠️  Could not resolve CVM URL automatically — check Phala dashboard"
  exit 1
fi

echo "$CVM_URL" > .cvm_url

# Write cvm.js for dashboard (overrides default input)
if [ -d dashboard ]; then
  cat > dashboard/cvm.js <<EOF
// Generated by deploy.sh — do not edit by hand
window.CVM_URL = "$CVM_URL";
EOF
  # Also patch the placeholder in index.html
  sed -i "s|__CVM_URL__|$CVM_URL|g" dashboard/index.html
fi

echo ""
echo "✅ Deployed."
echo "   CVM:        $CVM_URL"
echo "   Health:     $CVM_URL/health"
echo "   Attest:     $CVM_URL/attestation"
echo "   Saved to:   $PROJECT_DIR/.cvm_url"
