---
name: "@2004/realtime-voice-preview"
version: 1.4.0
description: |
  One-click Starchild Live Preview: an OpenAI Realtime API voice interface connected
  to a Starchild Agent through ask_starchild. Supports a temporary-first work-thread
  selector and resumable background jobs with polling, cancellation and reconnect recovery.

  Use for "voice preview", "realtime voice", "语音测试", "talk to my agent",
  "实时语音", "voice thread", or "Starchild Live".
delivery: script
author: Starchild
tags: [openai, realtime, voice, webrtc, agent]
metadata:
  starchild:
    emoji: 🎙️
    skillKey: realtime-voice-preview
user-invocable: true
disable-model-invocation: false
---

## What this skill does

Creates **Starchild Live**, a WebRTC voice UI that leaves speech/VAD/interruption to
OpenAI Realtime and delegates Agent reasoning, files, memory, tools and workspace work
through one gateway tool: `ask_starchild`.

The skill bundles the complete project under `template/`. Its setup script creates or
updates the user's own copy at `output/projects/realtime-voice-preview/`; it does not rely
on this agent's pre-existing project. This integration uses **OpenAI Realtime, not Grok**.

## Prerequisites

1. `OPENAI_REALTIME_API_KEY` securely configured, with Realtime model access and billing.
2. Starchild runtime at `STARCHILD_RUNTIME_URL` (default `http://127.0.0.1:8000`).
3. Node.js for parser tests.

First check whether `OPENAI_REALTIME_API_KEY` is already configured. If it is missing,
call `request_env_input` for exactly that variable; never request or accept it in chat.
The secure prompt's visible guidance must tell the user to:

- create a project key at https://platform.openai.com/api-keys;
- enable billing / add credits on the same OpenAI project;
- confirm that project has Realtime API/model access;
- prefer a project-scoped key without unrelated permissions.

Stop and wait after requesting the key. Do not tell the user to edit `.env` manually.

## Workflow

### 1. Create the user's own project

```bash
python3 skills/realtime-voice-preview/scripts/setup.py
```

This copies the bundled template to `output/projects/realtime-voice-preview/`, preserves
any existing `.env`, checks runtime health and runs the 59 parser + 16 background tests.
Use `--target PATH` for another destination and `--force` to refresh bundled non-secret
files.

### 2. Start and serve

Serve with the Preview tool using these exact values:

- `title`: `OpenAI Realtime Voice Demo` (keep constant; it determines Preview ID)
- `dir`: `output/projects/realtime-voice-preview/src`
- `command`: `python3 server.py`
- `port`: `8765`

Then verify `GET http://127.0.0.1:8765/health` returns healthy. Tell the user to open the
Preview in a **separate, preferably full-screen browser tab**, grant microphone permission,
and test there rather than inside the embedded Preview iframe. Microphone permission is
more reliable in a top-level tab.

### 3. Thread route

Agent Settings exposes one selector. Preserve this ordering:

1. `temporary` — **Temporary — do not enter an existing thread**. This is the default.
2. `persistent` — dedicated voice-only context.
3. `thread:<id>` — recent normal work threads, newest first.

The browser sends the selected `route` only when saving `/bridge_config`. The server
maps it to the internal `isolated | persistent | selected` config. It must ignore any
per-call `thread_id` sent to `/agent_bridge`.

Temporary uses `is_temporary=True`, so it does not read or write an existing work
thread. A selected work-thread ID must be validated against `/bridge_threads`. Build
that catalog from the authenticated Thread Service (`/api/clawd/threads`), not runtime
`/sessions`: the Thread Service supplies user-facing titles. Render title first with
message count/activity as optional context; keep the thread ID only as the internal
option value. Filter temporary/voice/transport threads and cap the result set.

### 4. `ask_starchild` execution modes

The Realtime tool accepts `question` and optional `execution_mode`:

| Mode | Behavior |
|---|---|
| `wait` | Waits within a short safe budget; if unfinished, automatically returns HTTP 202 with a resumable `run_id` before the Preview gateway timeout |
| `background` | Immediately returns HTTP 202 with accepted `run_id` |
| `auto` | Conservative local selection; short ordinary questions try the bounded wait path, explicit background/continue or long task-like prompts use background |

For HTTP 202 the client must:

1. send exactly one `function_call_output` acknowledging accepted `run_id`;
2. persist pending job metadata and a bounded delivered-ID set in `localStorage`;
3. poll `GET /agent_jobs?run_id=...` about every two seconds;
4. offer cancel through `POST /agent_jobs/cancel`;
5. recover active jobs after reload/reconnect with `GET /agent_jobs`;
6. if disconnected, retain a terminal result as pending;
7. when the data channel is open, inject the verified terminal result once, mark it delivered, then use the existing response/continuation guard to request speech.

