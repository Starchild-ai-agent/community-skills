---
name: "@1892/fal-image"
version: 1.1.0
description: "Generate images using Fal.ai (Flux Pro, Flux Ultra, and other models). Use when you need to create AI-generated images, artwork, visuals, or any image content. Supports Flux Pro 1.1 Ultra (best quality), Flux Pro 1.1, Flux Dev, and more."
author: starchild
tags: [image-generation, fal, flux, ai-art, visuals, dalle-alternative]

metadata:
  starchild:
    emoji: "🎨"
    skillKey: fal-image
    requires:
      env: [FAL_API_KEY]
    install:
      - kind: pip
        package: fal-client

user-invocable: true
---

# Fal.ai Image Generation

[Fal.ai](https://fal.ai) is one of the most widely used API platforms for AI image generation, offering fast inference on top models including Flux Pro, Stable Diffusion, and more. To use this skill, create a free API key at **[fal.ai/dashboard/keys](https://fal.ai/dashboard/keys)** and add it to your `.env` as `FAL_API_KEY`.

Generate high-quality images via Fal.ai's API. The key is already in `.env` as `FAL_API_KEY` — the client needs it as `FAL_KEY`.

## Quick Usage

```python
import fal_client, os
os.environ['FAL_KEY'] = os.environ['FAL_API_KEY']  # required alias

result = fal_client.run(
    'fal-ai/flux-pro/v1.1-ultra',  # best model
    arguments={
        'prompt': 'your prompt here',
        'image_size': 'square_hd',   # 1:1 for Instagram feed
        'num_images': 1,
        'output_format': 'jpeg',
        'safety_tolerance': '5'      # 1=strict, 6=permissive
    }
)
url = result['images'][0]['url']  # direct CDN URL, download with requests
```

## Models & When to Use Them

| Endpoint | Quality | Speed | Use for |
|---|---|---|---|
| `fal-ai/flux-pro/v1.1-ultra` | ⭐⭐⭐⭐⭐ | ~8s | Hero shots, campaign images |
| `fal-ai/flux-pro/v1.1` | ⭐⭐⭐⭐ | ~5s | Batch content, iterations |
| `fal-ai/flux/dev` | ⭐⭐⭐ | ~3s | Rapid prototyping |
| `fal-ai/flux-realism` | ⭐⭐⭐⭐ | ~6s | Photorealistic shots |

Default to `flux-pro/v1.1-ultra` unless speed matters more than quality.

## Image Sizes

| Value | Pixels | Use for |
|---|---|---|
| `square_hd` | 1024×1024 | Instagram feed (1:1) |
| `portrait_4_3` | 768×1024 | Instagram portrait feed |
| `portrait_16_9` | 576×1024 | Instagram Stories / Reels cover |
| `landscape_4_3` | 1024×768 | Wide format |
| `landscape_16_9` | 1024×576 | YouTube thumbnail |

## Full Response Schema

```python
result = {
    'images': [{'url': str, 'width': int, 'height': int, 'content_type': str}],
    'timings': {'inference': float},
    'seed': int,
    'has_nsfw_concepts': [bool],
    'prompt': str  # may be refined by model
}
```

## Downloading the Image

```python
import requests
response = requests.get(url)
with open('output/image.jpg', 'wb') as f:
    f.write(response.content)
```

## Starchild Brand Prompt Formula

For on-brand Starchild content, prompts should include:
- **Base mood**: `deep black background, dark cinematic atmosphere`
- **Color accent**: `amber orange glow, #F84600 orange light`
- **Style**: `abstract, minimal, geometric, high contrast`
- **NOT**: product mockups, literal UI, stock-photo style, people, faces

Good prompt template:
```
[abstract concept], deep black background, [specific visual element], 
amber orange light refraction, cinematic, ultra detailed, 
8k, high contrast, minimal composition, no text
```

## Composition Layer (Pillow)

After generating, apply the brand composition script:
`skills/fal-image/scripts/compose_instagram.py`

This adds:
- Starchild logo + wordmark
- Orange top accent bar
- Bottom gradient overlay for text legibility
- Optional headline/subtext

## Gotchas

- Always set `os.environ['FAL_KEY'] = os.environ['FAL_API_KEY']` — the client looks for `FAL_KEY` not `FAL_API_KEY`
- URLs are temporary CDN links (~1 hour) — download immediately after generation
- `safety_tolerance: '5'` is fine for abstract/artistic content; lower it for anything near real people
- Generation is async-capable: use `fal_client.submit()` + `fal_client.result()` for batch jobs
