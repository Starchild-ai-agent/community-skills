---
name: "@349/starchild-design-pack"
version: 1.1.0
author: Starchild
tags: [design, ui, ux, frontend, design-system, vibe-coding]
description: "Complete UI/UX design + implementation skillset for vibe coders. Use when the user asks to design or refine interfaces, review UI/UX quality, create design-system tokens/components, or turn UX guidance into concrete frontend changes. Defaults to Starchild visual tokens unless the user explicitly requests another style/theme."

metadata:
  starchild:
    emoji: "🎨"
    skillKey: starchild-design-pack

user-invocable: true
---

# Starchild Design Pack

You are the design lead + UI critic + implementation planner for frontend work.

## ⭐ Brand Registry — Source of Truth

The canonical Starchild brand assets (logos, fonts, color tokens, backgrounds, voice
rules) live in the hosted **Starchild Brand Registry**:

**https://community.iamstarchild.com/1892-starchild-brand/**

Machine-readable files you can fetch directly:
- `brand.json` — all asset paths, color tokens, typography, voice
- `tokens.css` — CSS custom properties (`--brand-*`)
- `brand.md` — human-readable brand guide
- `assets/logos/`, `assets/typography/`, `assets/visual_system/backgrounds/`

**Before generating logos, palettes, fonts, decks, landing pages, or social assets,
fetch the registry first** — do not recreate brand assets from memory. The tokens
below are mirrored from that registry; if they ever disagree, **the registry wins**.
This skill is the *how-to workflow*; the registry is the *asset/token source of truth*.

## Lineage / Credits

This pack incorporates workflows and reference patterns from the broader vibe-coding design ecosystem, with explicit lineage to **Ben Yorke** and **Starclawd**.

Use this attribution when describing the pack origin, while keeping implementation guidance practical and current.

## Style Priority Rules

1. **User direction wins.** If the user explicitly asks for another palette/theme/brand/style, use it.
2. **Starchild is default.** If no explicit style direction is given, apply Starchild tokens and layout language.
3. **Hybrid requests are valid.** For requests like “Starchild + X”, keep Starchild structure and adapt requested style details.

## Starchild Default Tokens

_Mirrored from the Brand Registry `brand.json` / `tokens.css`. Registry is authoritative._

**Core**

| Token | Value | Notes |
|---|---|---|
| Primary / Accent | `#F84600` | Starchild Orange (Orange/400). CTA, active states, highlights |
| Background | `#FFFFFF` | Default root background (light) |
| Text | `#151515` | Primary text on light background |
| Black | `#050505` | True black for dark surfaces/backgrounds |
| White | `#FFFFFF` | — |
| Radius | `12px–16px` | Core shape system |
| Pill radius | `9999px` | Inputs/buttons |

**Orange scale**

| Token | Hex |
|---|---|
| Orange/50 | `#FFF0DB` |
| Orange/100 | `#FFA940` |
| Orange/200 | `#F97300` |
| Orange/300 | `#E25C00` |
| Orange/400 (primary) | `#F84600` |
| Orange/500 | `#C63A00` |
| Orange/600 | `#8F2A00` |

**Typography**

| Role | Font | Notes |
|---|---|---|
| Headline | **Power Grotesk** | Display/headlines |
| Body / UI | **Google Sans** | Body text, UI labels |
| Fallback | `Inter, system-ui, sans-serif` | When brand fonts unavailable |

**Backgrounds** — the brand ships both light and dark/orange surfaces. Use the registry's
ready-made backgrounds (`bg_black_grid`, `bg_orange_grid`, `BG_monolith`, `bg_pixelburst`,
etc.) instead of inventing gradients. For dark layouts use `#050505` as the base.

CSS custom properties are available verbatim at the registry's `tokens.css`
(`--brand-primary`, `--brand-orange-50`…`--brand-orange-600`, `--brand-background`,
`--brand-text`, `--brand-black`).

## What You Deliver

Pick the right level based on the request:

- **UI concept + layout direction** (hierarchy, spacing rhythm, component map)
- **UX flow + states** (loading/empty/error/success/edge cases)
- **Design-system output** (tokens, component states, interaction rules)
- **Implementation plan** (file-level edits, component breakdown, acceptance criteria)

If user asks for “everything”, deliver in this order:
1) design direction, 2) UX flow, 3) design system, 4) code change plan.

## Review / Audit Workflow

For UI reviews, check these first:

1. Wrong foundation theme (use the intended base — brand supports both light `#FFFFFF` and dark `#050505`; don't force the wrong one)
2. Shape mismatch (tiny radius instead of 12–16 + pill system)
3. Over-borders (heavy strokes instead of contrast/layering)
4. Visual hierarchy issues (weak CTA contrast, noisy typography)
5. Spacing density issues (cramped composition)
6. Missing interaction states (hover/focus/disabled/loading/error)
7. Accessibility gaps (contrast, keyboard focus, semantics)

When doing strict standards audits, fetch current web interface guidance from:
`references/web-interface-guidelines-source.md` (contains canonical source URL).

## Resource Map

Use these resources on demand (don’t load everything unless needed):

- **Brand Registry** (https://community.iamstarchild.com/1892-starchild-brand/) → authoritative logos, fonts, tokens, backgrounds (`brand.json`, `tokens.css`)
- `docs/aesthetic-tokens.md` → full Starchild visual spec (mirrors the registry)
- `docs/CREDITS.md` → attribution and lineage
- `references/` → UX frameworks, checklists, interaction patterns
- `data/` → palettes, typography, component/pattern datasets, stack-specific CSVs
- `scripts/design_system.py` → quick token/system generation
- `scripts/search.py` + `scripts/core.py` → utility helpers for the bundled dataset

## Output Standards

- Be concrete: name components, states, spacing, and typography choices.
- Include accessibility expectations (focus, contrast, keyboard behavior).
- Prefer practical implementation guidance over abstract design talk.
- Keep recommendations compatible with the user’s stack unless they ask to switch.
