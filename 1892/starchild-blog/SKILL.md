---
name: "@1892/starchild-blog"
version: 1.0.0
description: End-to-end workflow for the Starchild Blog — create/import drafts, format articles, set titles and (mandatory) hero images, add SEO structures, preview, and publish to the protected production slug. Use for any Starchild blog article work: new posts, importing community/X articles, editing, or shipping live.
author: Starchild
tags: ["blog", "content", "publishing", "seo", "starchild", "static-site"]
metadata:
  starchild:
    emoji: "📝"
    skillKey: starchild-blog
user-invocable: true
---

# Starchild Blog

Static Python site generator. One source of truth, deterministic build, zero
external JS at runtime (Chart.js is vendored). This skill covers the full
lifecycle: draft → format → title + hero → SEO → preview → publish.

## Project layout

Root: `output/projects/starchild-blog/`

```
config.py                 site constants (SITE_URL, SITE_NAME, CTA, UTM…)
build.py                  generator; `python3 build.py [--check]`
scripts/import_article.py import any HTML article → draft (reusable)
scripts/og_image.py       auto-generates OG cards when no og_image set
templates/                base.html, home.html, post.html, tag.html
assets/                   style.css, fonts, wordmark, vendor/chart.umd.min.js
assets/images/            hero images live here
content/posts/            YYYY-MM-DD-<slug>.md  (source of truth)
public/                   BUILD OUTPUT — never edit by hand (gitignored)
public/drafts/            standalone draft pages + mirrored assets
```

### Outbound UTM scheme

All marketing links off the blog go through `build._utm_url()` so GA/analytics
can attribute traffic. Constants live in `config.py`:

| Param | Value | Notes |
|---|---|---|
| `utm_source` | `blog` (`UTM_SOURCE`) | fixed |
| `utm_medium` | placement name | `nav`, `footer`, `article_cta` |
| `utm_campaign` | optional | set `UTM_CAMPAIGN` when a named campaign is live |
| `utm_content` | optional | pass `content=` to `_utm_url` for A/B or slot labels |

Currently tagged:

- Top-nav **Create your agent** → `medium=nav`
- In-article CTA block → `medium=article_cta` + `content=<slug>`
- Footer **iamstarchild.com** → `medium=footer`

Article CTAs always include `utm_content=<post.slug>` so product analytics
(PostHog/GA) can rank which posts drive conversions. Nav/footer stay generic
(no content param) so sitewide clicks are not forced into one article's bucket.

Example article CTA:
```
https://iamstarchild.com?utm_source=blog&utm_medium=article_cta&utm_content=smart-routing-value-benchmark
```

Never UTM-tag: internal blog links, assets, RSS, canonical/OG URLs, JSON-LD
(Organization `url` stays bare `ORG_URL`). Destination base URLs are
`CTA_URL` / `ORG_URL` in `config.py`. To retarget, change the base URL once;
UTMs are appended at build time.

### PostHog: no product-side config needed

The blog only emits tagged links. Collection happens on **iamstarchild.com**
(the destination), not on the static blog.

PostHog's web SDK **auto-captures all 5 standard UTMs**, including
`utm_content`. Do **not** add `custom_campaign_params` for these; that option
is only for non-standard query keys.

Captured as:

| Place | Property examples |
|---|---|
| Event properties | `utm_source`, `utm_medium`, `utm_content` on the landing session's pageviews |
| Person properties | `$initial_utm_content`, latest `utm_content` |
| Session properties | `$entry_utm_content` / `$session_entry_utm_content` |

Reporting (after real traffic with the new links):

1. Confirm capture: open a session that came from a blog article CTA; check
   event properties for `utm_content=<slug>`.
2. Trends / funnel on the conversion event (signup, agent create, etc.).
3. Breakdown by `utm_content` (or person `$initial_utm_content` for first-touch).
4. Filter `utm_source = blog` and/or `utm_medium = article_cta`.

Caveats:

- Properties only appear in the PostHog UI after **at least one event** has
  that value. Until someone clicks a tagged CTA, `utm_content` won't show in
  the filter picker.
- Attribution sticks to the **landing session**. Later return visits without
  UTMs won't re-attach `utm_content` unless you use person `$initial_utm_*`
  or a funnel that starts from the entry session.
- PostHog must be installed on **iamstarchild.com**. Installing it only on
  the blog does nothing for conversion attribution.
- Draft URLs also get `utm_content=<slug>` (same as published); fine for
  testing.

## GOLDEN RULES — read before touching anything

