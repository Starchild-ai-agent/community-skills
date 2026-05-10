"""Sticker post-processing — background removal, outline, resize, and export."""

from io import BytesIO
from collections import deque
from PIL import Image, ImageFilter

from .config import STICKER_SIZE, MAX_FILE_SIZE, STICKER_BORDER_WIDTH, PLATFORM_SPECS


def flood_fill_remove_bg(img: Image.Image, threshold: int = 210) -> Image.Image:
    """Remove background via two-pass flood-fill from image edges.

    Pass 1: Remove near-white pixels (standard white bg removal).
    Pass 2: Expand from the transparent boundary through bright pastel pixels
             to catch colored glows (pink, yellow). Stops at dark pixels
             (character outlines) and vivid pixels (heart fills, effects).
             Character interior is unreachable — outlines block the flood.
    """
    img = img.convert("RGBA")
    pixels = img.load()
    w, h = img.size

    is_bg = set()
    queue = deque()

    # Seed from all four edges
    for x in range(w):
        queue.append((x, 0))
        queue.append((x, h - 1))
    for y in range(h):
        queue.append((0, y))
        queue.append((w - 1, y))

    # Pass 1: remove near-white background
    while queue:
        x, y = queue.popleft()
        if (x, y) in is_bg or x < 0 or y < 0 or x >= w or y >= h:
            continue

        r, g, b, a = pixels[x, y]
        if r > threshold and g > threshold and b > threshold and max(r, g, b) - min(r, g, b) < 35:
            is_bg.add((x, y))
            queue.append((x + 1, y))
            queue.append((x - 1, y))
            queue.append((x, y + 1))
            queue.append((x, y - 1))

    # Pass 2: expand through bright pastel pixels (colored glows)
    # Glow: brightness > 150, saturation < 100 (pastel pink/yellow)
    # Hearts: brightness < 110, saturation > 120 (vivid red) → won't match
    # Outlines: brightness < 80 → won't match
    # Character body behind outlines → unreachable
    fringe_queue = deque()
    # Seed from pass 1 boundary
    for bx, by in is_bg:
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = bx + dx, by + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in is_bg:
                fringe_queue.append((nx, ny))
    # Also seed directly from image edges — catches glow that extends to
    # the border with no white pixels for pass 1 to find
    for x in range(w):
        for y in [0, h - 1]:
            if (x, y) not in is_bg:
                fringe_queue.append((x, y))
    for y in range(h):
        for x in [0, w - 1]:
            if (x, y) not in is_bg:
                fringe_queue.append((x, y))

    while fringe_queue:
        x, y = fringe_queue.popleft()
        if (x, y) in is_bg or x < 0 or y < 0 or x >= w or y >= h:
            continue

        r, g, b, a = pixels[x, y]
        brightness = (r + g + b) // 3
        saturation = max(r, g, b) - min(r, g, b)
        if brightness > 150 and saturation < 100:
            is_bg.add((x, y))
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in is_bg:
                    fringe_queue.append((nx, ny))

    # Find edge pixels (foreground adjacent to background)
    edge_pixels = set()
    for bx, by in is_bg:
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]:
            nx, ny = bx + dx, by + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in is_bg:
                edge_pixels.add((nx, ny))

    # Set background pixels to transparent
    for x, y in is_bg:
        pixels[x, y] = (0, 0, 0, 0)

    # Alpha-matte edge pixels for smooth transition
    for x, y in edge_pixels:
        r, g, b, a = pixels[x, y]
        darkness = 255 - min(r, g, b)
        new_alpha = min(255, int(darkness * 1.3))
        pixels[x, y] = (r, g, b, new_alpha)

    # Smooth the alpha channel
    r_ch, g_ch, b_ch, a_ch = img.split()
    a_ch = a_ch.filter(ImageFilter.GaussianBlur(radius=0.8))
    img = Image.merge("RGBA", (r_ch, g_ch, b_ch, a_ch))

    return img


