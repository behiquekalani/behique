#!/usr/bin/env bash
#
# Send a fake Gumroad sale webhook to the local server for testing.
#
# Usage: ./test_webhook.sh
#

echo "Sending fake Gumroad sale webhook to localhost:8097..."
echo ""

curl -s -X POST http://localhost:8097/webhook/gumroad \
  -H "Content-Type: application/json" \
  -d '{
    "seller_id": "test-seller-123",
    "product_id": "test-product-456",
    "product_name": "Behike OS Test Product",
    "price": "97.00",
    "email": "test@example.com",
    "sale_timestamp": "'"$(date -u +%Y-%m-%dT%H:%M:%SZ)"'",
    "is_recurring_charge": "false",
    "url_params": {},
    "ip_country": "PR"
  }' | python3 -m json.tool 2>/dev/null || echo "(raw response above)"

echo ""
echo "Check health: curl -s http://localhost:8097/webhook/status | python3 -m json.tool"
