"""StickerForge tools — BaseTool implementations for sticker generation."""

import asyncio
import json
import os
import logging
import requests
from datetime import datetime
from typing import Optional, List

from core.tool import BaseTool, ToolContext, ToolResult

from .config import (
    EMOTIONS,
    EMOTION_NAMES,
    EMOTION_MAP,
    PLATFORM_SPECS,
    PUDGY_TOTAL_SUPPLY,
    PUDGY_IMAGE_CID,
    PUDGY_METADATA_CID,
    IPFS_GATEWAYS,
)

logger = logging.getLogger(__name__)


class StickerExtractTraitsTool(BaseTool):
    """Extract visual traits from a character image."""

    @property
    def name(self) -> str:
        return "sticker_extract_traits"

    @property
    def description(self) -> str:
        return (
            "Analyze a character image and extract detailed visual traits "
            "(body color, flipper color, belly color, eye type, accessories, clothing, etc.). "
            "Returns a JSON object describing the character's appearance. "
            "Use this to inspect what the vision model sees before generating stickers.\n\n"
            "Example: sticker_extract_traits(image_path=\"/workspace/penguin.png\")"
        )

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "image_path": {
                    "type": "string",
                    "description": "Absolute path to the character image file (PNG, JPG, or WebP)",
                },
            },
            "required": ["image_path"],
        }

    async def execute(self, ctx: ToolContext, image_path: str, **kwargs) -> ToolResult:
        if not os.path.isfile(image_path):
            return ToolResult(
                success=False,
                error=f"Image not found: {image_path}",
                error_category="invalid_parameter",
            )

        try:
            from .trait_extractor import extract_traits

            traits = await asyncio.to_thread(extract_traits, image_path)
            return ToolResult(success=True, output=json.dumps(traits, indent=2))
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class StickerGeneratePackTool(BaseTool):
    """Generate a complete sticker pack from a character image."""

    @property
    def name(self) -> str:
        return "sticker_generate_pack"

    @property
    def description(self) -> str:
        return (
            "Generate a complete sticker pack from a character image. "
            "Runs the full pipeline: trait extraction, base sticker generation, "
            "emotion variants (happy, sad, angry, surprised, love, cool), "
            "post-processing (background removal, outline, resize), and ZIP packaging.\n\n"
            "Supported platforms: telegram, whatsapp, discord, line, wechat\n"
            "Available emotions: happy, sad, angry, surprised, love, cool\n\n"
            "This tool takes several minutes to complete as it makes multiple AI image generation calls.\n\n"
            "Example: sticker_generate_pack(image_path=\"/workspace/penguin.png\", platform=\"telegram\")"
        )

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "image_path": {
                    "type": "string",
                    "description": "Absolute path to the character image file (PNG, JPG, or WebP)",
                },
                "platform": {
                    "type": "string",
                    "description": "Target messaging platform",
                    "enum": list(PLATFORM_SPECS.keys()),
                    "default": "telegram",
                },
                "emotions": {
                    "type": "array",
                    "items": {"type": "string", "enum": EMOTION_NAMES},
                    "description": "Which emotions to generate (default: all 6)",
                },
            },
            "required": ["image_path"],
        }

    async def execute(
        self,
        ctx: ToolContext,
        image_path: str,
        platform: str = "telegram",
        emotions: Optional[List[str]] = None,
        **kwargs,
    ) -> ToolResult:
        if not os.path.isfile(image_path):
            return ToolResult(
                success=False,
                error=f"Image not found: {image_path}",
                error_category="invalid_parameter",
            )

        if platform not in PLATFORM_SPECS:
            return ToolResult(
                success=False,
                error=f"Unknown platform: {platform}. Choose from: {', '.join(PLATFORM_SPECS.keys())}",
                error_category="invalid_parameter",
            )

        # Resolve emotions
        if emotions:
            invalid = [e for e in emotions if e not in EMOTION_MAP]
            if invalid:
                return ToolResult(
                    success=False,
                    error=f"Unknown emotions: {invalid}. Choose from: {EMOTION_NAMES}",
                    error_category="invalid_parameter",
                )
            selected_emotions = [EMOTION_MAP[e] for e in emotions]
        else:
            selected_emotions = EMOTIONS

        try:
            result = await asyncio.to_thread(
                _run_pack_pipeline, image_path, platform, selected_emotions, ctx.workspace_dir
            )
            return ToolResult(success=True, output=result)
        except Exception as e:
            logger.exception("sticker_generate_pack failed")
            return ToolResult(success=False, error=str(e))


