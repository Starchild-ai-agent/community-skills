#!/usr/bin/env python3
"""Build HTML mythbook for zodiac past-life myth outputs.

Usage:
  python3 build_mythbook.py <myth.json> <out.html>

JSON schema:
{
  "title": "天蝎座前世神话",
  "subtitle": "献给 ...",
  "hero": "名字或称呼",
  "zodiac": "天蝎座",
  "birth_date": "1995-11-02",
  "keywords": ["冷静", "执拗", "温柔"],
  "story_html": "<p>...</p><p>...</p>",
  "poem_lines": ["...", "...", "...", "..."],
  "image": {
    "src": "illustration.png",
    "caption": "前世神话形象"
  },
  "closing": "愿你..."
}
"""
from __future__ import annotations

import html
import json
import sys
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "mythbook_template.html"


def esc(s: str) -> str:
    return html.escape(s or "")


def main() -> None:
    if len(sys.argv) != 3:
        print("Usage: build_mythbook.py <myth.json> <out.html>", file=sys.stderr)
        sys.exit(2)

    in_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2])

    data = json.loads(in_path.read_text(encoding="utf-8"))

    title = data.get("title") or "星座前世神话"
    subtitle = data.get("subtitle") or ""
    hero = data.get("hero") or ""
    zodiac = data.get("zodiac") or ""
    birth_date = data.get("birth_date") or ""
    keywords = data.get("keywords") or []
    story_html = data.get("story_html") or ""
    poem_lines = data.get("poem_lines") or []
    image = data.get("image") or {}
    closing = data.get("closing") or ""

    keywords_html = " · ".join(esc(str(k)) for k in keywords[:3])
    poem_html = "\n".join(f"<p>{esc(str(line))}</p>" for line in poem_lines)

    img_src = esc(image.get("src", ""))
    img_cap = esc(image.get("caption", ""))
    img_block = ""
    if img_src:
        cap = f"<figcaption>{img_cap}</figcaption>" if img_cap else ""
        img_block = (
            '<figure class="illus">'
            f'<img src="{img_src}" alt="{img_cap}" loading="lazy">'
            f'{cap}'
            '</figure>'
        )

    subtitle_block = f'<p class="subtitle">{esc(subtitle)}</p>' if subtitle else ""
    meta_block = (
        f"<p class=\"meta\">{esc(hero)}　|　{esc(zodiac)}　|　{esc(birth_date)}"
        + (f"　|　{keywords_html}" if keywords_html else "")
        + "</p>"
    )
    closing_block = f'<p class="closing">{esc(closing)}</p>' if closing else ""

    tpl = TEMPLATE.read_text(encoding="utf-8")
    out_html = (
        tpl.replace("{{TITLE}}", esc(title))
        .replace("{{SUBTITLE_BLOCK}}", subtitle_block)
        .replace("{{META_BLOCK}}", meta_block)
        .replace("{{IMAGE_BLOCK}}", img_block)
        .replace("{{STORY_HTML}}", story_html)
        .replace("{{POEM_HTML}}", poem_html)
        .replace("{{CLOSING_BLOCK}}", closing_block)
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(out_html, encoding="utf-8")
    print(f"Mythbook written: {out_path}")


if __name__ == "__main__":
    main()
