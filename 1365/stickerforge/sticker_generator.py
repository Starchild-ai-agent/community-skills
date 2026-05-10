"""AI sticker generation — base creation and emotion variant editing."""

import base64
import re
from io import BytesIO

from PIL import Image

from .http import post as http_post
from .config import OPENROUTER_URL, IMAGE_MODEL


def _pad_for_full_body(image_path: str) -> str:
    """Pad a head-crop PFP with white space below to suggest full-body composition.

    NFT PFPs are always cropped at the chest. By extending the canvas downward,
    the model sees a tall frame with the head at top and empty space below,
    which strongly encourages it to draw the full body into that space.
    Returns a base64 data URL of the padded image.
    """
    img = Image.open(image_path).convert("RGB")
    w, h = img.size
    # Create a canvas 1.4x taller — just enough space for body + feet
    new_h = int(h * 1.4)
    canvas = Image.new("RGB", (w, new_h), (255, 255, 255))
    canvas.paste(img, (0, 0))
    buf = BytesIO()
    canvas.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{b64}"

BASE_PROMPT = """Generate a full-body Pudgy Penguin sticker of this exact character standing upright.

IMPORTANT: The reference image is a head-only portrait crop. You MUST draw the COMPLETE character standing upright from head to feet — including the body, legs, and feet which are NOT in the reference. Do NOT copy the reference framing.

CHARACTER (copy colors and accessories from the reference EXACTLY):
- Body/skin: {skin_color}, flippers: {flipper_color}, belly: {belly_color}
- Eyes: {eye_type}
- Head: {head_accessory}
- Face: {face_accessory}
- Clothing ({clothing_color}): {clothing}
- {overall_description}

BODY PROPORTIONS:
- Round pudgy body — wide and chubby like the reference, NOT narrow or elongated
- Head sits directly on body (no neck), about 1/3 of total height
- Flippers hang at the sides at mid-body height
- Exactly TWO small orange oval feet at the very bottom, tucked under the body

RULES:
- STANDING UPRIGHT — NOT sitting, NOT squatting
- NO tail — Pudgy Penguins do not have tails
- Neutral standing pose, flippers at sides, friendly expression
- Exactly 2 feet — small compact solid orange ovals, NO toes, NO lines, NO detail, NOT oversized
- Flippers: {flipper_color} (body color), NOT {clothing_color} (clothing color)
- Thick uniform black outlines, clean flat colors
- Background: solid pure white (#FFFFFF) — no gradients, shadows, or scenery
- No sticker border or outline frame
- Character centered, filling ~70-80% of the image"""


EDIT_PROMPT = """Edit this Pudgy Penguin sticker image. Make ONLY the changes listed below. Keep everything else exactly as it is.

CHANGES:
{emotion_edit}

MUST PRESERVE — do NOT alter any of these:
- Exact same art style, line weight, and thick black outlines
- Exact same body shape and proportions — vertical oval body, taller than wide
- Exact same colors for body, belly, beak, clothing, and all accessories
- All clothing and accessories unchanged
- NO tail — Pudgy Penguins do not have tails
- Feet: small compact solid orange ovals tucked directly under the body, angled slightly outward — NO toes, NO lines, NO detail
- Flippers: {flipper_color} (body color), NOT {clothing_color} (clothing color)
- Background: solid pure white — no gradients, shadows, or scenery
- No sticker border or outline frame
- Full body visible from head to feet, character centered in frame"""


def _build_base_prompt(traits: dict) -> str:
    skin = traits.get("skin_color", "blue")
    flipper = traits.get("flipper_color", skin)
    clothing_color = traits.get("clothing_color", "none")
    return BASE_PROMPT.format(
        skin_color=skin,
        flipper_color=flipper,
        belly_color=traits.get("belly_color", "white"),
        eye_type=traits.get("eye_type", "round black eyes"),
        head_accessory=traits.get("head_accessory", "none"),
        face_accessory=traits.get("face_accessory", "none"),
        clothing=traits.get("clothing", "none"),
        clothing_color=clothing_color,
        overall_description=traits.get("overall_description", "a Pudgy Penguin"),
    )


def _build_edit_prompt(traits: dict, emotion: dict) -> str:
    skin = traits.get("skin_color", "blue")
    flipper = traits.get("flipper_color", skin)
    clothing_color = traits.get("clothing_color", "none")
    return EDIT_PROMPT.format(
        emotion_edit=emotion["prompt"],
        flipper_color=flipper,
        clothing_color=clothing_color,
    )


def _extract_image_bytes(data: dict) -> bytes:
    """Extract image bytes from OpenRouter API response."""
    msg = data["choices"][0]["message"]

    # OpenRouter native: inline_images or images array
    for key in ("inline_images", "images"):
        if key in msg and msg[key]:
            data_url = msg[key][0]
            if isinstance(data_url, dict):
                data_url = data_url.get("image_url", {}).get("url", "") or data_url.get("url", "")
            b64_data = data_url.split(",", 1)[1] if "," in data_url else data_url
            return base64.b64decode(b64_data)

    # Content may be a list of parts
    content = msg.get("content", "")
    if isinstance(content, list):
        for part in content:
            if isinstance(part, dict):
                if part.get("type") == "image_url":
                    url = part.get("image_url", {}).get("url", "")
                    b64_data = url.split(",", 1)[1] if "," in url else url
                    return base64.b64decode(b64_data)
                if part.get("type") == "image" and "data" in part:
                    return base64.b64decode(part["data"])

    # Fallback: search text content for base64 data URL
    if isinstance(content, str):
        match = re.search(r"data:image/[^;]+;base64,([A-Za-z0-9+/=]+)", content)
        if match:
            return base64.b64decode(match.group(1))

    raise ValueError(f"No image found in response. Keys in message: {list(msg.keys())}")


def _image_to_data_url(image_path: str) -> str:
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    ext = image_path.rsplit(".", 1)[-1].lower()
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "webp": "image/webp"}.get(ext, "image/png")
    return f"data:{mime};base64,{b64}"


def _bytes_to_data_url(image_bytes: bytes, mime: str = "image/png") -> str:
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:{mime};base64,{b64}"


def _call_model(data_url: str, prompt: str, temperature: float = 0.2) -> bytes:
    resp = http_post(
        OPENROUTER_URL,
        headers={"Content-Type": "application/json"},
        timeout=120,
        json={
            "model": IMAGE_MODEL,
            "modalities": ["text", "image"],
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ],
                }
            ],
            "temperature": temperature,
            "max_tokens": 4096,
        },
    )
    resp.raise_for_status()
    return _extract_image_bytes(resp.json())


def generate_base(image_path: str, traits: dict) -> bytes:
    """Generate a full-body neutral-pose base sticker from the character image."""
    data_url = _pad_for_full_body(image_path)
    prompt = _build_base_prompt(traits)
    return _call_model(data_url, prompt, temperature=0.3)


def generate_base_from_bytes(image_bytes: bytes, traits: dict, mime: str = "image/png") -> bytes:
    """Generate a full-body neutral-pose base sticker from raw image bytes."""
    data_url = _bytes_to_data_url(image_bytes, mime)
    prompt = _build_base_prompt(traits)
    return _call_model(data_url, prompt, temperature=0.3)


def generate_sticker(base_image_bytes: bytes, traits: dict, emotion: dict) -> bytes:
    """Edit the base sticker to show a specific expression/pose."""
    data_url = _bytes_to_data_url(base_image_bytes)
    prompt = _build_edit_prompt(traits, emotion)
    return _call_model(data_url, prompt, temperature=0.2)