class StickerGenerateSingleTool(BaseTool):
    """Generate a single emotion sticker from a character image."""

    @property
    def name(self) -> str:
        return "sticker_generate_single"

    @property
    def description(self) -> str:
        return (
            "Generate a single emotion sticker from a character image. "
            "Useful for testing or creating one-off stickers.\n\n"
            "Available emotions: happy, sad, angry, surprised, love, cool\n"
            "Supported platforms: telegram, whatsapp, discord, line, wechat\n\n"
            "Example: sticker_generate_single(image_path=\"/workspace/penguin.png\", emotion=\"happy\")"
        )

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "image_path": {
                    "type": "string",
                    "description": "Absolute path to the character image file (PNG, JPG, or WebP)",
                },
                "emotion": {
                    "type": "string",
                    "description": "The emotion to generate",
                    "enum": EMOTION_NAMES,
                },
                "platform": {
                    "type": "string",
                    "description": "Target messaging platform",
                    "enum": list(PLATFORM_SPECS.keys()),
                    "default": "telegram",
                },
            },
            "required": ["image_path", "emotion"],
        }

    async def execute(
        self,
        ctx: ToolContext,
        image_path: str,
        emotion: str,
        platform: str = "telegram",
        **kwargs,
    ) -> ToolResult:
        if not os.path.isfile(image_path):
            return ToolResult(
                success=False,
                error=f"Image not found: {image_path}",
                error_category="invalid_parameter",
            )

        if emotion not in EMOTION_MAP:
            return ToolResult(
                success=False,
                error=f"Unknown emotion: {emotion}. Choose from: {EMOTION_NAMES}",
                error_category="invalid_parameter",
            )

        if platform not in PLATFORM_SPECS:
            return ToolResult(
                success=False,
                error=f"Unknown platform: {platform}. Choose from: {', '.join(PLATFORM_SPECS.keys())}",
                error_category="invalid_parameter",
            )

        try:
            result = await asyncio.to_thread(
                _run_single_pipeline, image_path, emotion, platform, ctx.workspace_dir
            )
            return ToolResult(success=True, output=result)
        except Exception as e:
            logger.exception("sticker_generate_single failed")
            return ToolResult(success=False, error=str(e))


