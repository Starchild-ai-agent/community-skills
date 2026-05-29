#!/usr/bin/env bash
# Verify a freshly-deployed CVM: health, attestation, and one round-trip chat.
# Usage:  bash smoke-test.sh           # reads .cvm_url
#         bash smoke-test.sh <url>     # explicit URL
set -euo pipefail

URL="${1:-$(cat .cvm_url 2>/dev/null || true)}"
if [ -z "$URL" ]; then
  echo "❌ no CVM URL given and .cvm_url not found"; exit 1
fi

echo "▶ /health"
curl -fsS "$URL/health" | python3 -m json.tool

echo ""
echo "▶ /attestation"
curl -fsS "$URL/attestation" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f'  quote bytes:  {len(d.get(\"quote\",\"\")) // 2}')
print(f'  report_data:  {d.get(\"report_data\", \"\")[:32]}…')
"

echo ""
echo "▶ /chat (PING → expect PONG)"
RESP=$(curl -fsS -X POST "$URL/chat" \
  -H 'content-type: application/json' \
  -d '{"messages":[{"role":"user","content":"reply with just the single word PONG"}],"stream":false}')
echo "$RESP" | python3 -c "
import sys, json
d = json.load(sys.stdin)
msg = d.get('message', {}).get('content', '')
print(f'  reply: {msg!r}')
if 'PONG' in msg.upper():
    print('  ✅ chat works')
else:
    print('  ⚠️  unexpected reply (LLM up but maybe model not following instruction)')
"

echo ""
echo "✅ smoke test complete"
