#!/usr/bin/env python3
"""
Web Crawler — Playwright-based site crawler with screenshots and interaction.

Usage:
    python3 skills/web-crawler/scripts/crawl.py <url> [options]

Options:
    --output-dir DIR       Output directory (default: output/crawl-{domain})
    --screenshot           Take screenshot of each page (default: on)
    --no-screenshot        Disable screenshots
    --full-page            Full-page screenshots (default: viewport only)
    --click SELECTOR       Click an element and screenshot the result
    --click-all SELECTOR   Click all matching elements sequentially
    --extract-links        Extract and report all links
    --extract-text         Extract visible text content
    --console-log          Capture browser console messages
    --wait SEC             Wait seconds after load (default: 2)
    --viewport WxH         Viewport size (default: 1440x900)
    --timeout SEC          Navigation timeout (default: 30)
    --user-agent STR       Custom user agent
    --cookie NAME=VALUE    Set cookie before navigation
    --audit                Run full UX audit (screenshots + links + text + console + clickables)
    --max-pages N          Max pages to crawl in audit mode (default: 20)

Output:
    {output-dir}/
    ├── screenshots/       PNG screenshots
    ├── pages/             Extracted text per page
    ├── report.json        Structured crawl report
    └── audit.md           Human-readable audit (if --audit)
"""

import argparse
import json
import os
import re
import sys
import time
from urllib.parse import urljoin, urlparse
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout


def slugify(url):
    parsed = urlparse(url)
    path = parsed.path.strip("/").replace("/", "_") or "index"
    return re.sub(r'[^a-zA-Z0-9_-]', '_', path)[:80]


def extract_clickables(page):
    """Extract all interactive elements."""
    return page.evaluate("""() => {
        const els = document.querySelectorAll('a, button, [role="button"], input[type="submit"], [onclick]');
        return Array.from(els).map(el => ({
            tag: el.tagName.toLowerCase(),
            text: (el.textContent || '').trim().substring(0, 100),
            href: el.href || null,
            type: el.type || null,
            role: el.getAttribute('role'),
            ariaLabel: el.getAttribute('aria-label'),
            visible: el.offsetParent !== null,
            rect: el.getBoundingClientRect().toJSON()
        })).filter(e => e.visible);
    }""")


def extract_links(page):
    """Extract all links."""
    return page.evaluate("""() => {
        return Array.from(document.querySelectorAll('a[href]')).map(a => ({
            text: (a.textContent || '').trim().substring(0, 100),
            href: a.href,
            internal: a.href.startsWith(window.location.origin)
        }));
    }""")


def extract_text(page):
    """Extract visible text."""
    return page.evaluate("""() => {
        const walker = document.createTreeWalker(
            document.body, NodeFilter.SHOW_TEXT, null, false
        );
        const texts = [];
        while (walker.nextNode()) {
            const text = walker.currentNode.textContent.trim();
            if (text.length > 1) texts.push(text);
        }
        return texts.join('\\n');
    }""")


def extract_meta(page):
    """Extract page metadata."""
    return page.evaluate("""() => {
        const getMeta = (name) => {
            const el = document.querySelector(`meta[name="${name}"], meta[property="${name}"]`);
            return el ? el.content : null;
        };
        return {
            title: document.title,
            description: getMeta('description') || getMeta('og:description'),
            ogImage: getMeta('og:image'),
            viewport: getMeta('viewport'),
            robots: getMeta('robots'),
            canonical: (() => { const el = document.querySelector('link[rel="canonical"]'); return el ? el.href : null; })()
        };
    }""")


def check_accessibility(page):
    """Basic accessibility checks."""
    return page.evaluate("""() => {
        const issues = [];
        // Images without alt
        document.querySelectorAll('img').forEach(img => {
            if (!img.alt) issues.push({type: 'missing-alt', src: img.src?.substring(0, 100)});
        });
        // Buttons without accessible name
        document.querySelectorAll('button').forEach(btn => {
            if (!btn.textContent?.trim() && !btn.getAttribute('aria-label'))
                issues.push({type: 'unlabeled-button', html: btn.outerHTML.substring(0, 100)});
        });
        // Missing lang attribute
        if (!document.documentElement.lang)
            issues.push({type: 'missing-lang'});
        // Missing h1
        if (!document.querySelector('h1'))
            issues.push({type: 'missing-h1'});
        // Color contrast (basic — check for very light text)
        const headings = document.querySelectorAll('h1,h2,h3,p');
        headings.forEach(el => {
            const style = getComputedStyle(el);
            const color = style.color;
            if (color === 'rgba(0, 0, 0, 0)' || color === 'transparent')
                issues.push({type: 'invisible-text', tag: el.tagName, text: el.textContent?.substring(0, 50)});
        });
        return issues;
    }""")