class StickerFromPudgyTool(BaseTool):
    """Generate a sticker pack from a Pudgy Penguin NFT by token ID."""

    @property
    def name(self) -> str:
        return "sticker_from_pudgy"

    @property
    def description(self) -> str:
        return (
            "Generate a sticker pack directly from a Pudgy Penguin NFT. "
            "Just provide the token ID (0–8887) — the tool fetches the NFT image "
            "from IPFS and runs the full sticker generation pipeline.\n\n"
            "Example: sticker_from_pudgy(token_id=6873)\n"
            "Example: sticker_from_pudgy(token_id=100, platform=\"whatsapp\", emotions=[\"happy\", \"love\"])"
        )

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "token_id": {
                    "type": "integer",
                    "description": "Pudgy Penguin token ID (0–8887)",
                    "minimum": 0,
                    "maximum": 8887,
                },
                "platform": {
                    "type": "string",
                    "description": "Target messaging platform",
                    "enum": list(PLATFORM_SPECS.keys()),
                    "default": "telegram",
                },
                "emotions": {
                    "type": "array",
                    "items": {"type": "string", "enum": EMOTION_NAMES},
                    "description": "Which emotions to generate (default: all 6)",
                },
            },
            "required": ["token_id"],
        }

    async def execute(
        self,
        ctx: ToolContext,
        token_id: int,
        platform: str = "telegram",
        emotions: Optional[List[str]] = None,
        **kwargs,
    ) -> ToolResult:
        if not isinstance(token_id, int) or token_id < 0 or token_id > 8887:
            return ToolResult(
                success=False,
                error=f"Invalid token ID: {token_id}. Must be 0–8887.",
                error_category="invalid_parameter",
            )

        if platform not in PLATFORM_SPECS:
            return ToolResult(
                success=False,
                error=f"Unknown platform: {platform}. Choose from: {', '.join(PLATFORM_SPECS.keys())}",
                error_category="invalid_parameter",
            )

        # Resolve emotions
        if emotions:
            invalid = [e for e in emotions if e not in EMOTION_MAP]
            if invalid:
                return ToolResult(
                    success=False,
                    error=f"Unknown emotions: {invalid}. Choose from: {EMOTION_NAMES}",
                    error_category="invalid_parameter",
                )
            selected_emotions = [EMOTION_MAP[e] for e in emotions]
        else:
            selected_emotions = EMOTIONS

        try:
            result = await asyncio.to_thread(
                _run_pudgy_pipeline, token_id, platform, selected_emotions, ctx.workspace_dir
            )
            return ToolResult(success=True, output=result)
        except Exception as e:
            logger.exception("sticker_from_pudgy failed")
            return ToolResult(success=False, error=str(e))


# ---------------------------------------------------------------------------
# IPFS helpers for Pudgy Penguins
# ---------------------------------------------------------------------------


def _fetch_from_ipfs(cid: str, path: str, timeout: int = 60) -> bytes:
    """Download content from IPFS, trying multiple gateways."""
    errors = []
    for gateway in IPFS_GATEWAYS:
        url = f"{gateway}/{cid}/{path}"
        try:
            resp = requests.get(url, timeout=timeout)
            resp.raise_for_status()
            return resp.content
        except Exception as e:
            errors.append(f"{gateway}: {e}")
            continue
    raise RuntimeError(
        f"Failed to fetch from IPFS ({cid}/{path}). Tried {len(IPFS_GATEWAYS)} gateways:\n"
        + "\n".join(errors)
    )


def _fetch_pudgy_image(token_id: int) -> bytes:
    """Download the PNG image for a Pudgy Penguin token."""
    return _fetch_from_ipfs(PUDGY_IMAGE_CID, f"penguin/{token_id}.png", timeout=90)


def _fetch_pudgy_metadata(token_id: int) -> dict:
    """Fetch on-chain metadata (name, attributes) for a Pudgy Penguin token."""
    raw = _fetch_from_ipfs(PUDGY_METADATA_CID, str(token_id), timeout=30)
    return json.loads(raw)


# ---------------------------------------------------------------------------
# Pipeline helpers (run in thread via asyncio.to_thread)
# ---------------------------------------------------------------------------