def add_sticker_outline(img: Image.Image, border_width: int = STICKER_BORDER_WIDTH,
                        color: tuple = (255, 255, 255, 255)) -> Image.Image:
    """Add a white die-cut sticker outline around the character programmatically.

    Works by dilating the alpha channel to create an expanded silhouette,
    then compositing a white border layer behind the original character.
    """
    alpha = img.split()[3]

    # Dilate the alpha channel by applying MaxFilter repeatedly
    dilated = alpha.copy()
    for _ in range(border_width):
        dilated = dilated.filter(ImageFilter.MaxFilter(3))

    # Smooth the dilated outline edge for a clean look
    dilated = dilated.filter(ImageFilter.GaussianBlur(radius=1.5))

    # Threshold back to solid after blur (keeps smooth edge but strong opacity)
    dilated = dilated.point(lambda p: min(255, int(p * 1.5)))

    # Create the white outline layer
    outline = Image.new("RGBA", img.size, color)
    outline.putalpha(dilated)

    # Composite: white outline behind the character
    result = Image.alpha_composite(outline, img)
    return result


def resize_for_sticker(img: Image.Image, size: int = STICKER_SIZE) -> Image.Image:
    """Resize and center on a transparent canvas of the given size."""
    w, h = img.size
    # Leave room for the image to breathe (don't fill 100%)
    target = int(size * 0.92)
    scale = target / max(w, h)
    new_w, new_h = int(w * scale), int(h * scale)
    resized = img.resize((new_w, new_h), Image.LANCZOS)

    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    offset_x = (size - new_w) // 2
    offset_y = (size - new_h) // 2
    canvas.paste(resized, (offset_x, offset_y), resized)
    return canvas


def to_webp_bytes(img: Image.Image, lossless: bool = True) -> bytes:
    """Save as WebP. Uses lossless by default for guaranteed alpha fidelity."""
    buf = BytesIO()
    img.save(buf, format="WEBP", lossless=lossless, exact=True)
    return buf.getvalue()


def to_png_bytes(img: Image.Image) -> bytes:
    buf = BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def process(image_bytes: bytes, size: int = STICKER_SIZE) -> bytes:
    """Full sticker processing pipeline:
    1. Remove white background (flood-fill)
    2. Add programmatic white die-cut border
    3. Resize to target size
    4. Export as WebP with RGBA transparency (Telegram auto-renders as sticker)
    """
    img = Image.open(BytesIO(image_bytes)).convert("RGBA")
    img = flood_fill_remove_bg(img)
    img = add_sticker_outline(img)
    img = resize_for_sticker(img, size)

    webp_bytes = to_webp_bytes(img, lossless=True)
    if len(webp_bytes) > MAX_FILE_SIZE:
        webp_bytes = to_webp_bytes(img, lossless=False)
    return webp_bytes


def process_for_platform(image_bytes: bytes, platform: str) -> bytes:
    """Platform-aware processing. Uses PLATFORM_SPECS for size/format/limits."""
    spec = PLATFORM_SPECS.get(platform, PLATFORM_SPECS["telegram"])
    size = spec["size"]
    fmt = spec["format"]
    max_size = spec["max_file_size"]

    img = Image.open(BytesIO(image_bytes)).convert("RGBA")
    img = flood_fill_remove_bg(img)
    img = add_sticker_outline(img)
    img = resize_for_sticker(img, size)

    if fmt == "webp":
        out_bytes = to_webp_bytes(img, lossless=True)
        if len(out_bytes) > max_size:
            out_bytes = to_webp_bytes(img, lossless=False)
        # If still too large (WhatsApp 100KB limit), reduce quality iteratively
        if len(out_bytes) > max_size:
            for quality in [85, 70, 55, 40]:
                buf = BytesIO()
                img.save(buf, format="WEBP", quality=quality)
                out_bytes = buf.getvalue()
                if len(out_bytes) <= max_size:
                    break
    else:
        out_bytes = to_png_bytes(img)
        if len(out_bytes) > max_size:
            # Reduce size slightly until under limit
            current_size = size
            while len(out_bytes) > max_size and current_size > 128:
                current_size = int(current_size * 0.85)
                smaller = resize_for_sticker(img, current_size)
                out_bytes = to_png_bytes(smaller)

    return out_bytes
