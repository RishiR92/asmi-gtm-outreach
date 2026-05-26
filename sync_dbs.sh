#!/bin/bash
# Run this before starting a local send session: ./sync_dbs.sh
# 1. Pulls new leads your team added on Railway → imports to local
# 2. Pulls Contacted/Replied status → marks locally so no re-sends

RAILWAY="https://asmi-gtm-outreach-production.up.railway.app"
LOCAL="http://localhost:8000"
VENV="$(dirname "$0")/backend/venv/bin/python3"

# Check local server is running
if ! curl -sf "$LOCAL/api/health" > /dev/null; then
  echo "❌ Local server not running. Start it first:"
  echo "   cd backend && venv/bin/uvicorn main:app --port 8000 &"
  exit 1
fi

echo "🔄 Step 1: Import new leads from Railway..."
curl -sf "$RAILWAY/api/leads?limit=500" > /tmp/railway_leads_sync.json

"$VENV" << 'PYEOF'
import json, requests

with open('/tmp/railway_leads_sync.json') as f:
    leads = json.load(f).get('data', [])

skip_statuses = {'Contacted', 'Replied', 'Not Interested', 'Feature Confirmed'}
generic_prefixes = ('contact@','hello@','info@','admin@','team@','support@','editor@',
                    'newsletter@','hi@','mail@','press@','media@','marketing@',
                    'organizer@','manager@','group@','community@','members@')

local_all = requests.get('http://localhost:8000/api/leads?limit=2000', timeout=10).json().get('data', [])
local_emails = {(x.get('email') or '').lower() for x in local_all if x.get('email')}

imported = skipped = 0
for l in leads:
    if l.get('status') in skip_statuses:
        skipped += 1
        continue
    e = (l.get('email') or '').lower()
    if not e or any(e.startswith(g) for g in generic_prefixes):
        continue
    if e in local_emails:
        skipped += 1
        continue

    payload = {k: l.get(k) for k in ['name','newsletter_name','url','email','estimated_audience',
                                       'category','contact_method','linkedin_url','twitter_handle','notes']}
    payload['status'] = l.get('status') or 'Email Found'
    r = requests.post('http://localhost:8000/api/leads', json=payload, timeout=5)
    if r.status_code in (200, 201):
        imported += 1
        print(f"  ✓ {l['name']} ({e})")

print(f"  → {imported} new leads imported, {skipped} already present")
PYEOF

echo ""
echo "🔄 Step 2: Sync Contacted/Replied status from Railway → Local..."

for STATUS in "Contacted" "Replied" "Not Interested"; do
  EMAILS=$(curl -sf "$RAILWAY/api/leads?status=$STATUS&limit=500" | "$VENV" -c "
import sys, json
leads = json.load(sys.stdin).get('data', [])
emails = [l['email'] for l in leads if l.get('email')]
import json; print(json.dumps({'emails': emails, 'status': '$STATUS'}))
" 2>/dev/null)

  COUNT=$(echo "$EMAILS" | "$VENV" -c "import sys,json; print(len(json.load(sys.stdin)['emails']))")
  if [ "$COUNT" -gt 0 ]; then
    RESULT=$(curl -sf -X POST "$LOCAL/api/leads/bulk-status" \
      -H "Content-Type: application/json" -d "$EMAILS" | "$VENV" -c "import sys,json; print(json.load(sys.stdin).get('message','?'))")
    echo "  $STATUS ($COUNT): $RESULT"
  fi
done

echo ""
echo "✅ Sync complete. Safe to send — no duplicates."
