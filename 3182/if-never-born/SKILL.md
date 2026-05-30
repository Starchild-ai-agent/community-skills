---
name: "@3182/if-never-born"
version: 1.0.0
author: Agentway
tags: [story, fairy-tale, gift, healing, illustration, storybook]
description: |
  Generate a warm, healing parallel-universe fairy tale (~1000 words) plus 3 cohesive storybook illustrations, themed "if this person had never been born, what would the world miss." Output is a polished HTML storybook that can be previewed and published.

  Use when the user wants a personalized "if I had never been born" / "如果我没出生" tale for a real person — input is a name, age, and 3 key life events. Great for birthdays, memorials, encouragement gifts, or healing keepsakes.
metadata:
  starchild:
    emoji: "🌟"
    skillKey: if-never-born
    requires:
      bins: [python3]
user-invocable: true
---

# If I Had Never Been Born — 平行宇宙治愈童话

You are the storyteller. This skill turns a real person into the hero of a tender fairy tale that proves, by gentle contrast, that their existence mattered. The device is a parallel world where they were never born — and the warmth that goes missing there.

## Inputs (collect first)

Ask for these if not given. Keep it light, one short message:

1. **Name** — what to call the hero (real or nickname).
2. **Age** — used for tone (a child's tale vs. an elder's tale) and small details.
3. **3 key life events** — moments that shaped them or touched others. Examples: "taught her little sister to ride a bike," "moved to a new city alone at 22," "started a small bakery," "stayed up nursing a sick friend." Mundane, human ripples work BETTER than grand achievements — the healing comes from small specifics.

Optional: language (default = match the user), gender/pronoun, a relationship note (whose gift this is), a favorite color/animal/place to weave in.

Then **confirm the language** and write in it. ~1000 words means ~1000 Chinese characters for zh, ~1000 words for en.

## Narrative skeleton — "The Keeper of Maybes"

Always follow this 3-act arc. It guarantees the tone lands warm, not morbid.

**Frame:** A gentle cosmic guardian — the Keeper of Maybes (守梦人 / 星灵 / 织光者, pick a fitting name) — visits {name} and offers to show the world that would exist if {name} had never been born. Never frame this as death. It's a "what if you were never here at all" — softer, dreamlike.

**Act 1 — The Spark (≈200 words).** Introduce {name} warmly with age-appropriate, sensory detail. Establish their ordinary world and one small thing they think doesn't matter about themselves (this is the seed the story will redeem). The Keeper arrives and poses the question.

**Act 2 — The Three Absences (≈600 words, ~200 each).** Walk through three vignettes of the parallel world, one per life event. In each:
- Show concretely what/who is *missing* — a person never comforted, a dish never cooked, a song never heard, a courage never sparked, a chain of small kindnesses that never happened.
- Make it specific and sensory, never abstract ("the world would be sadder" = banned; "the bench by the river never heard her laugh, so the old man who sat there each morning never learned to smile again" = good).
- Each vignette ends on a quiet ache that the reader feels — but the dread is gentle, wrapped in beauty.
- Each vignette = one illustration (see below).

**Act 3 — The Return (≈200 words).** The Keeper brings {name} home; the parallel world's missing lights flicker back on, one by one, tied to the three vignettes. Land the healing thesis: a life isn't measured by how big it is, but by the warmth it leaves in others — and {name} leaves a great deal. End with a tender line spoken *to* {name} by name.

## Tone & craft rules

- **Warm, lyrical, hopeful.** Fairy-tale register: simple sentences, a little magic, gentle rhythm. Read like a bedtime story for the soul.
- **Concrete over abstract.** Earn emotion with specific images, smells, sounds, names of small things.
- **Never morbid.** No grief over death; the absence is a soft "what if," always resolved into affirmation.
- **Use the real details.** Weave the 3 events naturally; don't list them. Use the optional color/animal/place if given.
- **Length discipline.** ~1000 words / 字. Tight and complete, not padded.

## The 3 illustrations

Generate AFTER the story so prompts match the scenes you wrote. Use `image_generate`.

**Style anchor (paste into every prompt for cohesion):**
`dreamy storybook watercolor illustration, soft warm light, gentle pastel palette, golden-hour glow, picture-book aesthetic, tender and healing mood, delicate ink linework, no text`

**Character anchor:** write a 1-line fixed description of {name} (approx age, hair, one signature item/color) and paste it into all 3 prompts so the hero looks consistent.

**The 3 scenes** map to the three vignettes — show the *moment of warmth* (the version where {name} exists), not the empty void, so the images feel healing:
1. Vignette 1's tender moment.
2. Vignette 2's tender moment.
3. The Return — {name} and the Keeper of Maybes under a sky of relit stars/lights.

Settings: `aspect_ratio="landscape"`, `quality="medium"`, `n=1`. Use `nanopro` (default) for warmth and coherence. Read each `images[0].path` from the tool result — never guess paths.

## Assemble the storybook

Build a polished HTML page so it's shareable.

1. Write the story + metadata to a JSON file (see `scripts/build_storybook.py` header for schema).
2. Run: `python3 skills/if-never-born/scripts/build_storybook.py <story.json> <out.html>`
   - The script interleaves the 3 images between story sections and applies the storybook CSS theme.
3. Save outputs under `output/if-never-born/<name>/` (story.md, the 3 images, storybook.html).

Tell the user the full path: `output/if-never-born/<name>/storybook.html`.

## Publishing (when the user wants to share)

The HTML is self-contained-ish (images are relative paths in the same folder). To make a public link:
- Load the **community-publish** skill and call `publish_preview()` on the story folder, OR serve via the `preview` tool and share the `/preview/{id}/` link.
- On web, you can also just point the user to the local `storybook.html` path — the frontend renders it.

## Quick checklist
1. Collect name + age + 3 events (+ optional extras), confirm language.
2. Write the ~1000-word tale via the 3-act skeleton.
3. Generate 3 cohesive illustrations (style + character anchors).
4. Build the HTML storybook with the script.
5. Give the user the path; offer to publish.
