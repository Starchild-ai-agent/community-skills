"""
StickerForge Skill — AI Sticker Pack Generator

Generates emotion-variant sticker packs from character images.
Supports Telegram, WhatsApp, Discord, LINE, and WeChat.

OpenRouter API access is handled via SC-Proxy (no API key needed).
"""

import logging
from typing import List

logger = logging.getLogger(__name__)


def register(api) -> List[str]:
    """Skill entry point — register all StickerForge tools."""
    registered = []

    try:
        from .tools import (
            StickerExtractTraitsTool,
            StickerGeneratePackTool,
            StickerGenerateSingleTool,
            StickerFromPudgyTool,
        )

        api.register_tool(StickerExtractTraitsTool())
        api.register_tool(StickerGeneratePackTool())
        api.register_tool(StickerGenerateSingleTool())
        api.register_tool(StickerFromPudgyTool())

        registered = [
            "sticker_extract_traits",
            "sticker_generate_pack",
            "sticker_generate_single",
            "sticker_from_pudgy",
        ]
        logger.info(f"Registered StickerForge tools ({len(registered)} tools)")
    except Exception as e:
        logger.warning(f"Failed to load StickerForge tools: {e}")

    return registered


EXTENSION_INFO = {
    "name": "stickerforge",
    "version": "1.0.0",
    "description": "AI sticker pack generator for messaging platforms",
    "tools": [
        "sticker_extract_traits",
        "sticker_generate_pack",
        "sticker_generate_single",
        "sticker_from_pudgy",
    ],
    "env_vars": [],
}
