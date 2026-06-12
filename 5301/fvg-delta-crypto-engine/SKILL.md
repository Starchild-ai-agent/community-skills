---
name: "@5301/fvg-delta-crypto-engine"
version: 5.5.0
---

# FVG-Delta Crypto Signal Engine — Agent / Maintainer Guide (v5.5)

This is the single source of truth for any AI agent or engineer taking over this
project. Read it fully before touching `app.py`. It explains the strategy, the
code workflow, every bug that was fixed in this revision, the current state, and
the rules for updating the app and its docs safely.

---

## 1. What the app is

A production-style FastAPI service that scans **MEXC UST-M perpetual futures** on
**closed 15-minute candles**, runs a strict Smart-Money-Concept (SMC) staged
state machine, draws annotated chart screenshots, sends Telegram alerts for the
late stages, and serves a live auto-updating dashboard with an in-memory Trade
History. It is hosted on **Hugging Face Spaces (Docker SDK)**.

Single file does almost everything: `app.py`. Everything else is config/docs/entrypoints.

---

## 2. The strategy (must preserve)

The engine hunts the classic SMC continuation sequence. A setup walks forward
through five stages and is **never allowed to skip or silently regress**:

| Stage | Meaning | Where it shows |
|------|---------|----------------|
| 0 | Zone acquired: a valid impulse + FVG (fair-value gap) exists | Internal only |
| 1 | First retracement liquidity locked **and** a BoS close beyond the impulse wick extreme, with the FVG still **clean** (untouched) and liquidity untapped before the break | Dashboard |
| 2 | Price breaks **and closes** past the first liquidity (a real sweep, not a wick) — FVG still clean | Dashboard |
| 3 | Price interacts with (touches) the FVG zone | Dashboard **+ Telegram** |
| 4 | An opposite-direction confirmation candle prints a clean reversal out of the FVG → verified entry with dynamic SL/TP | Dashboard **+ Telegram** |

Key rules baked into the code (do not weaken without explicit user request):

- **Closed candles only.** `bars[-1]` (forming) is never used for decisions. The
  most recent *closed* candle is `bars[-2]` (`last_closed = len(bars) - 2`).
- **FVG must be clean for Stage 1 & 2.** If any candle enters the FVG before the
  liquidity sweep, the textbook order is broken → invalidate. Only Stage 3 & 4
  involve FVG interaction.
- **Close through the FVG against the setup = invalidation.** This applies before
  Stage 1 (waiting), during Stage 1–3, and specifically at Stage 3 a close back
  through the FVG (a "Stage-3 invalidation") means the setup must **never** be
  promoted to Stage 4.
- **Only NEW opportunities.** A confirmation whose SL/TP have already played out
  in history is discarded (freshness gate) — it is not surfaced and not recorded.
- **Lock-forward indices.** Each transition's bar index is searched once and
  stored on the `SetupState` (`bos_break_idx`, `stage2_break_idx`,
  `fvg_interaction_idx`, locked liquidity/BoS). Subsequent cycles only look for
  the next transition, so stages don't flicker on transient empty scans.

### Dynamic SL / TP (v5.5)

- **SL** sits a little **past the FVG far edge** (`z.low` for LONG, `z.high` for
  SHORT) plus `SL_FVG_BUFFER_ATR`. If a recent order-block / body swing sits just
  beyond the FVG within `OB_MAX_DISTANCE_ATR` (default 1.0×ATR), the SL anchors to
  that instead — but it is **never placed far from the FVG**. Floors
  (`MIN_STOP_ATR_MULT`, `MIN_STOP_PCT`) stop a single candle from instant-stopping.
- **Risk** `R = max(structural, MIN_STOP_ATR_MULT·ATR, entry·MIN_STOP_PCT/100)`.
- **TP2** = farther of `TP2_RR·R` (default 3R) and the nearest resting liquidity /
  opposing swing beyond entry (`TP_SWING_LOOKBACK`). `target_source` records which.
- **TP1** = midpoint between entry and TP2 (50% of the target distance).
- **Breakeven** is a real outcome: once TP1 prints, the user moves SL to entry, so
  if price returns to entry after TP1 the trade resolves as
  `Breakeven (TP1 then entry)` (see `_sequential_outcome`).

---

## 3. Code workflow (how a scan cycle flows)

