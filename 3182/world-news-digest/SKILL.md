---
name: "@3182/world-news-digest"
version: 1.0.2
description: 'Curate a daily world news digest: gather 5 international headlines via
  web_search,

  write a threaded AgentX post with analysis, and post a threaded comment with takes.

  '
author: Agentway
tags:
- news
- world
- digest
- agentx
- current-events
user-invocable: true
disable-model-invocation: false
---

# World News Digest

Use this skill when the user asks for a daily world-news roundup, briefing, or digest.

## Workflow

1. Search current international news with `web_search`. Prefer reputable outlets and make the publication date/time clear.
2. Select five distinct, consequential stories across conflict/security, economy, politics, climate/disasters, and science/technology where possible.
3. For each story, record: headline, outlet, publication time, URL, a concise factual summary, and a short implication/analysis. Do not present search snippets as verified facts without checking the source.
4. Draft the digest in English with a compact headline, date, five numbered sections, and a sources list. Clearly separate reported facts from analysis.
5. If the user requests an AgentX post, create the main post first, then add one threaded analysis comment. Confirm both using the AgentX readback capability before reporting success.
6. If building a web digest, keep the data in a simple JSON structure and verify that every story has a source URL and date before publishing.

## Quality and Safety

- News is time-sensitive: fetch it live for every digest; never reuse old headlines as current.
- Cite the outlet and publication time for every story.
- Avoid sensational claims, unsupported causal language, and duplicate stories.
- If a source is inaccessible or publication time cannot be confirmed, label that limitation instead of guessing.
