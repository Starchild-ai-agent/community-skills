"""
Starchild Instagram Composition Layer
Applies brand assets onto a Fal.ai generated image.

Usage:
    python skills/fal-image/scripts/compose_instagram.py \
        --input path/to/image.jpg --output path/to/out.jpg \
        --headline "Title" --subtext "Subtitle" --tag "NEW FEATURE"
"""
import argparse, os, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

ORANGE = (248, 70, 0)
WHITE  = (255, 255, 255)
GREY   = (180, 180, 180)

WORKSPACE    = Path(__file__).resolve().parents[3]
ASSETS_DIR   = WORKSPACE / "Brand assets"
WORDMARK_PNG = ASSETS_DIR / "Wordmark" / "PNG" / "Wordmark_White.png"

def _font(size, bold=False):
    candidates = [
        f"/usr/share/fonts/truetype/dejavu/DejaVuSans{'-Bold' if bold else ''}.ttf",
        f"/usr/share/fonts/truetype/liberation/LiberationSans-{'Bold' if bold else 'Regular'}.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except: pass
    return ImageFont.load_default()

def _wordmark(px=40):
    for candidate in [WORDMARK_PNG]:
        if candidate.exists():
            img = Image.open(candidate).convert("RGBA")
            r = px / img.height
            return img.resize((int(img.width * r), px), Image.LANCZOS)
    return None

def compose(image, headline="", subtext="", tag="", accent_bar=True, watermark=True):
    """Apply Starchild brand overlay to a PIL Image. Returns RGB Image."""
    T = 1080
    img = image.copy().convert("RGBA")
    if img.size != (T, T):
        img = img.resize((T, T), Image.LANCZOS)
    draw = ImageDraw.Draw(img)

    if accent_bar:
        draw.rectangle([(0, 0), (T, 6)], fill=ORANGE)

    if headline or subtext or tag:
        gh = 380
        grad = Image.new("RGBA", (T, gh), (0, 0, 0, 0))
        gd = ImageDraw.Draw(grad)
        for i in range(gh):
            gd.line([(0, i), (T, i)], fill=(0, 0, 0, int(210 * i / gh)))
        img.paste(grad, (0, T - gh), grad)
        draw = ImageDraw.Draw(img)

    x, by = 72, T - 80
    if tag:
        tf = _font(28, bold=True)
        draw.text((x, by - 180), tag.upper(), font=tf, fill=ORANGE)
        tw = draw.textlength(tag.upper(), font=tf)
        draw.line([(x, by - 148), (x + tw, by - 148)], fill=ORANGE, width=2)

    if headline:
        hf = _font(72, bold=True)
        words = headline.split()
        lines, cur = [], []
        for w in words:
            cur.append(w)
            if len(" ".join(cur)) > 18:
                lines.append(" ".join(cur[:-1])); cur = [w]
        if cur: lines.append(" ".join(cur))
        yo = (by - 140) if tag else (by - 80)
        for line in lines[:3]:
            draw.text((x, yo), line, font=hf, fill=WHITE); yo += 84

    if subtext:
        draw.text((x, by - 10), subtext, font=_font(34), fill=GREY)

    if watermark:
        wm = _wordmark(40)
        if wm:
            img.paste(wm, (28, 34 if accent_bar else 28), wm)

    return img.convert("RGB")

def generate_and_compose(prompt, output_path, model="fal-ai/flux-pro/v1.1-ultra",
                         headline="", subtext="", tag="", image_size="square_hd"):
    """Full pipeline: Fal.ai generate → brand compose → save. Returns output_path."""
    import fal_client
    os.environ["FAL_KEY"] = os.environ.get("FAL_API_KEY", os.environ.get("FAL_KEY", ""))
    print(f"Generating with {model}...")
    result = fal_client.run(model, arguments={
        "prompt": prompt, "image_size": image_size,
        "num_images": 1, "output_format": "jpeg", "safety_tolerance": "5"
    })
    url = result["images"][0]["url"]
    print(f"URL: {url}")
    raw_bytes = requests.get(url).content
    raw = Image.open(BytesIO(raw_bytes)).convert("RGBA")
    composed = compose(raw, headline=headline, subtext=subtext, tag=tag)
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    composed.save(output_path, "JPEG", quality=95)
    print(f"Saved: {output_path}")
    return output_path

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--input"); p.add_argument("--output", required=True)
    p.add_argument("--prompt"); p.add_argument("--model", default="fal-ai/flux-pro/v1.1-ultra")
    p.add_argument("--headline", default=""); p.add_argument("--subtext", default="")
    p.add_argument("--tag", default="")
    a = p.parse_args()
    if a.prompt:
        generate_and_compose(a.prompt, a.output, a.model, a.headline, a.subtext, a.tag)
    elif a.input:
        src = requests.get(a.input).content if a.input.startswith("http") else open(a.input,"rb").read()
        img = Image.open(BytesIO(src)).convert("RGBA")
        compose(img, a.headline, a.subtext, a.tag).save(a.output, "JPEG", quality=95)
        print(f"Saved: {a.output}")
    else:
        print("Provide --input or --prompt"); sys.exit(1)
