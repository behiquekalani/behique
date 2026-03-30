#!/bin/bash
# Deploy Hogar Ana Gabriel to Naboria
# Run from Ceiba: bash projects/hogar-ana-gabriel/deploy/deploy.sh

NABORIA="kalani@192.168.0.152"
REMOTE_DIR="/var/www/hogar-ana-gabriel"
LOCAL_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== Deploying Hogar Ana Gabriel to Naboria ==="

# Create remote directory
ssh $NABORIA "sudo mkdir -p $REMOTE_DIR && sudo chown kalani:kalani $REMOTE_DIR"

# Sync files (exclude deploy folder and dev files)
rsync -avz --delete \
  --exclude='deploy/' \
  --exclude='logo.html' \
  --exclude='.DS_Store' \
  "$LOCAL_DIR/" \
  "$NABORIA:$REMOTE_DIR/"

# Copy nginx config
scp "$LOCAL_DIR/deploy/nginx.conf" "$NABORIA:/tmp/hogar-ana-gabriel.conf"
ssh $NABORIA "sudo mv /tmp/hogar-ana-gabriel.conf /etc/nginx/sites-available/hogar-ana-gabriel && \
  sudo ln -sf /etc/nginx/sites-available/hogar-ana-gabriel /etc/nginx/sites-enabled/ && \
  sudo nginx -t && sudo systemctl reload nginx"

echo "=== Done. Live at http://hogaranagabriel.behike.store ==="
