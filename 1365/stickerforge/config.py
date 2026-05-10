"""StickerForge configuration — platform specs, emotions, and model settings."""

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

VISION_MODEL = "google/gemini-2.5-flash"
IMAGE_MODEL = "google/gemini-3-pro-image-preview"

STICKER_SIZE = 512
MAX_FILE_SIZE = 512 * 1024  # 512KB
STICKER_BORDER_WIDTH = 8  # pixels for the white die-cut outline

PLATFORM_SPECS = {
    "telegram": {
        "size": 512,
        "format": "webp",
        "extension": ".webp",
        "max_file_size": 512 * 1024,
    },
    "whatsapp": {
        "size": 512,
        "format": "webp",
        "extension": ".webp",
        "max_file_size": 100 * 1024,
    },
    "wechat": {
        "size": 240,
        "format": "png",
        "extension": ".png",
        "max_file_size": 1024 * 1024,
    },
    "line": {
        "size": 370,
        "format": "png",
        "extension": ".png",
        "max_file_size": 1024 * 1024,
    },
    "discord": {
        "size": 320,
        "format": "png",
        "extension": ".png",
        "max_file_size": 512 * 1024,
    },
}

# ---------------------------------------------------------------------------
# Face trait classification
# ---------------------------------------------------------------------------
# Face traits that are just expressions (safe to change eyes for emotions)
EXPRESSION_ONLY_FACES = {
    "normal", "winking", "blushing", "cute", "cross eyed", "star struck",
}

# Everything else is a physical accessory that MUST be preserved:
# Eyewear: Circle Glasses, Star Glasses, Aviator, Clout Goggles, Goggles,
#          Monocle, Scouter, 3D Glasses, Sunglasses
# Eye covers: Cucumbers, Eyepatch
# Masks: Hero Mask Blue, Hero Mask Red, Villain Mask, Football
# Facial hair: Beard, Mustache, Handlebar Bear
# Marks: Scar, Squad
# Rare: Laser Eyes, Sparkle Eyes, Bandana

# ---------------------------------------------------------------------------
# Emotion prompts — standard (eyes can change)
# ---------------------------------------------------------------------------
EMOTIONS = [
    {
        "name": "happy",
        "emoji": "😊",
        "filename": "happy",
        "prompt": (
            "Change the expression to extremely happy — big wide smile, eyes closed with joy. "
            "Change the pose to jumping with raised flippers. "
            "Add a few small solid gray four-pointed star sparkles overlapping the body."
        ),
        "prompt_preserve_face": (
            "Keep the eyes EXACTLY as they are — do not close them, do not change them. "
            "Open the beak wide to show happiness. Do not draw any mouth or lines below the beak. "
            "Change the pose to jumping with raised flippers. "
            "Add a few small solid gray four-pointed star sparkles overlapping the body."
        ),
    },
    {
        "name": "sad",
        "emoji": "😢",
        "filename": "sad",
        "prompt": (
            "Change the expression to sad and dejected — droopy eyes, a single tear "
            "rolling down the cheek. Change the pose to slouched with flippers hanging down."
        ),
        "prompt_preserve_face": (
            "Keep the eyes EXACTLY as they are — do not change them at all. "
            "Angle the beak slightly downward. Do not draw any mouth or lines below the beak. "
            "Add a single tear rolling down one cheek. "
            "Change the pose to slouched with flippers hanging down. "
            "Add slightly drooped eyebrows above the eyes to show sadness."
        ),
    },
    {
        "name": "angry",
        "emoji": "😠",
        "filename": "angry",
        "prompt": (
            "Change the expression to angry and furious — furrowed brows, puffed cheeks, "
            "clenched flippers. Add small steam puffs near the head."
        ),
        "prompt_preserve_face": (
            "Keep the eyes EXACTLY as they are — do not change them at all. "
            "Add strongly furrowed angry brows ABOVE the eyes. Do not draw any mouth or lines below the beak. "
            "Add puffed red cheeks showing fury. Clench the flippers into fists. "
            "Add small steam puffs near the head."
        ),
    },
    {
        "name": "surprised",
        "emoji": "😮",
        "filename": "surprised",
        "prompt": (
            "Change the expression to shocked and surprised — wide open eyes, open mouth. "
            "Change the pose to flippers thrown up in the air. "
            "Add exclamation marks near the head."
        ),
        "prompt_preserve_face": (
            "Keep the eyes EXACTLY as they are — do not change them at all. "
            "Open the beak wide in shock. Do not draw any mouth or lines below the beak. "
            "Add raised eyebrows above the eyes. "
            "Change the pose to flippers thrown up in the air. "
            "Add exclamation marks near the head."
        ),
    },
    {
        "name": "love",
        "emoji": "😍",
        "filename": "love",
        "prompt": (
            "Change only the visible eye(s) to red heart-shaped eyes — keep any eyepatch, glasses, or eye accessories unchanged. "
            "Add small pink circles on both cheeks. "
            "Add a few small red heart shapes near the head."
        ),
        "prompt_preserve_face": (
            "Keep the eyes EXACTLY as they are — do not change them at all. "
            "Do not draw any mouth or lines below the beak. "
            "Add small flat solid pink circles on both cheeks — no glow, no blur, no radiance. "
            "Add a few small red heart shapes near the head. "
            "No glowing effects, no bloom, no radial light, no soft halos anywhere. "
            "Keep the background solid pure white (#FFFFFF)."
        ),
    },
    {
        "name": "cool",
        "emoji": "😎",
        "filename": "cool",
        "prompt": (
            "Change the expression to a smug confident smirk with one eye winking. "
            "Change the pose to leaning back doing a peace sign with one flipper. "
            "Add a few small solid gray four-pointed star sparkles overlapping the body."
        ),
        "prompt_preserve_face": (
            "Keep the eyes EXACTLY as they are — do not change them, do not wink. "
            "Keep the beak as is — no extra mouth or smile lines. "
            "Change the pose to leaning back doing a peace sign with one flipper. "
            "Add a few small solid gray four-pointed star sparkles overlapping the body."
        ),
    },
]

EMOTION_NAMES = [e["name"] for e in EMOTIONS]
EMOTION_MAP = {e["name"]: e for e in EMOTIONS}

# ---------------------------------------------------------------------------
# Pudgy Penguins NFT (ERC-721 on Ethereum)
# ---------------------------------------------------------------------------
PUDGY_CONTRACT = "0xBd3531dA5CF5857e7CfAA92426877b022e612cf8"
PUDGY_TOTAL_SUPPLY = 8888  # token IDs 0–8887
PUDGY_IMAGE_CID = "QmNf1UsmdGaMbpatQ6toXSkzDpizaGmC9zfunCyoz1enD5"
PUDGY_METADATA_CID = "bafybeibc5sgo2plmjkq2tzmhrn54bk3crhnc23zd2msg4ea7a4pxrkgfna"

# Gateways tried in order — first success wins
IPFS_GATEWAYS = [
    "https://ipfs.io/ipfs",
    "https://gateway.pinata.cloud/ipfs",
    "https://dweb.link/ipfs",
]
