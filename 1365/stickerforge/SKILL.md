---
name: "@1365/stickerforge"
version: 1.0.0
description: AI sticker pack generator — extract character traits from images and generate emotion-variant sticker packs for Telegram, WhatsApp, Discord, LINE, and WeChat
tools:
  - sticker_from_pudgy
  - sticker_generate_pack
  - sticker_extract_traits
  - sticker_generate_single

metadata:
  starchild:
    emoji: "\U0001F9E9"
    skillKey: stickerforge

user-invocable: false
disable-model-invocation: false
---

# StickerForge

AI-powered sticker pack generator. Turns any character image into a full set of emotion-variant stickers ready for messaging platforms.

## How It Works

1. **Trait Extraction** — A vision model (Gemini 2.5 Flash) analyzes the input character image and extracts detailed visual traits: body color, flipper color, belly color, eye type, accessories, clothing, and an overall description.

2. **Base Generation** — An image generation model (Gemini 3 Pro) creates a full-body neutral-pose sticker using the extracted traits as strict guidance, ensuring character consistency.

3. **Emotion Variants** — The base sticker is edited into emotion variants (happy, sad, angry, surprised, love, cool). Each edit only changes expression and pose while preserving all character traits.

4. **Post-Processing** — Each sticker goes through:
   - Background removal (flood-fill from edges)
   - White die-cut sticker outline
   - Resize to platform specs
   - Format conversion (WebP for Telegram/WhatsApp, PNG for others)

5. **Packaging** — All stickers are packaged into a downloadable ZIP file.

## Available Tools

### `sticker_from_pudgy`
Generate a sticker pack directly from a Pudgy Penguin NFT — just provide the token ID. The tool automatically fetches the NFT image from IPFS (no image upload needed), retrieves on-chain metadata/traits, then runs the full sticker generation pipeline.

**Parameters:**
- `token_id` (required) — Pudgy Penguin token ID (0–8887)
- `platform` (optional, default: "telegram") — Target platform: telegram, whatsapp, discord, line, wechat
- `emotions` (optional, default: all 6) — List of emotions to generate: happy, sad, angry, surprised, love, cool

**Returns:** Path to the output directory containing individual stickers, `sticker_pack.zip`, the original NFT image, and both on-chain and vision-extracted traits.

**Example usage:**
- "I have Pudgy Penguin #6873, make me stickers" → `sticker_from_pudgy(token_id=6873)`
- "Make WhatsApp stickers for Pudgy #100, just happy and love" → `sticker_from_pudgy(token_id=100, platform="whatsapp", emotions=["happy", "love"])`

### `sticker_extract_traits`
Extract visual traits from a character image. Returns a JSON object describing the character's colors, accessories, clothing, and overall appearance. Useful for understanding what the character looks like before generating stickers.

**Parameters:**
- `image_path` (required) — Path to the character image file (PNG, JPG, or WebP)

### `sticker_generate_pack`
Generate a complete sticker pack from a character image. Runs the full pipeline: trait extraction, base generation, emotion variants, post-processing, and ZIP packaging.

**Parameters:**
- `image_path` (required) — Path to the character image file
- `platform` (optional, default: "telegram") — Target platform: telegram, whatsapp, discord, line, wechat
- `emotions` (optional, default: all 6) — List of emotions to generate: happy, sad, angry, surprised, love, cool

**Returns:** Path to the output directory containing individual stickers and a `sticker_pack.zip`.

### `sticker_generate_single`
Generate a single emotion sticker from a character image. Useful for testing or generating one-off stickers.

**Parameters:**
- `image_path` (required) — Path to the character image file
- `emotion` (required) — One of: happy, sad, angry, surprised, love, cool
- `platform` (optional, default: "telegram") — Target platform

**Returns:** Path to the generated sticker file.

## Supported Platforms

| Platform  | Size   | Format | Max Size |
|-----------|--------|--------|----------|
| Telegram  | 512px  | WebP   | 512KB    |
| WhatsApp  | 512px  | WebP   | 100KB    |
| Discord   | 320px  | PNG    | 512KB    |
| LINE      | 370px  | PNG    | 1MB      |
| WeChat    | 240px  | PNG    | 1MB      |

## Emotions

| Emotion    | Description                                           |
|------------|-------------------------------------------------------|
| Happy      | Big smile, jumping with raised flippers, sparkles     |
| Sad        | Droopy eyes, single tear, slouched pose               |
| Angry      | Furrowed brows, puffed cheeks, steam puffs            |
| Surprised  | Wide eyes, open mouth, flippers up, exclamation marks |
| Love       | Heart eyes, blushing cheeks, floating hearts          |
| Cool       | Smug smirk, winking, peace sign, sparkles             |

## Requirements

- **OpenRouter API access** is handled automatically via SC-Proxy — no API key configuration needed. All calls to `openrouter.ai` are routed through the proxy which injects credentials.
- Python packages: `requests`, `Pillow` (should already be installed)
- Uses `core.http_client.proxied_post` for all OpenRouter API calls