Never send a second function-call output for a background completion. Completion is a
new conversation message, not another output for the original `call_id`.

**Verbatim relay.** `ask_starchild.question` must carry the user's spoken words as
transcribed — the Realtime model must not paraphrase, summarize, translate, expand, or
guess intent. Realtime owns speech and turn-taking only; understanding belongs to the
Agent. If a request is genuinely ambiguous, the model asks the user out loud to clarify
rather than inventing a filled-in question. The tool description and system instructions
both enforce this so semantic drift never reaches the Agent.

**Temporary rolling context.** Temporary mode has no persisted thread history, so
elliptical follow-ups ("可以去做了吗", "那第二个呢") cannot be resolved server-side.
The browser keeps a rolling transcript (last ~12 turns) and sends it as the optional
`context` array with each `/agent_bridge` call. The server injects it — only when
`is_temporary` is true — as a compact `[Recent voice conversation]` block (capped to the
last 6 turns / 1200 chars) ahead of the verbatim spoken request. Selected/persistent
threads already have real history, so context is deliberately skipped there to avoid
duplication. `context` flows through both the synchronous and background-job paths.

Cancellation is cooperative. `cancel_requested` is active, not terminal; only report
`cancelled` after the worker observes the flag. The server retains sanitized job state
with TTL/cap bounds, allows one active job per effective thread, and reuses a recent
identical job's `run_id`.

### 5. Verify before delivery

```bash
python3 -m py_compile output/projects/realtime-voice-preview/src/server.py
node output/projects/realtime-voice-preview/src/test_function_calls.js
python3 output/projects/realtime-voice-preview/src/test_background_jobs.py
```

Expected: 59 function-call tests and 16 background-job tests pass. Also verify Preview
health and the live HTML title after restarting the service.

**Preview ID stability (do not skip).** The Preview tool derives the preview ID from the
`title` slug. Keep the serve `title` **constant** across every restart so the URL never
changes — product/brand renames belong in the HTML `<title>` and on-page copy only, never
in the serve `title`. Update code by re-serving the *same* title on the *same* port; never
stop-and-recreate under a new title, which silently mints a new ID and breaks the user's
saved URL.

## Endpoints

- `POST /session`, `GET /token`
- `POST /agent_bridge`
- `GET /agent_jobs`, `GET /agent_jobs?run_id=...`
- `POST /agent_jobs/cancel`
- `GET|POST /bridge_config`
- `GET /bridge_threads?agent_id=...`
- `GET /health`

## Design and safety rules

- `ask_starchild` is the only capability gateway; Realtime must not invent Agent data.
- Long-lived OpenAI keys stay server-side; only ephemeral client secrets reach browser.
- Preserve function-call event correlation, call-ID dedupe and the response continuation guard.
- Serialize runtime calls per effective thread and retain the short completed-result cache.
- Prefix every relayed runtime user message with a stable `[Starchild Live Voice Agent]` source marker and label the spoken request; this must be visible in selected work-thread history.
- Never hold `/agent_bridge` past the Preview gateway window. Use a shorter synchronous budget and promote unfinished `wait` calls to the existing background-job lifecycle.
- Parse bridge responses as text before JSON so an upstream HTML error becomes a useful diagnostic rather than `Unexpected token '<'`.
- Base64-wrap SDP in JSON across the Preview proxy.
- UI strings remain English; no hardcoded machine-specific public URL.
- Public publishing is optional and must use the `community-publish` skill.

## Troubleshooting

| Symptom | Check |
|---|---|
| No sound / connection fails | OpenAI billing, Realtime model access, mic permission |
| Agent bridge fails | Runtime `/health` and `STARCHILD_RUNTIME_URL` |
| `Unexpected token '<'` after ~30 seconds | Preview gateway returned HTML while a synchronous request was still running; ensure bounded wait auto-promotes to a `run_id` and the client validates response content before JSON parsing |
| Query interrupted | Duplicate tabs/calls; serialization and result cache must remain enabled |
| Work thread rejected | Refresh `/bridge_threads`, choose a recent thread, or use Temporary |
| Job result not spoken after reconnect | Confirm it remains pending locally, data channel is open, and delivered set does not already contain the run ID |
| Cancel stays `cancel_requested` | Worker/runtime cancellation is cooperative; wait for verified terminal state |