```
scanner_loop()                      # every SCAN_INTERVAL_SECONDS
  └─ picks = shard rotation + every active (stage>=1) symbol
       └─ process_symbol(symbol)
            ├─ load_bars()                      # MEXC kline (gzip/deflate; brotli installed)
            ├─ evaluate_stages(st)              # THE state machine (see below)
            ├─ record_stage4_open()             # when a FRESH stage 4 first appears
            ├─ _stage4_expired() -> close_stage4_trade()   # SL/TP2/breakeven -> history
            └─ maybe_send_stage_alerts()        # Stage 3 & 4 Telegram (photo first, then text)
```

`evaluate_stages(st)` order of operations:
1. Acquire a zone via `detect_latest_zone()` if none (impulse + FVG quality gates).
2. TTL / max-age expiry.
3. Hard invalidation: close through FVG against the setup (stages 1–3).
4. `_lock_first_liquidity()` — locks first retracement liquidity + immutable BoS
   level (impulse wick extreme) once.
5. Stage 1 (BoS close), Stage 2 (liquidity sweep, with premature-FVG-touch
   invalidation), Stage 3 (FVG interaction), Stage 4 (confirmation candle).
6. Stage-3 close-through invalidation guard before any Stage-4 promotion.
7. Freshness gate: discard already-played-out confirmations.
8. `final_stage = desired_stage` (sequential, monotonic via locked indices).

Charts: `draw_chart()` (live state) and `draw_trade_chart()` (closed-trade
snapshot from a stored history row). BoS is drawn as a **horizontal line at the
impulse wick extreme** from the anchor candle to the breaking candle, with a
diamond on the anchor and an arrow on the break candle. FVG box is anchored to the
gap candle (`fvg_idx - 1`).

---

## 4. What was broken and what this revision fixed

| Symptom reported | Root cause | Fix |
|---|---|---|
| Setups invalidated at Stage 3 were promoted to Stage 4, hit SL, and got recorded | No guard for a close back through the FVG between interaction and confirmation; `max()` stage-lock force-jumped to 4 | Added Stage-3 close-through invalidation guard; removed `max()` jump so stages are sequential from locked indices |
| No Stage-3 rows ever visible | Confirmation in history made stage jump 0→4 in one cycle, skipping 3; also `/api/state` capped `states[:320]` so later symbols were hidden on live update | Sequential staging keeps 3 visible until a clean confirm; `/api/state` now always includes **every** stage≥1 symbol |
| Already-played-out / already-hit-TP setups surfaced at Stage 1 / Stage 4 | No freshness check | Freshness gate: `_levels_already_hit()` → discard (no promote, no record) |
| Telegram never fired though tables populated | Stage-4 that already expired reset to 0 before alert; Stage 3 skipped | Sequential staging + freshness keep genuine live 3/4 states long enough to alert; alert order is photo then text |
| SL too far from price | SL anchored to the candle before confirmation (could be distant) | SL now FVG-edge anchored, only extends to a nearby OB within `OB_MAX_DISTANCE_ATR` |
| Breakeven not modeled | Outcome used `any()` (order-blind) | `_sequential_outcome()` walks candles in time order; TP1-then-entry = breakeven |
| BoS plotted near the liquidity line / drooping diagonal | Diagonal from extreme to break close | Horizontal BoS line at the wick extreme, anchor diamond + break arrow |
| Dashboard live update dropped/hid rows, snapped to empty | `/api/state` 320-cap + heavy server-rendered duplication | Full active-state payload; client patches rows in place from `/api/state` |
| MEXC requests intermittently failed | Missing brotli decoder (`Can not decode content-encoding: br`) | `brotli` pinned in `requirements.txt`; sessions send `Accept-Encoding: gzip, deflate` |

---

## 5. Current state

- Engine: rebuilt, lock-forward, sequential. Verified against live MEXC data:
  zones detected, stages advance, fresh Stage-4 setups produce correct
  FVG-anchored SL and 3R/liquidity TP2, and resolve to SL / TP2 / breakeven in
  Trade History.
- Stage-4 is intentionally selective: at any single instant a brand-new
  confirmation (entry candle = latest closed candle, nothing played out yet) is
  rare, so a static snapshot may show few/none. Over a continuous live session the
  engine accumulates them and writes Trade History on expiry.
- Trade History is **in-memory only** (`TRADE_HISTORY` deque, session-scoped,
  wiped on restart). No disk persistence — the HF Spaces FS is ephemeral/read-only.
