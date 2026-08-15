#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

cleanup() { docker compose down -v --remove-orphans >/dev/null 2>&1 || true; }
trap cleanup EXIT

export SERVICE_KEY="e2e-service-key"
docker compose up -d --build postgres redis identity account billing gateway

wait_for() {
  local url="$1"
  for _ in $(seq 1 60); do
    if curl -fsS "$url" >/dev/null 2>&1; then return 0; fi
    sleep 2
  done
  echo "Timed out waiting for $url" >&2
  return 1
}

wait_for_response() {
  local url="$1"
  for _ in $(seq 1 60); do
    if curl -sS -o /dev/null "$url" 2>/dev/null; then return 0; fi
    sleep 2
  done
  echo "Timed out waiting for an HTTP response from $url" >&2
  return 1
}

wait_for http://localhost:4001/health
wait_for http://localhost:4003/health
wait_for_response http://localhost:8081/accounts/plans/catalog
wait_for_response http://localhost:4000/graphql

EMAIL="e2e-$(date +%s)@pulse.local"
REGISTER=$(curl -fsS -X POST http://localhost:4001/auth/register \
  -H 'content-type: application/json' \
  -d "{\"email\":\"$EMAIL\",\"password\":\"PulsePass123!\"}")

ACCESS_TOKEN=$(python3 -c 'import json,sys; print(json.load(sys.stdin)["accessToken"])' <<<"$REGISTER")
USER_ID=$(python3 -c 'import json,sys; print(json.load(sys.stdin)["user"]["id"])' <<<"$REGISTER")
ACCOUNT_ID=$(python3 -c 'import uuid; print(uuid.uuid4())')
ACCOUNT_NUMBER="E2E-$(date +%s)"

docker compose exec -T postgres psql -U pulse -d pulse -v ON_ERROR_STOP=1 <<SQL
INSERT INTO accounts(id,account_number,user_id,full_name,status)
VALUES ('$ACCOUNT_ID','$ACCOUNT_NUMBER','$USER_ID','E2E Customer','active');
SQL

# Internal service must reject callers without the shared key.
STATUS=$(curl -s -o /dev/null -w '%{http_code}' "http://localhost:8081/accounts/$ACCOUNT_ID")
test "$STATUS" = "401"

# The authenticated customer can fetch their own account through GraphQL.
OWN=$(curl -fsS http://localhost:4000/graphql \
  -H "authorization: Bearer $ACCESS_TOKEN" \
  -H 'content-type: application/json' \
  -d "{\"query\":\"query { account(id: \\\"$ACCOUNT_ID\\\") { id account_number } }\"}")
python3 -c 'import json,sys; d=json.load(sys.stdin); assert not d.get("errors"), d; assert d["data"]["account"]["id"]' <<<"$OWN"

# The same customer cannot read the seeded demo customer's account.
FOREIGN=$(curl -fsS http://localhost:4000/graphql \
  -H "authorization: Bearer $ACCESS_TOKEN" \
  -H 'content-type: application/json' \
  -d '{"query":"query { account(id: \"aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa\") { id } }"}')
python3 -c 'import json,sys; d=json.load(sys.stdin); assert d.get("errors"), d' <<<"$FOREIGN"

# Unauthenticated GraphQL requests are rejected.
UNAUTH=$(curl -s http://localhost:4000/graphql -H 'content-type: application/json' -d '{"query":"query { plans { id } }"}')
python3 -c 'import json,sys; d=json.load(sys.stdin); assert d.get("errors"), d' <<<"$UNAUTH"

echo "Pulse E2E authorization smoke tests passed"