def crawl_page(page, url, args, console_messages):
    """Crawl a single page, return page data."""
    result = {"url": url, "status": None, "error": None}

    try:
        response = page.goto(url, timeout=args.timeout * 1000, wait_until="networkidle")
        result["status"] = response.status if response else None
        time.sleep(args.wait)
    except PWTimeout:
        # Try with domcontentloaded instead
        try:
            response = page.goto(url, timeout=args.timeout * 1000, wait_until="domcontentloaded")
            result["status"] = response.status if response else None
            time.sleep(args.wait)
        except Exception as e:
            result["error"] = str(e)
            return result
    except Exception as e:
        result["error"] = str(e)
        return result

    result["meta"] = extract_meta(page)
    result["final_url"] = page.url

    if args.screenshot or args.audit:
        slug = slugify(url)
        ss_path = os.path.join(args.output_dir, "screenshots", f"{slug}.png")
        page.screenshot(path=ss_path, full_page=args.full_page)
        result["screenshot"] = ss_path

    if args.extract_links or args.audit:
        result["links"] = extract_links(page)

    if args.extract_text or args.audit:
        text = extract_text(page)
        text_path = os.path.join(args.output_dir, "pages", f"{slugify(url)}.txt")
        with open(text_path, "w") as f:
            f.write(text)
        result["text_file"] = text_path
        result["text_length"] = len(text)

    if args.audit:
        result["clickables"] = extract_clickables(page)
        result["accessibility"] = check_accessibility(page)

    if args.console_log or args.audit:
        result["console"] = [m for m in console_messages]
        console_messages.clear()

    return result


def run_audit(page, start_url, args, console_messages):
    """Full site audit: crawl internal pages breadth-first."""
    visited = set()
    queue = [start_url]
    results = []
    domain = urlparse(start_url).netloc

    while queue and len(visited) < args.max_pages:
        url = queue.pop(0)
        normalized = url.split("#")[0].rstrip("/")
        if normalized in visited:
            continue
        visited.add(normalized)

        print(f"  [{len(visited)}/{args.max_pages}] {url}", flush=True)
        result = crawl_page(page, url, args, console_messages)
        results.append(result)

        # Queue internal links
        for link in result.get("links", []):
            href = link["href"].split("#")[0].rstrip("/")
            parsed = urlparse(href)
            if parsed.netloc == domain and href not in visited and href not in queue:
                queue.append(href)

    return results


def generate_audit_md(results, output_dir):
    """Generate human-readable audit report."""
    lines = ["# UX Audit Report\n"]
    lines.append(f"**Pages crawled:** {len(results)}\n")

    # Summary stats
    total_links = sum(len(r.get("links", [])) for r in results)
    total_issues = sum(len(r.get("accessibility", [])) for r in results)
    total_console_errors = sum(1 for r in results for c in r.get("console", []) if c.get("type") == "error")
    broken = [r for r in results if r.get("status") and r["status"] >= 400]

    lines.append(f"**Total links found:** {total_links}")
    lines.append(f"**Accessibility issues:** {total_issues}")
    lines.append(f"**Console errors:** {total_console_errors}")
    lines.append(f"**Broken pages (4xx/5xx):** {len(broken)}\n")

    if broken:
        lines.append("## ❌ Broken Pages\n")
        for r in broken:
            lines.append(f"- **{r['status']}** — {r['url']}")

    # Per-page details
    lines.append("\n## Pages\n")
    for r in results:
        status_emoji = "✅" if r.get("status", 0) == 200 else "⚠️" if r.get("status") else "❌"
        lines.append(f"### {status_emoji} {r.get('meta', {}).get('title', r['url'])}\n")
        lines.append(f"- **URL:** {r['url']}")
        lines.append(f"- **Status:** {r.get('status', 'error')}")
        if r.get("screenshot"):
            lines.append(f"- **Screenshot:** `{os.path.basename(r['screenshot'])}`")

        clickables = r.get("clickables", [])
        if clickables:
            buttons = [c for c in clickables if c["tag"] in ("button",) or c.get("role") == "button"]
            nav_links = [c for c in clickables if c["tag"] == "a"]
            lines.append(f"- **Buttons:** {len(buttons)} | **Links:** {len(nav_links)}")

        issues = r.get("accessibility", [])
        if issues:
            lines.append(f"- **Accessibility issues:**")
            for iss in issues[:10]:
                lines.append(f"  - `{iss['type']}` {iss.get('src', iss.get('text', ''))}")

        console_errs = [c for c in r.get("console", []) if c.get("type") == "error"]
        if console_errs:
            lines.append(f"- **Console errors:**")
            for ce in console_errs[:5]:
                lines.append(f"  - `{ce.get('text', '')[:150]}`")

        lines.append("")

    md = "\n".join(lines)
    path = os.path.join(output_dir, "audit.md")
    with open(path, "w") as f:
        f.write(md)
    return path


