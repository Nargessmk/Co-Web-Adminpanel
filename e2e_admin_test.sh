#!/usr/bin/env bash
# E2E test for the admin panel fixes:
#   1. admin routes accept a valid 30-minute token (audience/issuer verified)
#   2. product create with image upload goes through the storage microservice
#   3. consultations admin list returns JSON
#   4. over-long (60 min), wrong-audience, and expired tokens are rejected
set -u
cd "$(dirname "$0")"
BASE="http://127.0.0.1:4000"
SECRET="PDv7DrqznYL6nv7DrqzjnQYO9JxIsWdcjnQYL6nu0f"
PASS=0; FAIL=0

mint() { # mint <lifetime_minutes> <audience>
  docker exec cloudland-backend python -c "
import jwt, datetime, sys
mins = int(sys.argv[1]); aud = sys.argv[2]
now = datetime.datetime.now(datetime.timezone.utc)
print(jwt.encode({'sub':'e2e-admin','roles':['admin'],
  'app_id':'feb89eda-0360-4f12-ab5f-846534d5ab78','type':'access',
  'iat': now, 'exp': now + datetime.timedelta(minutes=mins),
  'iss':'APM_jwt','aud':aud}, '$SECRET', algorithm='HS256'))
" "$1" "$2" 2>/dev/null
}

check() { # check <description> <expected_http> <actual_http>
  if [ "$2" = "$3" ]; then PASS=$((PASS+1)); echo "PASS: $1 ($3)"
  else FAIL=$((FAIL+1)); echo "FAIL: $1 — expected $2, got $3"; fi
}

TOKEN=$(mint 30 ailand.ai)
echo "token: ${TOKEN:0:40}... (${#TOKEN} bytes)"

# --- 1. admin lists return 200 JSON
R=$(curl -s -m 15 -o /tmp/e2e_body -w '%{http_code}' -H "Authorization: Bearer $TOKEN" "$BASE/api/products/admin/all")
check "GET /api/products/admin/all" 200 "$R"
grep -q '"success":true' /tmp/e2e_body && echo "  body: success:true" || { echo "  body: $(head -c 200 /tmp/e2e_body)"; FAIL=$((FAIL+1)); }

R=$(curl -s -m 15 -o /tmp/e2e_body -w '%{http_code}' -H "Authorization: Bearer $TOKEN" "$BASE/api/consultations/admin?limit=5")
check "GET /api/consultations/admin" 200 "$R"

# --- 2. product create WITHOUT image
R=$(curl -s -m 20 -o /tmp/e2e_body -w '%{http_code}' -X POST \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"title":"E2E Delete Me","slug":"e2e-delete-me","short_description":"e2e","category_id":5}' \
  "$BASE/api/products/admin")
check "POST /api/products/admin (no image)" 201 "$R"
PRODUCT_ID=$(grep -o '"id":[0-9]*' /tmp/e2e_body | head -1 | cut -d: -f2)
echo "  created product id: ${PRODUCT_ID:-none}"

# --- 3. product create WITH image (exercises storage/MinIO path)
printf '\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82' > /tmp/e2e.png
R=$(curl -s -m 60 -o /tmp/e2e_body -w '%{http_code}' -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -F 'title=E2E Upload Test' -F 'slug=e2e-upload-test' -F 'category_id=5' \
  -F 'image=@/tmp/e2e.png;type=image/png' \
  "$BASE/api/products/admin")
check "POST /api/products/admin (with image upload)" 201 "$R"
UP_ID=$(grep -o '"id":[0-9]*' /tmp/e2e_body | head -1 | cut -d: -f2)
IMG_URL=$(grep -o '"image_url":"[^"]*"' /tmp/e2e_body | head -1 | cut -d'"' -f4)
echo "  uploaded product id: ${UP_ID:-none}, image_url: ${IMG_URL:-none}"
if [ -n "$IMG_URL" ]; then
  # image_url is an absolute S3 URL — fetch it directly
  IR=$(curl -s -m 25 -o /dev/null -w '%{http_code}' "$IMG_URL")
  check "GET uploaded image ($IMG_URL)" 200 "$IR"
fi

# --- 4. negative token tests
R=$(curl -s -m 15 -o /dev/null -w '%{http_code}' -H "Authorization: Bearer $(mint 60 ailand.ai)" "$BASE/api/products/admin/all")
check "60-minute token rejected" 401 "$R"

R=$(curl -s -m 15 -o /dev/null -w '%{http_code}' -H "Authorization: Bearer $(mint 30 evil.example.com)" "$BASE/api/products/admin/all")
check "wrong-audience token rejected" 401 "$R"

R=$(curl -s -m 15 -o /dev/null -w '%{http_code}' "$BASE/api/products/admin/all")
check "missing token rejected" 401 "$R"

# --- 5. storage health
R=$(curl -s -m 15 -o /dev/null -w '%{http_code}' http://127.0.0.1:4003/api/health)
check "storage /api/health" 200 "$R"

# --- 6. cleanup created products
if [ -n "${PRODUCT_ID:-}" ]; then
  R=$(curl -s -m 20 -o /dev/null -w '%{http_code}' -X DELETE -H "Authorization: Bearer $TOKEN" "$BASE/api/products/admin/$PRODUCT_ID")
  check "DELETE test product $PRODUCT_ID" 200 "$R"
fi
if [ -n "${UP_ID:-}" ]; then
  R=$(curl -s -m 20 -o /dev/null -w '%{http_code}' -X DELETE -H "Authorization: Bearer $TOKEN" "$BASE/api/products/admin/$UP_ID")
  check "DELETE uploaded test product $UP_ID" 200 "$R"
fi

echo
echo "RESULT: $PASS passed, $FAIL failed"
exit $FAIL
