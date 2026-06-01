# Starchild Design System

This skill defines the core aesthetic for all Starchild interfaces.

> **Source of truth:** the hosted Brand Registry at
> https://community.iamstarchild.com/1892-starchild-brand/
> (`brand.json` / `tokens.css`). If anything here disagrees with the registry,
> the registry wins. Fetch it before generating brand assets.

## Visual Identity

### Colors
- **Primary / Accent:** `#F84600` (Starchild Orange, Orange/400)
- **Background:** `#FFFFFF` (default light root background)
- **Text:** `#151515` (primary text on light)
- **Black:** `#050505` (true black for dark surfaces/backgrounds)
- **Containers:** dark charcoal on dark layouts; subtle tinted surfaces on light
- **Orange scale:** `#FFF0DB` · `#FFA940` · `#F97300` · `#E25C00` · `#F84600` · `#C63A00` · `#8F2A00`

The brand ships **both light and dark/orange** surfaces. Prefer the registry's
ready-made backgrounds (black grid, orange grid, monolith, pixelburst) over invented gradients.

### Typography
- **Headline:** Power Grotesk (display/headlines)
- **Body / UI:** Google Sans
- **Fallback:** `Inter, system-ui, sans-serif`
- **Hierarchy:**
  - **Headers:** 600-700 (Semibold/Bold)
  - **Body:** 400 (Regular)
  - **Labels:** 500 (Medium)
- **Spacing:** Generous, avoid cramped layouts.

### Shapes & Borders
- **Corners:** 12-16px radius (Generous, soft curves)
- **UI Elements:** Pill-shaped buttons and input fields (fully rounded ends).
- **Strokes:** Minimal borders; rely on background color contrast.

### Layout Patterns
- **Composition:** Centered focus.
- **Whitespace:** Generous, breathing room.
- **Anchor:** Bottom-anchored UI (e.g., chat/input fields).
- **Depth:** Floating components on dark backgrounds.

### Components
- **Input fields:** Dark background, rounded pill shape.
- **Buttons/Selectors:** Subtle background differentiation, rounded.
- **Icons:** Minimal, line-based.
- **Disclaimer text:** Small, gray, bottom-positioned.

---

## Skill Implementation
- **Zen-Layout Template:** Enforce centered composition, bottom-anchored input, and generous whitespace.
- **Pill-Metric:** Standardize all inputs, buttons, and cards on 12-16px corner radius.