1. **Protected slug `1892-starchild-blog`** (https://community.iamstarchild.com/1892-starchild-blog/).
   Tech bound a custom domain to it. NEVER unpublish / stop / overwrite /
   reassign it. Same protection class as `1892-docs`. Publishing a rebuild to
   this slug is fine; anything that could drop or repoint it is forbidden.
2. **Edit `content/posts/*.md`, never `public/`.** `public/` is wiped and
   regenerated on every build.
3. **Every article MUST have a hero image** (`hero_image` frontmatter). No
   exceptions — see step 4.
4. **No AI-isms in prose.** No em dashes (`—`), no horizontal dividers. See
   step 6 and the `content-writing` skill.
5. **Never invent numbers.** When importing, keep every figure, benchmark,
   date, and model name exactly as the source.

## Two previews (both auto-start)

| Preview id | Serves | Port | Use |
|---|---|---|---|
| `1892-starchild-blog-poc` | `public/` (full site) | 9081 | Final review, homepage/feed check, publish source |
| `1892-starchild-blog-drafts` | `public/drafts/` | 9086 | Sharing drafts (root = index of all drafts) |

Draft URL for the user (web Preview panel or browser):
`/preview/1892-starchild-blog-drafts/<slug>/`
Full-site URL: `/preview/1892-starchild-blog-poc/`

---

# LIFECYCLE

## 1. Create a draft

### A. Import an existing article (community / X / any HTML page)
The importer fetches the page, scopes all its CSS under `.sr-article` (so page
styles can't leak into the blog shell), neutralizes page-level chrome
(background/margins → blog white bg + Google Sans typography), drops the source
`<h1>` (template renders the title), vendors any Chart.js CDN reference, decodes
UTF-8 correctly, and writes a `draft: true` markdown file.

```bash
cd output/projects/starchild-blog
python3 scripts/import_article.py "<URL>" \
  --date 2026-07-01 \
  --slug my-slug \
  --title "Human-readable title" \
  --author "Starchild Research" \
  --tags research,benchmarks \
  --description "≤160 char summary."
python3 build.py
```
`--slug` is optional (auto-derived from title) but ALWAYS pass it explicitly for
imports so the URL is stable and predictable. Omit `--publish` to keep it a
draft (default).

### B. Hand-write a new post
Create `content/posts/YYYY-MM-DD-<slug>.md` with the frontmatter in step 2, then
`python3 build.py`. Body is Markdown; raw HTML is allowed (used for figures,
callouts, tables).

## 2. Frontmatter reference

```yaml
---
title: "Human title (quote if it contains : or #)"
slug: my-slug                      # lowercase, hyphens; = URL path
date: 2026-07-01                   # YYYY-MM-DD
author: Starchild Research         # or "Starchild Team"
description: One sentence ≤160 chars. Drives <meta description> + OG.
tags: [research, benchmarks]       # lowercase; each becomes /tags/<tag>/
draft: true                        # true = /drafts/ only; false = live
hero_image: assets/images/x.png    # MANDATORY. Banner + og:image source.
og_image: assets/images/x.png      # set = hero (recommended). Omit = auto card.
source_url: https://…              # provenance (optional but keep for imports)
---
```

Rules:
- `description` **must be ≤160 chars** or it hurts SEO snippets. Keep it real,
  no hype.
- `title`: put quotes around it whenever it contains `:`, `#`, or a leading
  special char (YAML will otherwise break).
- Set BOTH `hero_image` and `og_image` to the same file so the on-page banner
  and the social card match.

## 3. Formatting imported / rich articles

The importer produces a self-contained body block:
`<style> … scoped .sr-article … </style>` + `<div class="sr-article"> … </div>`
+ vendored `<script src="__ASSETS__/vendor/chart.umd.min.js">` + chart data.

- **CSS scoping:** every source selector is prefixed with `.sr-article`;
  `html/body/:root` collapse to the container. Page background and margins are
  forced transparent/0 so the article inherits the blog's white background.
- **Typography normalization:** headings, labels, metadata, table headers, and
  section numbers are reset to Google Sans and blog weights/sizes so imported
  pages match the rest of the blog. Layout and data-viz styling (stat cards,
  chart boxes, callouts, table highlights) are preserved.
- **Charts:** the `__ASSETS__` token is resolved by `build.py` per render
  context (`../assets` for drafts, `../../assets` for posts, absolute for feed).
  Chart.js is served locally — never reintroduce a CDN `<script src>`.
- **Encoding:** the importer forces UTF-8 (`apparent_encoding`) so `★ × ≠ –`
  render correctly. If you ever see `â˜…`-style mojibake, the source was
  re-fetched without this — re-run the importer.
- Keep legitimate technical notation: `3–9×` (en dash range), `α`, `≠`, `×`,
  figure labels. Only **em dashes** are AI-isms to remove.
- **Strip imported page chrome that the blog template already owns.** Remove
  in-body kickers like `Author · Topic · Month D, YYYY` (`.kicker` with author /
  date / category). The post template renders date (and hides author in UI on
  purpose). Keep the deck (`.sub`) and a short suite/meta line if they add
  content the template does not. Do not re-print author, date, or site name
  inside the article body.

### Callouts (standard formatting)

Use for a short interpretive note that sits outside the main paragraph flow
(rank caveats, methodology notes, non-obvious chart takeaways). Do not use for
ordinary body copy or chart axis explanations (those belong in `.lede` or
`.fig-sub`).

Markup:

```html
<div class="callout"><b>Lead phrase.</b> Rest of the note in one short paragraph.</div>
<!-- stronger border only when the note is a hard constraint / rule set -->
<div class="callout emphasis"><b>Fair-comparison rules.</b> …</div>
```

CSS tokens (must match brand, not the source page's cream palette):

| Token | Value | Source |
|---|---|---|
| page / paper bg | `#FFFFFF` | brand `background` |
| ink | `#151515` | brand `text` |
| callout fill | `#FFF0DB` | brand `orange.50` |
| default border | `#FFA940` | brand `orange.100` |
| emphasis border | `#F84600` | brand `primary` |
| body text in callout | `#646464` (`--muted`) | blog body secondary |
| bold lead | `#151515`, weight 700 | brand ink |

Shape: 3px left border, `0 12px 12px 0` radius, `14px 18px` padding, `14.5px` /
`1.55` line-height, `max-width: 68ch`. Lead phrase is plain `<b>` (no emoji, no
ALL-CAPS label chip). One callout = one idea. Prefer default; use `.emphasis`
only for methodology/rules that the reader must not miss.

Do **not**: full-width colored boxes, green/blue accent colors, icon bullets,
`blockquote`, or horizontal rules as callout substitutes.

## 4. Hero images — MANDATORY

Every article ships with a hero banner. It renders full-width above the title
(`.post-hero` in `style.css`) and doubles as the social card.

1. Save the image to `assets/images/<slug>-hero.png` (user upload lands in
   `workspace/uploads/…` — copy it over; also check `/data/workspace/uploads/`).
2. Add to frontmatter:
   ```yaml
   hero_image: assets/images/<slug>-hero.png
   og_image: assets/images/<slug>-hero.png
   ```
3. `python3 build.py` and verify `class="post-hero"` + the filename appear in
   the built page.

If the user supplies no image, ask for one or generate a brand-consistent
banner (`image-create`, white bg / #111 ink / #F84600 orange). Do not publish
without a hero.

## 5. SEO structures (built automatically — verify, don't hand-write)

`build.py` emits, per post: `<title>`, `<meta description>`, canonical URL,
Open Graph (`og:title/description/image/url/type=article`), `article:published_time`
+ `article:tag`, and JSON-LD `Article` + `Organization`. Site-wide it emits
`feed.xml` (RSS), `sitemap.xml`, `robots.txt` (disallows `/drafts/`),
`api/posts.json`, and per-tag pages.

Canonical/OG absolute URLs derive from `config.py:SITE_URL`
(`https://community.iamstarchild.com/1892-starchild-blog`). Don't hardcode URLs
in posts — keep links relative; the builder absolutizes what it needs.

Your SEO checklist per article: real ≤160-char `description`, `hero_image` set
(→ og:image), sensible lowercase `tags`, stable `slug`. Drafts carry
`noindex` and are excluded from feed/sitemap/API automatically.

## 6. Editorial / AI-ism pass (before publishing)

Load the `content-writing` skill for voice. Then scrub:
- **Remove all em dashes** (`—`). Replace with commas, colons, parentheses, or
  restructure. Keep en-dash numeric ranges (`3–6×`).
- No horizontal dividers (`---`) between sections; let headings separate.
- Replace canned transitions ("The mechanism is simple", "That's exactly what
  X is built to measure"), formulaic contrast ("X is not Y, it's Z"), and vague
  section headings ("The picture" → "Accuracy versus cost").
- Prefer flowing sentences over choppy fragments; active voice; no hype words
  (revolutionary, seamless, game-changing).
- Preserve every number, model name, date, figure, and caveat.

Quick scan:
```bash
grep -n '—' content/posts/<file>.md            # em dashes (should be 0)
grep -n ' - ' content/posts/<file>.md           # stray dividers
```

## 7. Build & preview

```bash
cd output/projects/starchild-blog
python3 build.py --check     # validates all posts render, no errors
python3 build.py             # writes public/ + public/drafts/
```
`build.py` reports `built N post(s), M draft(s), K tag(s)`. Both previews serve
the fresh output immediately (static). Verify:
```bash
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:9086/<slug>/   # draft
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:9081/          # site
```
Give the user the draft link: `/preview/1892-starchild-blog-drafts/<slug>/`.

If a preview isn't running (port pool full / after restart), re-serve:
```
preview(action="serve", title="Starchild Blog Drafts",
        dir="output/projects/starchild-blog/public/drafts")
```

## 8. Publishing & permissions

Publishing = flip the post live, rebuild, then republish the full-site preview
to the protected slug via the `community-publish` skill.

1. Get user sign-off on the draft.
2. Set `draft: false` in the post frontmatter (confirm hero_image + description
   are set first).
3. Rebuild: `python3 build.py`.
4. Ensure the full-site preview is running (`1892-starchild-blog-poc`, port
   9081). Re-serve if needed with `dir=output/projects/starchild-blog/public`.
5. Publish to the SAME protected slug (never a new one):
   ```
   from exports import publish_preview      # community-publish skill
   publish_preview(preview_id="1892-starchild-blog-poc",
                   slug="starchild-blog",
                   title="The Starchild Blog")
   ```
   The gateway maps `starchild-blog` → `1892-starchild-blog` (user_id prefix is
   added automatically). This refreshes the existing live site in place; it does
   NOT create or repoint the domain binding.
6. Verify live: `https://community.iamstarchild.com/1892-starchild-blog/` returns
   200 and the new post appears on the homepage/feed.

**Permissions model:**
- `publish_preview` → anyone with the URL can visit (the blog is public).
- The custom domain binding is managed by the tech team, not this skill. Treat
  it as permanent infrastructure.
- Drafts are `noindex` + robots-disallowed + absent from feed/sitemap/API, so a
  draft URL is shareable for review without being indexed. It is not access-
  controlled — don't put anything truly private in a draft.
- The community-publish skill is the ONLY sanctioned path to publish. Never
  hand-curl the services API or push to the slug by other means.

---

## Troubleshooting

- **Draft preview 404 / won't load in panel:** deep nested links can fail in the
  Preview panel. Use the drafts preview (`1892-starchild-blog-drafts`) whose root
  is `public/drafts/` — the article sits one level down at `/<slug>/`, and the
  root is an index of all drafts.
- **Charts blank:** a CDN `<script src>` slipped back in, or `__ASSETS__` wasn't
  resolved. Confirm the built page references `vendor/chart.umd.min.js` and has
  no `cdn.jsdelivr` reference.
- **Wrong background / fonts on an imported article:** re-run the importer (it
  now forces white bg + Google Sans). Don't patch `public/` by hand.
- **Mojibake (`â˜…`):** re-run the importer; it decodes UTF-8 via
  `apparent_encoding`.
- **"No available ports in pool":** stop an old/unused preview
  (`preview(action="stop", preview_id=…)`) then re-serve. Never stop the two
  blog previews or any protected slug.
- **YAML parse error on build:** usually an unquoted `title` containing `:` or
  `#`. Wrap the title in double quotes.
- **Telegram / X link preview shows no image despite `og:image` being set:**
  header image was saved as RGBA PNG. Telegram's crawler silently rejects
  alpha-channel PNGs and falls back to no preview at all. Fix before rebuilding:
  `Image.open(path).convert('RGB').save(path, format='PNG')`. Verify the saved
  file is color type 2: `struct.unpack('B', open(path,'rb').read()[25:26])[0] == 2`.
- **Draft 404 on homepage in --drafts mode:** fixed in build.py — drafts are
  now rendered to both `posts/<slug>/` and `drafts/<slug>/` in drafts mode so
  homepage and tag page links resolve.

## Quick reference

```bash
cd output/projects/starchild-blog

# Import → draft
python3 scripts/import_article.py "<URL>" --date YYYY-MM-DD --slug S \
  --title "T" --author "Starchild Research" --tags a,b --description "…"

# Build
python3 build.py --check && python3 build.py

# Preview links
# draft: /preview/1892-starchild-blog-drafts/<slug>/
# site:  /preview/1892-starchild-blog-poc/

# Publish (after draft:false + rebuild), via community-publish skill:
#   publish_preview(preview_id="1892-starchild-blog-poc",
#                   slug="starchild-blog", title="The Starchild Blog")
```
