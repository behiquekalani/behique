#!/bin/bash
# Behike Store Deployment Script
# Run from Ceiba to deploy landing pages to Hutia
#
# Make executable: chmod +x deploy.sh
# Usage: ./deploy.sh

set -e

HUTIA_IP="192.168.0.152"
HUTIA_USER="kalani"
SITE_DIR="/home/kalani/behike-store"
PAGES_DIR="/Users/kalani/behique/themes/behike-store/landing-pages"

echo "=== Behike Store Deployment ==="
echo "Deploying to Hutia ($HUTIA_IP)..."
echo ""

# Check if Hutia is reachable
if ! ping -c 1 -W 2 "$HUTIA_IP" > /dev/null 2>&1; then
  echo "ERROR: Hutia ($HUTIA_IP) is not reachable."
  echo "Make sure the machine is on and connected to the network."
  exit 1
fi

echo "[1/3] Creating site directory on Hutia..."
ssh "$HUTIA_USER@$HUTIA_IP" "mkdir -p $SITE_DIR"

echo "[2/3] Syncing landing pages..."
rsync -avz --delete "$PAGES_DIR/" "$HUTIA_USER@$HUTIA_IP:$SITE_DIR/"

echo "[3/3] Starting web server on Hutia..."
ssh "$HUTIA_USER@$HUTIA_IP" "
  # Kill existing server if running
  pkill -f 'python3 -m http.server 8080.*behike-store' 2>/dev/null || true
  sleep 1

  # Start new server
  cd $SITE_DIR
  nohup python3 -m http.server 8080 --bind 0.0.0.0 > /tmp/behike-store.log 2>&1 &
  echo 'Server PID:' \$!
  echo 'Server started on port 8080'
"

echo ""
echo "=== Deployment Complete ==="
echo ""
echo "Local preview:  http://$HUTIA_IP:8080"
echo "Server logs:    ssh $HUTIA_USER@$HUTIA_IP 'tail -f /tmp/behike-store.log'"
echo ""
echo "Next steps:"
echo "  1. Verify the site loads at http://$HUTIA_IP:8080"
echo "  2. Point Cloudflare tunnel to $HUTIA_IP:8080"
echo "  3. Set up the chat API on Cobo (see bridge/cobo-chatbot-instructions.md)"
