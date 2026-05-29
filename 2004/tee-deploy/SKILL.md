---
name: "@2004/tee-deploy"
version: 0.2.0
description: Onboard a user to Phala Cloud and deploy a verifiable Starchild TEE agent — a minimal FastAPI runtime running inside an Intel TDX confidential VM, plus a published chat dashboard with attestation verification. Use when the user wants to "try TEE", "run an agent in a confidential VM", "deploy to Phala", or replicate the internal Starchild TEE test setup.
delivery: script
---

# tee-deploy — Phala TEE Agent Deployment

End-to-end skill that walks a brand-new user from "what is TEE" to a running agent inside an Intel TDX CVM with a public chat page, in one session.

## What this skill produces

| Output | Where | What it is |
|---|---|---|
| Live CVM | `https://<hash>-8000.dstack-pha-prod5.phala.network` | FastAPI agent inside Intel TDX, ~30s LLM round-trip, attestation on every reply |
| Chat dashboard | `https://community.iamstarchild.com/<userid>-<slug>` | Browser-side chat UI that talks directly to the CVM and verifies the TDX quote |
| Project dir | `workspace/projects/tee-deploy/<name>/` | All deploy artifacts (compose, dashboard, .cvm_url) |

## When NOT to use

- User wants to deploy their existing complex agent into TEE — this skill ships a fixed minimal agent (chat + a few tools). For arbitrary code, point them at the official Phala docs.
- User wants on-chain identity / ERC-8004 / multi-CVM orchestration — that's the `phala-cvm-orchestration` territory.

---

## The 6-phase workflow

Run sequentially. Do not skip phases — phase 1 sets the credentials phase 3 needs.

### Phase 1 · Onboarding (talk to user)

Before showing the checklist, **run BYOK detection first** so you know whether the user even needs to provide a new LLM key:

```bash
python3 skills/tee-deploy/assets/scripts/detect-byok.py
```

Output is a JSON array of compatible BYOK custom models. If non-empty, you can reuse one of them and skip asking for an LLM key entirely. Pick the **first 3-5 most useful** (prefer well-known providers: OpenAI, Anthropic-via-OpenAI-compat, DeepSeek, Qwen, Venice) and present them in the checklist.

