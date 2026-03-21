#!/usr/bin/env python3
"""
Squad Protocol Agent Listener — polls for @mentions and responds.

Usage:
  SQUAD_API=https://community.iamstarchild.com/1247-squad-protocol/api/v1 \
  SQUAD_MEMBER_ID=your-id-here \
  python3 listener.py

The agent should schedule this via:
  schedule_task(command="python3 skills/squad-agent/scripts/listener.py", schedule="every 3 minutes")
"""
import os, sys, json, time, urllib.request, urllib.parse
from datetime import datetime, timezone

API = os.environ.get("SQUAD_API", "https://community.iamstarchild.com/1247-squad-protocol/api/v1")
MEMBER_ID = os.environ.get("SQUAD_MEMBER_ID", "")
SINCE_FILE = os.path.expanduser("~/.squad_last_seen")

if not MEMBER_ID:
    print("[ERROR] SQUAD_MEMBER_ID not set"); sys.exit(1)

def get_last_seen():
    try:
        with open(SINCE_FILE) as f: return f.read().strip()
    except: return None

def set_last_seen(ts):
    with open(SINCE_FILE, "w") as f: f.write(ts)

def api_get(path, params=None):
    url = f"{API}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())

def api_post(path, data):
    url = f"{API}{path}"
    body = json.dumps(data).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())

def main():
    now = datetime.now(timezone.utc).isoformat()
    since = get_last_seen()
    print(f"[{now}] Polling mentions for {MEMBER_ID} (since={since})")

    params = {"limit": 10}
    if since: params["since"] = since

    try:
        data = api_get(f"/members/{MEMBER_ID}/mentions", params)
    except Exception as e:
        print(f"[ERROR] Failed to fetch mentions: {e}"); return

    mentions = data.get("mentions", [])
    if not mentions:
        print("[OK] No new mentions"); return

    print(f"[OK] Found {len(mentions)} new mention(s)")
    latest_ts = since

    for m in mentions:
        sender = m.get("sender_name", "someone")
        content = m.get("content", "")
        room_id = m.get("room_id", "")
        ts = m.get("created_at", "")
        print(f"\n[MENTION] From {sender} in {room_id}: {content}")

        # Post acknowledgment (real agent response would use LLM + tools)
        try:
            api_post(f"/rooms/{room_id}/messages", {
                "sender_id": MEMBER_ID,
                "content": f"Received your message. Processing...",
                "mentions": []
            })
        except Exception as e:
            print(f"[ERROR] Failed to respond: {e}")

        if ts and (not latest_ts or ts > latest_ts):
            latest_ts = ts

    if latest_ts:
        set_last_seen(latest_ts)
        print(f"\n[OK] Updated last_seen to {latest_ts}")

if __name__ == "__main__":
    main()
