"""Vision-based character trait extraction using Gemini."""

import base64
import json

from .http import post as http_post
from .config import OPENROUTER_URL, VISION_MODEL

ANALYSIS_PROMPT = """You are analyzing a Pudgy Penguin NFT image. Extract ALL visual traits into this exact JSON schema:

{
  "skin_color": "specific color description of the penguin's body/skin (e.g. 'pastel mint green', 'classic blue', 'dark gray')",
  "flipper_color": "the exact color of the penguin's flippers/wings — these are BODY parts, not clothing (e.g. 'dark gray', 'navy blue', 'teal', 'mint green'). Look at the flippers themselves, they match the penguin's body color, NOT the outfit.",
  "belly_color": "the color of the penguin's belly/chest area — the lighter front-facing part (e.g. 'white', 'cream', 'light yellow')",
  "eye_type": "eye style description (e.g. 'normal round black eyes', 'sleepy half-closed', 'heart eyes')",
  "head_accessory": "exact description of hat/crown/headband/hair or 'none'",
  "face_accessory": "exact description of glasses/mask/scarf or 'none'",
  "clothing": "exact description of shirt/jacket/hoodie/scarf or 'none'",
  "clothing_color": "the main color(s) of the clothing (e.g. 'gray', 'red and white striped') or 'none' if no clothing",
  "special_features": "any other distinguishing features or 'none'",
  "overall_description": "A complete 2-sentence description of this specific penguin's full appearance including all accessories and colors"
}

Be EXTREMELY specific about colors (e.g. "pastel mint green" not just "green").
Be EXACT about accessories (e.g. "red beanie with white pom-pom" not just "hat").
IMPORTANT: The flipper_color is the penguin's natural flipper/wing color (a body part). It matches the penguin's body, NOT the clothing. Carefully distinguish between the clothing color and the flipper color — they are often different.
Return ONLY valid JSON, no markdown fences or extra text."""


def extract_traits_from_bytes(image_bytes: bytes, mime: str = "image/png") -> dict:
    """Extract traits from raw image bytes."""
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    return _call_vision(b64, mime)


def extract_traits(image_path: str) -> dict:
    """Extract traits from an image file path."""
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    ext = image_path.rsplit(".", 1)[-1].lower()
    mime = {
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "webp": "image/webp",
    }.get(ext, "image/png")
    return _call_vision(b64, mime)


def _call_vision(b64: str, mime: str) -> dict:
    """Call the vision model and parse the JSON response."""
    resp = http_post(
        OPENROUTER_URL,
        headers={"Content-Type": "application/json"},
        timeout=60,
        json={
            "model": VISION_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
                        {"type": "text", "text": ANALYSIS_PROMPT},
                    ],
                }
            ],
            "temperature": 0.1,
            "max_tokens": 1000,
        },
    )
    resp.raise_for_status()

    raw = resp.json()["choices"][0]["message"]["content"].strip()
    # Strip markdown fences if present
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
        if raw.endswith("```"):
            raw = raw[:-3]
        raw = raw.strip()

    return json.loads(raw)