def _run_pack_pipeline(
    image_path: str,
    platform: str,
    selected_emotions: list,
    workspace_dir: str,
) -> str:
    """Synchronous full-pack pipeline — runs in a worker thread."""
    from .trait_extractor import extract_traits
    from .sticker_generator import generate_base, generate_sticker
    from .post_processor import process_for_platform
    from .packager import create_zip

    spec = PLATFORM_SPECS[platform]
    ext = spec["extension"]

    # Output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(workspace_dir, "stickerforge", timestamp)
    os.makedirs(output_dir, exist_ok=True)

    # Step 1: Extract traits
    traits = extract_traits(image_path)
    traits_path = os.path.join(output_dir, "traits.json")
    with open(traits_path, "w") as f:
        json.dump(traits, f, indent=2)

    # Detect if face has a physical accessory that must be preserved
    # Step 2: Generate base sticker
    base_bytes = generate_base(image_path, traits)
    raw_dir = os.path.join(output_dir, "raw")
    os.makedirs(raw_dir, exist_ok=True)
    with open(os.path.join(raw_dir, "base.png"), "wb") as f:
        f.write(base_bytes)

    # Step 3: Generate emotion variants
    raw_stickers = {}
    for emotion in selected_emotions:
        image_bytes = generate_sticker(base_bytes, traits, emotion)
        raw_stickers[emotion["name"]] = image_bytes
        with open(os.path.join(raw_dir, f"{emotion['filename']}.png"), "wb") as f:
            f.write(image_bytes)

    if not raw_stickers:
        raise RuntimeError("No stickers were generated")

    # Step 4: Post-process
    filenames = []
    for emotion in selected_emotions:
        name = emotion["name"]
        if name not in raw_stickers:
            continue
        processed_bytes = process_for_platform(raw_stickers[name], platform)
        out_name = f"{emotion['filename']}{ext}"
        out_path = os.path.join(output_dir, out_name)
        with open(out_path, "wb") as f:
            f.write(processed_bytes)
        filenames.append(out_name)

    # Step 5: Package
    zip_path = create_zip(output_dir, filenames)

    # Build summary
    lines = [
        f"Sticker pack generated: {len(filenames)} stickers for {platform}",
        f"Output directory: {output_dir}",
        f"ZIP file: {zip_path} ({os.path.getsize(zip_path)} bytes)",
        "",
        "Character traits:",
        f"  Body: {traits.get('skin_color', '?')}",
        f"  Flippers: {traits.get('flipper_color', '?')}",
        f"  Clothing: {traits.get('clothing', '?')} ({traits.get('clothing_color', '?')})",
        f"  Description: {traits.get('overall_description', '?')}",
        "",
        "Generated stickers:",
    ]
    for fname in filenames:
        fpath = os.path.join(output_dir, fname)
        lines.append(f"  {fpath} ({os.path.getsize(fpath)} bytes)")

    return "\n".join(lines)


def _run_single_pipeline(
    image_path: str,
    emotion_name: str,
    platform: str,
    workspace_dir: str,
) -> str:
    """Synchronous single-sticker pipeline — runs in a worker thread."""
    from .trait_extractor import extract_traits
    from .sticker_generator import generate_base, generate_sticker
    from .post_processor import process_for_platform

    spec = PLATFORM_SPECS[platform]
    ext = spec["extension"]
    emotion = EMOTION_MAP[emotion_name]

    # Output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(workspace_dir, "stickerforge", timestamp)
    os.makedirs(output_dir, exist_ok=True)

    # Step 1: Extract traits
    traits = extract_traits(image_path)
    # Step 2: Generate base sticker
    base_bytes = generate_base(image_path, traits)

    # Step 3: Generate emotion variant
    raw_bytes = generate_sticker(base_bytes, traits, emotion)

    # Step 4: Post-process
    processed_bytes = process_for_platform(raw_bytes, platform)
    out_name = f"{emotion['filename']}{ext}"
    out_path = os.path.join(output_dir, out_name)
    with open(out_path, "wb") as f:
        f.write(processed_bytes)

    return (
        f"Sticker generated: {out_path} ({os.path.getsize(out_path)} bytes)\n"
        f"Character: {traits.get('overall_description', '?')}\n"
        f"Emotion: {emotion_name} {emotion['emoji']}\n"
        f"Platform: {platform} ({spec['size']}px {spec['format'].upper()})"
    )


