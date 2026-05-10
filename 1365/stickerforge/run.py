#!/usr/bin/env python3
"""Standalone runner for StickerForge — works outside the server process.

Usage:
    # From repo root:
    python -m skills.stickerforge.run 1095
    python -m skills.stickerforge.run 6873 --platform whatsapp --emotions happy love cool
    python -m skills.stickerforge.run 42 --output-dir ./my_stickers

    # From an image file instead of token ID:
    python -m skills.stickerforge.run --image /path/to/character.png

Requires OPENROUTER_API_KEY in environment (or .env file).
"""

import argparse
import json
import os
import sys
from datetime import datetime

# Allow running from repo root: python -m skills.stickerforge.run
# The relative imports in the skill modules need the package to be importable.
# If run as __main__, ensure the repo root is on sys.path.
if __name__ == "__main__":
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

from skills.stickerforge.config import (
    EMOTIONS,
    EMOTION_MAP,
    EMOTION_NAMES,
    PLATFORM_SPECS,
    PUDGY_TOTAL_SUPPLY,
)


def fetch_pudgy(token_id: int, output_dir: str) -> str:
    """Download Pudgy Penguin image from IPFS, return local path."""
    from skills.stickerforge.tools import _fetch_pudgy_image, _fetch_pudgy_metadata

    print(f"  Fetching Pudgy Penguin #{token_id} from IPFS...")
    metadata = _fetch_pudgy_metadata(token_id)
    image_bytes = _fetch_pudgy_image(token_id)

    image_path = os.path.join(output_dir, f"pudgy_{token_id}.png")
    with open(image_path, "wb") as f:
        f.write(image_bytes)

    meta_path = os.path.join(output_dir, "nft_metadata.json")
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)

    attrs = {a["trait_type"]: a["value"] for a in metadata.get("attributes", [])}
    print(f"  {metadata.get('name', '?')}")
    print(f"  On-chain: {', '.join(f'{k}: {v}' for k, v in attrs.items())}")
    print(f"  Saved to: {image_path} ({len(image_bytes)} bytes)")
    return image_path


def run(image_path: str, platform: str, selected_emotions: list, output_dir: str):
    """Run the full sticker generation pipeline."""
    from skills.stickerforge.trait_extractor import extract_traits
    from skills.stickerforge.sticker_generator import generate_base, generate_sticker
    from skills.stickerforge.post_processor import process_for_platform
    from skills.stickerforge.packager import create_zip
    spec = PLATFORM_SPECS[platform]
    ext = spec["extension"]

    # Step 1: Extract traits
    print("\n[1/5] Extracting character traits...")
    traits = extract_traits(image_path)
    with open(os.path.join(output_dir, "traits.json"), "w") as f:
        json.dump(traits, f, indent=2)
    print(f"  Body: {traits.get('skin_color', '?')}")
    print(f"  Flippers: {traits.get('flipper_color', '?')}")
    print(f"  Clothing: {traits.get('clothing', '?')} ({traits.get('clothing_color', '?')})")
    print(f"  Description: {traits.get('overall_description', '?')}")

    # Step 2: Generate base sticker
    print("\n[2/5] Generating base sticker...")
    base_bytes = generate_base(image_path, traits)
    raw_dir = os.path.join(output_dir, "raw")
    os.makedirs(raw_dir, exist_ok=True)
    with open(os.path.join(raw_dir, "base.png"), "wb") as f:
        f.write(base_bytes)
    print(f"  Base generated ({len(base_bytes)} bytes)")

    # Step 3: Generate emotion variants
    print(f"\n[3/5] Generating {len(selected_emotions)} emotion variants...")
    raw_stickers = {}
    for i, emotion in enumerate(selected_emotions, 1):
        name = emotion["name"]
        print(f"  ({i}/{len(selected_emotions)}) {name}...", end="", flush=True)
        try:
            img_bytes = generate_sticker(base_bytes, traits, emotion)
            raw_stickers[name] = img_bytes
            with open(os.path.join(raw_dir, f"{emotion['filename']}.png"), "wb") as f:
                f.write(img_bytes)
            print(f" done ({len(img_bytes)} bytes)")
        except Exception as e:
            print(f" FAILED: {e}")

    if not raw_stickers:
        print("\nError: No stickers were generated.")
        sys.exit(1)

    # Step 4: Post-process
    print(f"\n[4/5] Post-processing for {platform}...")
    filenames = []
    for emotion in selected_emotions:
        name = emotion["name"]
        if name not in raw_stickers:
            continue
        print(f"  Processing {name}...", end="", flush=True)
        processed = process_for_platform(raw_stickers[name], platform)
        out_name = f"{emotion['filename']}{ext}"
        with open(os.path.join(output_dir, out_name), "wb") as f:
            f.write(processed)
        filenames.append(out_name)
        print(f" done ({len(processed)} bytes)")

    # Step 5: Package
    print("\n[5/5] Packaging...")
    zip_path = create_zip(output_dir, filenames)
    print(f"  {zip_path} ({os.path.getsize(zip_path)} bytes)")

    # Summary
    print(f"\nDone! {len(filenames)} stickers in: {output_dir}")
    for fname in filenames:
        fpath = os.path.join(output_dir, fname)
        print(f"  {fpath} ({os.path.getsize(fpath)} bytes)")


def main():
    parser = argparse.ArgumentParser(
        description="StickerForge — generate sticker packs from Pudgy Penguins or any character image"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("token_id", nargs="?", type=int, help="Pudgy Penguin token ID (0–8887)")
    group.add_argument("--image", type=str, help="Path to a character image file instead of token ID")
    parser.add_argument("--platform", default="telegram", choices=list(PLATFORM_SPECS.keys()))
    parser.add_argument("--emotions", nargs="+", default=None, choices=EMOTION_NAMES)
    parser.add_argument("--output-dir", default="outputs", help="Base output directory")
    args = parser.parse_args()

    # Resolve emotions
    if args.emotions:
        selected = [EMOTION_MAP[e] for e in args.emotions]
    else:
        selected = EMOTIONS

    # Output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if args.token_id is not None:
        dirname = f"pudgy_{args.token_id}_{timestamp}"
    else:
        dirname = timestamp
    output_dir = os.path.join(args.output_dir, dirname)
    os.makedirs(output_dir, exist_ok=True)

    # Get image
    if args.token_id is not None:
        if args.token_id < 0 or args.token_id > 8887:
            print(f"Error: token ID must be 0–8887, got {args.token_id}")
            sys.exit(1)
        image_path = fetch_pudgy(args.token_id, output_dir)
    else:
        image_path = args.image
        if not os.path.isfile(image_path):
            print(f"Error: image not found: {image_path}")
            sys.exit(1)

    run(image_path, args.platform, selected, output_dir)


if __name__ == "__main__":
    main()