def main():
    parser = argparse.ArgumentParser(description="Playwright web crawler")
    parser.add_argument("url", help="URL to crawl")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--screenshot", action="store_true", default=True)
    parser.add_argument("--no-screenshot", action="store_true")
    parser.add_argument("--full-page", action="store_true")
    parser.add_argument("--click", default=None)
    parser.add_argument("--click-all", default=None)
    parser.add_argument("--extract-links", action="store_true")
    parser.add_argument("--extract-text", action="store_true")
    parser.add_argument("--console-log", action="store_true")
    parser.add_argument("--wait", type=float, default=2)
    parser.add_argument("--viewport", default="1440x900")
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--user-agent", default=None)
    parser.add_argument("--audit", action="store_true")
    parser.add_argument("--max-pages", type=int, default=20)
    args = parser.parse_args()

    if args.no_screenshot:
        args.screenshot = False

    # Parse viewport
    vw, vh = map(int, args.viewport.split("x"))

    # Output dir
    if not args.output_dir:
        domain = urlparse(args.url).netloc.replace(".", "-")
        args.output_dir = f"output/crawl-{domain}"

    os.makedirs(os.path.join(args.output_dir, "screenshots"), exist_ok=True)
    os.makedirs(os.path.join(args.output_dir, "pages"), exist_ok=True)

    console_messages = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": vw, "height": vh},
            user_agent=args.user_agent or "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # Console capture
        page.on("console", lambda msg: console_messages.append({
            "type": msg.type, "text": msg.text[:500]
        }))

        if args.audit:
            print(f"Starting full audit of {args.url} (max {args.max_pages} pages)...")
            results = run_audit(page, args.url, args, console_messages)
            audit_path = generate_audit_md(results, args.output_dir)
            report = {"mode": "audit", "url": args.url, "pages_crawled": len(results), "results": results}
            print(f"\nAudit complete: {len(results)} pages crawled")
            print(f"Audit report: {audit_path}")
        else:
            result = crawl_page(page, args.url, args, console_messages)
            report = {"mode": "single", "url": args.url, "result": result}

            # Handle click
            if args.click:
                try:
                    page.click(args.click, timeout=5000)
                    time.sleep(args.wait)
                    ss_path = os.path.join(args.output_dir, "screenshots", "after-click.png")
                    page.screenshot(path=ss_path, full_page=args.full_page)
                    report["click"] = {"selector": args.click, "screenshot": ss_path}
                    print(f"Clicked '{args.click}' — screenshot saved")
                except Exception as e:
                    report["click"] = {"selector": args.click, "error": str(e)}

            if args.click_all:
                try:
                    elements = page.query_selector_all(args.click_all)
                    report["click_all"] = []
                    for i, el in enumerate(elements[:20]):
                        try:
                            el.click(timeout=3000)
                            time.sleep(args.wait)
                            ss_path = os.path.join(args.output_dir, "screenshots", f"click-{i}.png")
                            page.screenshot(path=ss_path, full_page=args.full_page)
                            report["click_all"].append({"index": i, "screenshot": ss_path})
                        except:
                            pass
                except Exception as e:
                    report["click_all"] = {"error": str(e)}

            print(f"Crawled: {result.get('meta', {}).get('title', 'N/A')} [{result.get('status')}]")

        # Save report
        report_path = os.path.join(args.output_dir, "report.json")
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2, default=str)
        print(f"Report: {report_path}")

        browser.close()


if __name__ == "__main__":
    main()
