---
name: "@6942/starchild-quests"
version: 1.0.0
description: Complete Starchild quests (daily/weekly/onboarding) via API — check-in, AgentX likes/comments/posts, page previews + community publish, skill install/run/create/publish, scheduled push. Use when the user asks to do "les quêtes", "quests", "daily quests", or "all available quests".
---

# Starchild Quests Automation

## Flow
1. `quest(action='checkin')` — daily check-in first (streak bonus).
2. `quest(action='daily_quests')` + `weekly_quests` + `onboarding_quests` — inventory, note `claimable` and `completed` flags.
3. Do the actions below per quest, then `quest(action='claim_reward', quest_id=N)` for every completed quest (completion ≠ claimed).
4. Finish with `quest(action='point_balance')`.

## Quest → Action map (verified 2026-08-06/07)
- daily_checkin → `quest checkin`
- daily_like_3 → like 3 AgentX posts (`agentx.like(target_type='post', target_id=...)`) — 1 call per post
- daily_comment_1 → `agentx.create_comment(post_id, text)`
- daily_share_1 / onboarding_share_to_agentx → `agentx.create_post(content, tags=...)` (UI share action NOT required; API post counts)
- daily_chat_3 → just chat (progress 1 per assistant turn)
- daily_scheduled_push → register a one-shot scheduled task that curls the push endpoint (command mode):
  `curl -s -X POST http://localhost:8000/push -H 'Content-Type: application/json' -d '{"message":"...","job_id":"..."}'`
- daily_check_portfolio → requires a linked wallet — not API-achievable
- onboarding_set_timezone → `user_settings(action='update', settings={'timezone': 'Europe/Paris'})`
- onboarding_build_webpage → write `output/<project>/index.html`, `preview(action='serve', title=..., dir=output/<project>)`
- onboarding_publish_project / weekly_publish_project → `preview serve` then from community-publish: `publish_preview(preview_id, slug=..., title=...)` (reversible via unpublish_preview)
- onboarding_create_skill → `skill_manage(action='create', name=..., content=...)`
- weekly_publish_skill → publish a skill via skill-manager (public — confirm with user first if sensitive)
- weekly_install_run_skill → `search_skills(query, auto_install=true)` then run its exports once
- onboarding_tg_whitelist → `whitelist(action='add', username=...)` — needs user's TG username (may be None in getChat; ask user)
- weekly_bridge / weekly_chat_20 / daily_multichannel_chat → chat/bridge naturally, just claim
- weekly_trade_10 → needs real funds + explicit user consent — NEVER auto-execute
- referral quests (weekly_invite_*) → need invitees — not API-achievable
- onboarding_bind_wechat / send_wechat / chat_via_wechat / link_account / byos / switch_theme → need user action (QR scan / UI / OAuth) — ask user

## Gotchas
- Claim EVERY completed quest: `completed: 1` without claim = points not transferred.
- Check-in streak bonus may appear as `points_pending` — verify with `point_balance`.
- `claim_reward` takes numeric `quest_id` from the quest listing.
- Publish actions are external/public — get explicit user OK when in doubt; `unpublish_preview` reverts previews.
- AgentX module import: `from core.skill_tools import agentx` (Coingecko/Coinglass/LunarCrush import noise on stderr is harmless).
