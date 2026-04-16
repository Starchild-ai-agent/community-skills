# Starchild Design System

Canonical default visual system for Starchild interfaces.

## Core Tokens

### Colors
- **Primary:** `#F84600`
- **Background:** `#000000`
- **Surface:** dark charcoal / near-black grays
- **Text:** `#FFFFFF`
- **Semantic:** green (success), red (error), blue/cyan (informational data)

### Color Guardrail
- Avoid default **purple/violet/indigo/magenta** accent-heavy schemes unless the user explicitly asks for them.
- Default to orange-first accents plus neutral dark support colors.

### Typography
- **Primary font:** Google Sans
- **Fallback stack:** `system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif`
- **Weights:**
  - Headers: 600–700
  - Body: 400
  - Labels: 500

### Shape + Rhythm
- **Radius:** 12–16px for cards/components
- **Pill controls:** fully rounded (`9999px`) for buttons/inputs where appropriate
- **Borders:** minimal; rely on layered contrast rather than heavy outlines
- **Spacing:** generous, breathable composition

## Component Direction

- **Inputs:** dark surface, strong contrast text, clear focus ring
- **Buttons:** clear visual hierarchy (primary vs secondary), rounded geometry
- **Cards/Panels:** subtle elevation via tone contrast, not thick borders
- **Icons:** clean and minimal; avoid decorative clutter

## UX State Minimum

Every production UI should define:
- loading
- empty
- error
- success
- disabled/focus interactions

## Simplicity Rule

Keep design files simple and compact. Avoid bloated token taxonomies unless explicitly requested.
