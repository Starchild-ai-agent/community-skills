#!/usr/bin/env python3
"""Build a polished HTML storybook for the "If I Had Never Been Born" tale.

Usage:
    python3 build_storybook.py <story.json> <out.html>

story.json schema:
{
  "title":    "如果你从未出生",          # story title
  "subtitle": "送给 {name} 的平行宇宙童话",  # optional subtitle
  "hero":     "小满",                    # name
  "age":      "8",                       # optional, string or int
  "language": "zh",                      # "zh" or "en" (affects font + footer text)
  "sections": [                          # ordered story blocks
    {"type": "text",  "html": "<p>...</p><p>...</p>"},
    {"type": "image", "src": "vignette1.png", "caption": "..."},
    {"type": "text",  "html": "<p>...</p>"},
    {"type": "image", "src": "vignette2.png", "caption": "..."},
    ...
  ],
  "dedication": "愿你永远记得，你来过，世界因此不同。"  # optional closing line
}

Notes:
- "src" should be a path RELATIVE to the output HTML (put images in the same folder).
- Text "html" may contain <p>, <em>, <strong>, <br>. Keep it simple.
- The script does no LLM work — the agent writes the story, this just renders it.
"""
import json
import sys
import html as _html
from pathlib import Path

TEMPLATE_PATH = Path(__file__).resolve().parent.parent / "assets" / "storybook_template.html"


def esc(s: str) -> str:
    return _html.escape(s or "")


def render_sections(sections):
    out = []
    for sec in sections:
        t = sec.get("type")
        if t == "text":
            out.append(f'<div class="story-text">{sec.get("html", "")}</div>')
        elif t == "image":
            cap = sec.get("caption", "")
            cap_html = f'<figcaption>{esc(cap)}</figcaption>' if cap else ""
            out.append(
                '<figure class="story-illus">'
                f'<img src="{esc(sec.get("src",""))}" alt="{esc(cap)}" loading="lazy">'
                f'{cap_html}</figure>'
            )
        else:
            # unknown block, skip safely
            continue
    return "\n".join(out)


def main():
    if len(sys.argv) != 3:
        print("Usage: build_storybook.py <story.json> <out.html>", file=sys.stderr)
        sys.exit(2)

    story_path, out_path = Path(sys.argv[1]), Path(sys.argv[2])
    data = json.loads(story_path.read_text(encoding="utf-8"))

    lang = (data.get("language") or "zh").lower()
    is_zh = lang.startswith("zh")

    title = data.get("title") or ("如果你从未出生" if is_zh else "If You Had Never Been Born")
    subtitle = data.get("subtitle") or ""
    hero = data.get("hero") or ""
    dedication = data.get("dedication") or ""

    body_html = render_sections(data.get("sections", []))

    footer_made = "用 ✨ 为你定制" if is_zh else "Lovingly crafted for you"
    ded_block = (
        f'<div class="dedication"><p>{esc(dedication)}</p></div>' if dedication else ""
    )
    subtitle_block = f'<p class="subtitle">{esc(subtitle)}</p>' if subtitle else ""

    font_stack = (
        '"Noto Serif SC", "Songti SC", "STSong", serif' if is_zh
        else '"Georgia", "Iowan Old Style", "Palatino", serif'
    )

    tpl = TEMPLATE_PATH.read_text(encoding="utf-8")
    out = (
        tpl.replace("{{LANG}}", "zh-CN" if is_zh else "en")
        .replace("{{FONT_STACK}}", font_stack)
        .replace("{{TITLE}}", esc(title))
        .replace("{{SUBTITLE_BLOCK}}", subtitle_block)
        .replace("{{BODY}}", body_html)
        .replace("{{DEDICATION_BLOCK}}", ded_block)
        .replace("{{FOOTER_MADE}}", footer_made)
        .replace("{{HERO}}", esc(hero))
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(out, encoding="utf-8")
    print(f"Storybook written: {out_path}")


if __name__ == "__main__":
    main()
