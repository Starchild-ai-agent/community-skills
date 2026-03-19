---
name: "@1247/web-crawler"
version: 1.0.0
description: "Headless browser for web crawling, UX audits, screenshots, and interaction testing. Use when the user wants to audit a website, take screenshots, click buttons, test UX flows, extract content from SPAs, or crawl pages that require JavaScript rendering."

metadata:
  starchild:
    emoji: "🕷️"
    skillKey: web-crawler
    requires:
      bins: [python3]
    install:
      - kind: pip
        package: playwright
      - kind: shell
        command: "playwright install chromium && playwright install-deps chromium"

user-invocable: true
---

# Web Crawler

Playwright-based headless browser for crawling JavaScript-heavy sites, taking screenshots, clicking buttons, and running UX audits. Works on SPAs, auth-walled pages, and anything that needs a real browser.

## Quick Reference

### Single page screenshot
```bash
python3 skills/web-crawler/scripts/crawl.py https://example.com
```

### Full UX audit (crawls all internal pages)
```bash
python3 skills/web-crawler/scripts/crawl.py https://example.com --audit --max-pages 30
```

### Click a button and screenshot result
```bash
python3 skills/web-crawler/scripts/crawl.py https://example.com --click "button.cta"
```

### Click all nav links sequentially
```bash
python3 skills/web-crawler/scripts/crawl.py https://example.com --click-all "nav a"
```

### Extract all text (good for SPAs)
```bash
python3 skills/web-crawler/scripts/crawl.py https://example.com --extract-text
```

## Output Structure

```
output/crawl-{domain}/
├── screenshots/     # PNG screenshots per page
├── pages/           # Extracted text per page
├── report.json      # Structured crawl data
└── audit.md         # Readable audit report (--audit mode)
```

## Audit Mode

`--audit` runs a breadth-first crawl of all internal pages:
- Screenshots every page
- Extracts all links (internal + external)
- Captures console errors
- Runs accessibility checks (missing alt, unlabeled buttons, missing h1/lang)
- Maps all clickable elements (buttons, links, interactive elements)
- Generates `audit.md` with findings

## Key Options

| Flag | Default | What it does |
|------|---------|-------------|
| `--audit` | off | Full site audit mode |
| `--max-pages N` | 20 | Max pages to crawl in audit |
| `--full-page` | off | Full-page screenshots vs viewport |
| `--click SEL` | — | Click CSS selector, screenshot result |
| `--click-all SEL` | — | Click all matching elements |
| `--extract-links` | off | Extract all `<a>` hrefs |
| `--extract-text` | off | Extract visible text |
| `--console-log` | off | Capture console messages |
| `--wait SEC` | 2 | Wait after page load |
| `--viewport WxH` | 1440x900 | Browser viewport |
| `--timeout SEC` | 30 | Navigation timeout |

## Workflow for UX Audit

1. Run `--audit` on the target site
2. Read `audit.md` for the summary
3. Check `report.json` for structured data (clickables, links, console errors)
4. Review screenshots in `screenshots/` folder
5. For deeper inspection: re-run single pages with `--click` to test specific interactions
6. Synthesize findings into actionable UX recommendations

## Gotchas

- **SPAs with hash routing**: The crawler follows `<a href>` links. Hash-only routes (`#/page`) won't be auto-discovered in audit mode. Use `--click-all "nav a"` instead.
- **Auth-walled sites**: Not yet supported. Future: add `--cookie` support.
- **Rate limiting**: The crawler hits pages fast. Add `--wait 3` for sensitive sites.
- **Chromium install**: First run needs `playwright install chromium` (~110MB). Persisted in setup.sh.
