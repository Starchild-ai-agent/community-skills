---
name: "@1892/starchild-design-pack"
version: 1.1.0
author: Starchild
tags: [design, ui, ux, frontend, design-system, vibe-coding]
description: "Starchild UI/UX design + implementation playbook. Use when designing/refining interfaces, auditing UX quality, or converting design direction into concrete frontend edits. Defaults to Starchild style unless user specifies otherwise."

metadata:
  starchild:
    emoji: "🎨"
    skillKey: starchild-design-pack

user-invocable: true
---

# Starchild Design Pack

Use this skill whenever the user asks to design UI, improve UX, audit interface quality, or apply a design system.

## Default Style (unless user overrides)

- Primary: `#F84600`
- Background: `#000000`
- Surface: dark charcoal
- Text: `#FFFFFF`
- Radius: `12px–16px`
- Pill radius: `9999px`
- Font: `Google Sans`, fallback `system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif`

## Hard Guardrails

1. User direction always wins.
2. Keep files simple and compact; no over-engineered token systems unless requested.
3. Avoid AI-generic defaults: **no purple/violet/indigo/magenta accent-heavy palettes** unless explicitly requested.
4. Always define loading/empty/error/success states.
5. Always include accessibility basics (contrast, keyboard focus, semantic structure).

## What to Deliver

Choose the right level based on request:

- UI direction (layout, hierarchy, spacing)
- UX flow (states + edge cases)
- Design-system tokens/components
- Implementation plan (file-level edits + acceptance criteria)

If the user asks for "full":
1) direction → 2) UX states → 3) system tokens/components → 4) implementation plan.

## Quick Audit Checklist (fast pass)

- Theme foundation correct (dark vs light intent)
- Radius system consistent (12–16 + pill)
- Typography coherent (Google Sans default unless overridden)
- CTA hierarchy obvious (contrast, placement)
- Spacing breathable (not cramped)
- Border noise controlled (avoid heavy boxed UI)
- Interaction states present (hover/focus/disabled/loading/error)
- Accessibility baseline present
- Palette avoids default purple-family drift

## Task → Best Resource

- "Set visual direction" → `docs/aesthetic-tokens.md`
- "Do a quick UI audit" → `references/10-checklist-new-interfaces.md` + checklist above
- "Check fidelity to target style" → `references/11-checklist-fidelity.md`
- "Improve UX clarity" → `references/20-patterns-*.md`
- "Need examples/inspiration" → `data/*.csv` (reference only; not default authority)
- "Generate token scaffolding" → `scripts/design_system.py`

## Resource Map

- `docs/aesthetic-tokens.md` — canonical visual tokens
- `docs/CREDITS.md` — lineage/attribution
- `references/` — checklists + UX patterns
- `data/` — reference datasets (inspiration only)
- `scripts/` — utilities

## Notes

- Keep recommendations practical and implementation-ready.
- Prefer concrete component/state guidance over abstract design talk.
- Stay compatible with the project stack unless asked to switch.