def _run_pudgy_pipeline(
    token_id: int,
    platform: str,
    selected_emotions: list,
    workspace_dir: str,
) -> str:
    """Synchronous Pudgy Penguin pipeline — fetch from IPFS then generate stickers."""
    from .trait_extractor import extract_traits
    from .sticker_generator import generate_base, generate_sticker
    from .post_processor import process_for_platform
    from .packager import create_zip

    spec = PLATFORM_SPECS[platform]
    ext = spec["extension"]

    # Output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(workspace_dir, "stickerforge", f"pudgy_{token_id}_{timestamp}")
    os.makedirs(output_dir, exist_ok=True)

    # Step 1: Fetch NFT metadata + image from IPFS
    logger.info(f"Fetching Pudgy Penguin #{token_id} from IPFS...")
    nft_metadata = _fetch_pudgy_metadata(token_id)
    image_bytes = _fetch_pudgy_image(token_id)

    # Save original NFT image and metadata
    original_path = os.path.join(output_dir, f"pudgy_{token_id}.png")
    with open(original_path, "wb") as f:
        f.write(image_bytes)

    metadata_path = os.path.join(output_dir, "nft_metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(nft_metadata, f, indent=2)

    # Step 2: Extract visual traits via vision model
    traits = extract_traits(original_path)

    # Merge on-chain attributes into traits for reference
    on_chain_attrs = {
        attr["trait_type"]: attr["value"]
        for attr in nft_metadata.get("attributes", [])
    }
    traits["nft_name"] = nft_metadata.get("name", f"Pudgy Penguin #{token_id}")
    traits["on_chain_attributes"] = on_chain_attrs

    # Use on-chain Face trait for precise accessory detection
    nft_face_trait = on_chain_attrs.get("Face", "")
    traits["nft_face_trait"] = nft_face_trait
    traits_path = os.path.join(output_dir, "traits.json")
    with open(traits_path, "w") as f:
        json.dump(traits, f, indent=2)

    # Step 3: Generate base sticker
    base_bytes = generate_base(original_path, traits)
    raw_dir = os.path.join(output_dir, "raw")
    os.makedirs(raw_dir, exist_ok=True)
    with open(os.path.join(raw_dir, "base.png"), "wb") as f:
        f.write(base_bytes)

    # Step 4: Generate emotion variants
    raw_stickers = {}
    for emotion in selected_emotions:
        image_bytes = generate_sticker(base_bytes, traits, emotion)
        raw_stickers[emotion["name"]] = image_bytes
        with open(os.path.join(raw_dir, f"{emotion['filename']}.png"), "wb") as f:
            f.write(image_bytes)

    if not raw_stickers:
        raise RuntimeError("No stickers were generated")

    # Step 5: Post-process
    filenames = []
    for emotion in selected_emotions:
        name = emotion["name"]
        if name not in raw_stickers:
            continue
        processed_bytes = process_for_platform(raw_stickers[name], platform)
        out_name = f"{emotion['filename']}{ext}"
        out_path = os.path.join(output_dir, out_name)
        with open(out_path, "wb") as f:
            f.write(processed_bytes)
        filenames.append(out_name)

    # Step 6: Package
    zip_path = create_zip(output_dir, filenames)

    # Build summary
    lines = [
        f"Pudgy Penguin #{token_id} — {len(filenames)} stickers for {platform}",
        f"NFT: {nft_metadata.get('name', '?')}",
        f"On-chain traits: {', '.join(f'{k}: {v}' for k, v in on_chain_attrs.items())}",
        f"Output directory: {output_dir}",
        f"ZIP file: {zip_path} ({os.path.getsize(zip_path)} bytes)",
        "",
        "Vision-extracted traits:",
        f"  Body: {traits.get('skin_color', '?')}",
        f"  Flippers: {traits.get('flipper_color', '?')}",
        f"  Clothing: {traits.get('clothing', '?')} ({traits.get('clothing_color', '?')})",
        f"  Description: {traits.get('overall_description', '?')}",
        "",
        "Generated stickers:",
    ]
    for fname in filenames:
        fpath = os.path.join(output_dir, fname)
        lines.append(f"  {fpath} ({os.path.getsize(fpath)} bytes)")

    return "\n".join(lines)