- Dashboard redesigned: animated gradient/grid background, radar logo with sweep,
  minimal header (logo, title, one-line description, tags, "Version 5.5 Active"),
  compact metric cards, compact tables that fit to width on desktop and scroll on
  mobile, in-place live refresh via `/api/state` (no page reload).

---

## 6. Important code map

```
app.py
  CFG (env config)                 ~line 48   ← all tunables; add new ones here
  Candle / Zone / SetupState / Stats          dataclasses
  _sequential_outcome()                       ← order-aware SL/TP2/breakeven
  _stage4_expired()                           ← terminal resolution (SL/TP2/BE)
  record_stage4_open / close_stage4_trade     ← Trade History lifecycle
  detect_latest_zone()                        ← impulse + FVG quality gates
  _lock_first_liquidity()                     ← locks liquidity + BoS extreme
  build_trade_levels()                        ← dynamic SL/TP (FVG-anchored)
  _levels_already_hit()                       ← freshness gate
  evaluate_stages()                           ← THE state machine
  draw_chart / draw_trade_chart()             ← matplotlib overlays
  maybe_send_stage_alerts()                   ← Telegram (stage 3 & 4 only)
  process_symbol / scanner_loop()             ← orchestration
  api_state()  ~line 1515                     ← live JSON (sends ALL active states)
  dashboard() ~line 1607                      ← HTML/CSS/JS (f-string)
```

Other files: `preflight_check.py`, `requirements.txt`, `start.sh`,
`run_one_shot.sh`, `README.md` (HF metadata block is immutable),
`STRATEGY_DETAILED_SPEC.txt`, `VARIABLES_AND_SECRETS_GUIDE.txt`.

---

## 7. Rules for updating the app (do not break it)

1. **Never alter the README metadata block** (first `---` … second `---`). Hugging
   Face uses it for hosting. Copy it byte-for-byte on any rewrite.
2. **The dashboard HTML is a Python f-string.** Every literal `{` or `}` in CSS/JS
   must be doubled (`{{` / `}}`). After editing, run
   `python3 -c "import ast; ast.parse(open('app.py').read())"` and grep the rendered
   HTML for stray single braces / typos before shipping.
3. **Keep element IDs stable.** The live JS targets `last-scan`, `m-symbols`,
   `m-scanned`, `m-zones`, `m-stage1-count`…`m-stage4-count`, `m-invalidations`,
   `c-stage1`…`c-stage4`, `c-trades`, `rows-stage1`…`rows-stage4`, `rows-trades`,
   `rows-alerts`, `rows-events`. Removing an ID is safe (JS guards with `if(el)`),
   but renaming a still-referenced one breaks live update.
4. **`/api/state` must keep returning every stage≥1 symbol.** Do not re-introduce a
   small slice cap on `states` or live rows will disappear again.
5. **Closed candles only.** Use `bars[-2]` / `last_closed`. Never decide on `bars[-1]`.
6. **Don't add disk persistence** for Trade History (HF FS is ephemeral/read-only).
7. **Preserve stage strictness:** sequential, no skipping, FVG clean for 1&2,
   close-through = invalidation, freshness gate for stage 4. If you must tune
   sensitivity, prefer CFG env vars over hard-coding.
8. **Add new tunables to `CFG`** (with an env override and a sane default) and
   document them in `VARIABLES_AND_SECRETS_GUIDE.txt`.
9. **Test before shipping:** `python preflight_check.py`, then a short live boot
   (`uvicorn app:app`) and hit `/health`, `/api/state`, `/`, `/api/chart.png`.

---

## 8. Rules for updating the docs

Whenever you change behavior, update **all** of these in the same change so they
never drift:

- `AGENT.md` (this file) — add the symptom→cause→fix row and any new rule.
- `STRATEGY_DETAILED_SPEC.txt` — exact strategy/stage/level behavior.
- `VARIABLES_AND_SECRETS_GUIDE.txt` — any new/changed env var, with example values.
- `README.md` — user-facing summary (never touch the metadata block).

Write explanations with concrete examples (worked numbers / a sample symbol),
matching the style already in those files.

---

## 9. Deploy notes (Hugging Face Spaces)

- Docker SDK. Container runs `start.sh` → `preflight_check.py` → `uvicorn app:app`
  on `$PORT` (default 7860).
- Required secrets: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`. Without them the UI
  still runs; Telegram alerts are skipped and logged.
- Tunables are all env vars (see the variables guide). Defaults are production-safe.