Then present this checklist (translated to user's language if non-English):

```
Two things to set up — ~3 minutes total:

1. Register on Phala Cloud → https://cloud.phala.network/register
   Use GitHub login (fastest). You get $20 free credit + 1 free CVM trial.

2. Get an API token
   Settings → API Tokens → Create New Token → name it "starchild-tee-deploy"
   Copy the token. (Don't paste it in chat — I'll trigger a secure popup.)

3. LLM key for the agent inside the CVM:
   {{ if BYOK detected }}
     I found these BYOK models already configured in your workspace:
       [a] GPT-5 (OpenAI)        — gpt-5
       [b] DeepSeek Chat         — deepseek-chat
       [c] Qwen3 6 Plus          — qwen3.6-plus
       [d] use a new key instead (I'll pop a secure input)
     Reply with the letter, default [a].
   {{ else }}
     Pick a provider (any one): OpenAI / Anthropic-via-OpenAI-compat /
     DeepSeek / NEAR AI / Venice. I'll pop a secure input next.
   {{ end }}

Reply "ready" when you have the Phala token at hand.
```

WAIT for user to confirm. Do not trigger any popup until they say ready.

### Phase 2 · Collect credentials (BYOK reuse OR secure input)

**Branch on what user picked in Phase 1.**

**Branch A — User picked an existing BYOK (a/b/c):**

No popup needed for the LLM key. Resolve the chosen BYOK and write LLM_* into `/data/workspace/.env`:

```python
# Read the chosen BYOK row from detect-byok output, then:
import os, re
from pathlib import Path

chosen = {"label": "...", "base_url": "...", "model": "...", "key_env": "CUSTOM_KEY_..."}
key_value = os.environ.get(chosen["key_env"]) or _read_env_var(chosen["key_env"])

# Write LLM_* into /data/workspace/.env (replace if exists, append if not)
def upsert_env(path: Path, key: str, value: str):
    text = path.read_text() if path.exists() else ""
    pat = re.compile(rf"^{re.escape(key)}=.*$", re.MULTILINE)
    line = f"{key}={value}"
    text = pat.sub(line, text) if pat.search(text) else (text.rstrip() + "\n" + line + "\n")
    path.write_text(text)

env = Path("/data/workspace/.env")
upsert_env(env, "LLM_PROVIDER", "openai")  # all reused BYOKs are wire=openai
upsert_env(env, "LLM_API_KEY",  key_value)
upsert_env(env, "LLM_MODEL",    chosen["model"])
upsert_env(env, "LLM_BASE_URL", chosen["base_url"])
```

Then trigger a popup for ONLY the Phala token:

```python
request_env_input(
    reason="Phala Cloud API token (so the CLI can deploy the CVM)",
    env_vars=[
        {"key": "PHALA_CLOUD_API_KEY", "label": "Phala Cloud API Token", "required": True},
    ]
)
```

**Branch B — User picked "new key" or no BYOK was detected:**

Trigger the full popup:

```python
request_env_input(
    reason="Phala API token + the LLM key the agent inside the CVM will call out to",
    env_vars=[
        {"key": "PHALA_CLOUD_API_KEY", "label": "Phala Cloud API Token",      "required": True},
        {"key": "LLM_PROVIDER",        "label": "LLM Provider (openai|anthropic|near_ai|venice)", "required": True},
        {"key": "LLM_API_KEY",         "label": "LLM API Key (for the chosen provider)",          "required": True},
        {"key": "LLM_MODEL",           "label": "Model id (e.g. gpt-4o-mini, claude-sonnet-4.5)", "required": True},
    ]
)
```

After EITHER branch: STOP and wait for the next user turn before continuing to Phase 3. The popup is async — do not proceed in the same turn.

**Note on user privacy:** when reusing a BYOK, the resolved API key flows into the CVM's compose `.env.deploy` the same way as a fresh key — that's intentional (the agent inside the CVM needs the plaintext to call the LLM). The reuse only saves the user from re-entering it.

### Phase 3 · Set up the project directory

Default name is `starchild-tee-agent`. Let the user override if they want (e.g. their handle). Then:

```bash
NAME="${1:-starchild-tee-agent}"          # ask user, or default
PROJECT="workspace/projects/tee-deploy/$NAME"
SKILL_DIR="$(dirname $(realpath skills/tee-deploy/SKILL.md))"

mkdir -p "$PROJECT"
cp -r "$SKILL_DIR/assets/"* "$PROJECT/"
chmod +x "$PROJECT/scripts/"*.sh

echo "Project ready at $PROJECT"
ls "$PROJECT"
```

### Phase 4 · Deploy (the slow step — ~2 min)

```bash
cd workspace/projects/tee-deploy/<name>
bash scripts/deploy.sh
```

This will:
1. `npm install phala` locally (~30s first time)
2. Re-bake `compose/docker-compose.yml` with the current `app.py` base64-embedded (so the compose hash captures the exact agent code)
3. Generate `compose/.env.deploy` from workspace `.env` (only `LLM_*` vars, never the Phala token)
4. Call `phala deploy --wait -t tdx.small`
5. Resolve the public URL, write to `.cvm_url` and `dashboard/cvm.js`

⚠️ **The deploy step can take 2-5 minutes.** Phala has to schedule the CVM, pull the python:3.11-slim image, run the boot script that decodes app.py, and install Python deps inside the CVM. If the foreground times out, the deploy is still running in background — check with `phala cvms list` not by re-running.

If `npm install phala` is slow (>3 min) → run deploy.sh with `background=true` and poll the bash session.

### Phase 5 · Smoke test

After `.cvm_url` exists, run:

```bash
cd workspace/projects/tee-deploy/<name>
bash scripts/smoke-test.sh
```

This hits `/health`, `/attestation`, and `/chat` with a "say PONG" prompt. All three must pass before publishing. If `/chat` fails, the most likely cause is a bad `LLM_API_KEY` or wrong `LLM_MODEL` — read the response body for the upstream error and ask the user to re-enter via `request_env_input(force=True)`.

### Phase 6 · Publish the dashboard

Load the `community-publish` skill and run:

```python
# Inside the skill's exports
from exports import publish_preview
result = publish_preview(
    title="Starchild on TEE · Chat",
    dir="workspace/projects/tee-deploy/<name>/dashboard",
)
# result['public_url'] = "https://community.iamstarchild.com/<userid>-<slug>"
```

Read `community-publish/SKILL.md` before calling — flow may need a `preview(serve)` first then `publish_preview` against the preview id.

### Hand-off message to user

Tell the user in their language, plain and short:

- Public chat: `<community URL>`
- Direct CVM: `<CVM URL>`
- Attestation: `<CVM URL>/attestation` (returns TDX quote)
- Cost: ~$0.058/hour for tdx.small (~$42/month if left running)
- Stop CVM anytime via Phala dashboard → CVMs → Stop (no charge while stopped)

---

## Important gotchas (read before debugging)

- **Phala CLI is a per-project npm install.** Don't `npm install -g phala` — global installs cause version drift across users.
- **Deploy script reads `/data/workspace/.env` directly**, not the current shell env. If you set `LLM_API_KEY` only in a subshell it won't be picked up.
- **`compose/.env.deploy` never contains `PHALA_CLOUD_API_KEY`.** The Phala token is for the CLI to talk to Phala's control plane; it must not leak into the CVM environment. The deploy.sh whitelist explicitly excludes it.
- **The CVM URL is hash-based and changes every deploy.** If the user redeploys, the old URL dies. Always re-publish the dashboard or regenerate `dashboard/cvm.js`.
- **`app.py` is base64-embedded into compose.** Edit `app.py` and re-run `deploy.sh` — the compose hash will change, which means a *different* TDX measurement → attestation will reflect the new code. This is by design (the binding is what makes it verifiable).
- **`tdx.small` is the cheapest tier** at ~$0.058/hr. Don't propose larger tiers unless user asks — they're an order of magnitude more expensive and the minimal agent doesn't need them.
- **dstack socket** at `/var/run/dstack.sock` inside the CVM is the only way to fetch a fresh attestation quote. The volume mount in compose is mandatory.

---

## File layout

```
skills/tee-deploy/
├── SKILL.md                            # this file
└── assets/
    ├── app.py                          # FastAPI agent (chat + tools + attestation), 18KB
    ├── dashboard/
    │   ├── index.html                  # chat UI shell
    │   ├── app.js                      # talks directly to CVM, verifies report_data binding
    │   └── style.css
    └── scripts/
        ├── deploy.sh                   # the main worker (idempotent)
        ├── detect-byok.py              # finds reusable BYOK custom models in workspace config
        └── smoke-test.sh               # health + attestation + chat round-trip
```

After Phase 3 the user's project dir is a copy of `assets/` plus runtime files:

```
workspace/projects/tee-deploy/<name>/
├── app.py                              # source of truth (edit here, redeploy)
├── compose/
│   ├── docker-compose.yml              # generated by deploy.sh from app.py
│   └── .env.deploy                     # generated, only LLM_* vars
├── dashboard/
│   ├── index.html                      # CVM URL patched in by deploy.sh
│   ├── app.js, style.css
│   └── cvm.js                          # window.CVM_URL = "..."
├── scripts/deploy.sh, smoke-test.sh
├── node_modules/                       # phala CLI (local install)
├── package.json
└── .cvm_url                            # canonical URL after deploy
```

---

## What this skill explicitly does NOT do

- Does not write `PHALA_CLOUD_API_KEY` into the CVM (control plane only)
- Does not provide RA-TLS, reproducible build, signed manifest, egress allowlist — those are V1.5/V2 features tracked in `output/tee-plan` and not part of this minimal onboarding skill
- Does not auto-renew or monitor the CVM — user must watch Phala dashboard for credit exhaustion
- Does not pin a specific LLM provider — the agent inside the CVM speaks OpenAI-compatible HTTP and works with any compatible endpoint
