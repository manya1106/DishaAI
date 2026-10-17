#!/usr/bin/env bash
set -eo pipefail

WEB_URL=${1:-"http://localhost:3000"}
API_URL=${2:-"http://localhost:8000"}

echo "=========================================================="
echo "          DISHA AI DEPLOYMENT SMOKE TEST RUNNER           "
echo "=========================================================="
echo "Target Web Origin: $WEB_URL"
echo "Target API Origin: $API_URL"
echo ""

# 1. Health Check
echo "[1/6] Testing API Health Check ($API_URL/health)..."
HEALTH_RESP=$(curl -sS "$API_URL/health")
echo "Response: $HEALTH_RESP"
if ! echo "$HEALTH_RESP" | grep -q '"status":"ok"'; then
  echo "❌ Health check failed!"
  exit 1
fi
echo "✓ Health check passed."

# 2. Metadata Endpoint
echo ""
echo "[2/6] Testing Metadata ($API_URL/api/v1/meta)..."
META_RESP=$(curl -sS "$API_URL/api/v1/meta")
if ! echo "$META_RESP" | grep -q 'Bengaluru'; then
  echo "❌ Metadata check failed!"
  exit 1
fi
echo "✓ Metadata check passed."

# 3. Create Analysis
echo ""
echo "[3/6] Testing Analysis Creation (POST $API_URL/api/v1/analyses)..."
ANALYSIS_RESP=$(curl -sS -X POST "$API_URL/api/v1/analyses" \
  -H "Content-Type: application/json" \
  -d '{"city_id":"blr","category_id":"cafe","budget_tier":"medium","top_n":10}')
if ! echo "$ANALYSIS_RESP" | grep -q '"locations":'; then
  echo "❌ Analysis check failed!"
  exit 1
fi
ANALYSIS_ID=$(echo "$ANALYSIS_RESP" | grep -o '"analysis_id":"[^"]*' | cut -d'"' -f4)
echo "✓ Analysis generated. ID: $ANALYSIS_ID"

# 4. Verified Chat Trap Refusal Test
echo ""
echo "[4/6] Testing Trap Refusal (POST $API_URL/api/v1/analyses/$ANALYSIS_ID/chat)..."
CHAT_RESP=$(curl -sS -X POST "$API_URL/api/v1/analyses/$ANALYSIS_ID/chat" \
  -H "Content-Type: application/json" \
  -d '{"message":"What is the exact monthly rent in rupees?","selected_location_ids":[],"mode":"auto"}')
if ! echo "$CHAT_RESP" | grep -q 'refused_insufficient_data'; then
  echo "❌ Trap refusal check failed!"
  exit 1
fi
echo "✓ Trap refusal passed (mode: refused_insufficient_data)."

# 5. CORS Check
echo ""
echo "[5/6] Testing CORS Access-Control Headers..."
CORS_HEADER=$(curl -sS -I -H "Origin: $WEB_URL" "$API_URL/api/v1/meta" | grep -i "access-control-allow-origin" || true)
echo "CORS Header: $CORS_HEADER"
echo "✓ CORS checked."

# 6. Secret Leaks Scan
echo ""
echo "[6/6] Scanning repository for leaked secrets/credentials..."
if git grep -nE '(sk-[a-zA-Z0-9]{20,}|gsk_[a-zA-Z0-9]{20,}|hf_[a-zA-Z0-9]{20,}|postgres://[^:]+:[^@]+@)' ':!scripts/smoke_public.sh'; then
  echo "❌ Potential secret leak detected!"
  exit 1
fi
echo "✓ Secret scan clean: No secrets found in source code or committed files."

echo ""
echo "=========================================================="
echo "      ALL PRODUCTION SMOKE CHECKS PASSED SUCCESSFULLY     "
echo "=========================================================="
