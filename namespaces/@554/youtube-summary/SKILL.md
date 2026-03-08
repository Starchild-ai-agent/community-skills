---
name: youtube-summary
version: 1.0.0
description: "Summarize YouTube videos by fetching their transcript and generating a structured summary. Use when the user shares a YouTube link and wants a summary, key points, or content overview of the video."

author: starchild
tags: [youtube, summary, transcript, video, content]

metadata:
  starchild:
    emoji: "🎬"
    skillKey: youtube-summary

user-invocable: true
---

# YouTube Summary Skill

Summarize any YouTube video by fetching its transcript via Supadata API and generating a structured, readable summary.

## Prerequisites

This skill requires a **Supadata API key**. The free tier is sufficient for personal use.

1. Sign up at [supadata.ai](https://supadata.ai)
2. Get your API key from the dashboard
3. Set it as an environment variable:
   ```
   SUPADATA_API_KEY=sd_your_key_here
   ```
   Or provide it directly when prompted.

---

## Workflow

### Step 1: Get the YouTube URL

Accept any of these formats:
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/watch?v=VIDEO_ID`

### Step 2: Fetch transcript via Supadata API

```bash
curl -s "https://api.supadata.ai/v1/youtube/transcript?url=VIDEO_URL" \
  -H "x-api-key: $SUPADATA_API_KEY"
```

Response format:
```json
{
  "content": [
    {"text": "...", "offset": 0, "duration": 5000, "lang": "en"},
    ...
  ],
  "lang": "en",
  "availableLangs": ["en"]
}
```

Extract the `text` fields and concatenate to get the full transcript.

### Step 3: Generate summary

Use the transcript text to produce a structured summary with these sections (adapt based on video content):

- **🎯 核心主题** — What is the video about?
- **📌 主要观点** — Key arguments or findings (3–7 bullet points)
- **📖 详细内容** — Expanded breakdown by section/topic
- **💡 结论** — Main takeaways or conclusions

Adjust language of summary to match the user's language preference.

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `401 Unauthorized` | Invalid or missing API key | Ask user to check their Supadata API key |
| `404 Not Found` | Video has no transcript / is private | Inform user the video has no available transcript |
| `429 Rate Limited` | Too many requests | Wait and retry, or upgrade Supadata plan |
| Empty `content` array | No captions available | Inform user and suggest they check if the video has captions |

---

## Example Usage

**User:** "帮我总结一下这个视频 https://youtu.be/BU9sIfGVhIQ"

**Agent workflow:**
1. Call Supadata API with the URL
2. Parse and concatenate transcript text
3. Generate structured summary in Chinese (matching user language)
4. Present summary with emoji section headers

---

## Notes

- Supadata free tier has a monthly quota — sufficient for casual use
- Videos without auto-generated or manual captions cannot be transcribed
- For non-English videos, Supadata returns the transcript in the original language; summarize accordingly
- Do NOT use `youtube-transcript-api` Python library or `yt-dlp` — cloud server IPs are blocked by YouTube. Always use Supadata API.
