#!/bin/bash
# Run this before starting local server: ./sync_dbs.sh
# Pulls Contacted/Replied leads from Railway and marks them locally.

RAILWAY="https://asmi-gtm-outreach-production.up.railway.app"
LOCAL="http://localhost:8000"

# Check local server is running
if ! curl -sf "$LOCAL/api/health" > /dev/null; then
  echo "❌ Local server not running. Start it first:"
  echo "   cd backend && venv/bin/uvicorn main:app --port 8000 &"
  exit 1
fi

echo "🔄 Syncing Contacted/Replied leads from Railway → Local..."

for STATUS in Contacted Replied "Not Interested"; do
  EMAILS=$(curl -sf "$RAILWAY/api/leads?status=$STATUS&limit=500" | python3 -c "
import sys, json
leads = json.load(sys.stdin).get('data', [])
emails = [l['email'] for l in leads if l.get('email')]
import json; print(json.dumps({'emails': emails, 'status': '$STATUS'}))
" 2>/dev/null)

  COUNT=$(echo "$EMAILS" | python3 -c "import sys,json; print(len(json.load(sys.stdin)['emails']))")
  if [ "$COUNT" -gt 0 ]; then
    RESULT=$(curl -sf -X POST "$LOCAL/api/leads/bulk-status" \
      -H "Content-Type: application/json" -d "$EMAILS" | python3 -c "import sys,json; print(json.load(sys.stdin).get('message','?'))")
    echo "  $STATUS: $RESULT"
  fi
done

echo "✅ Sync complete. Safe to send — no duplicates."
