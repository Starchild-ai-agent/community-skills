"""ZIP packaging for sticker packs."""

import os
import zipfile


def create_zip(output_dir: str, filenames: list) -> str:
    """Create a ZIP file containing the given sticker files."""
    zip_path = os.path.join(output_dir, "sticker_pack.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for fname in filenames:
            filepath = os.path.join(output_dir, fname)
            if os.path.exists(filepath):
                zf.write(filepath, fname)
    return zip_path
