#!/bin/bash
# Deploy Innova Barber to Naboria
# Run from Ceiba: bash projects/innova-barber/deploy/deploy.sh

NABORIA="kalani@192.168.0.152"
REMOTE_DIR="/var/www/innova-barber"
LOCAL_DIR="$(dirname "$0")/.."

echo "=== Deploying Innova Barber to Naboria ==="

# Create remote directory
ssh $NABORIA "sudo mkdir -p $REMOTE_DIR && sudo chown kalani:kalani $REMOTE_DIR"

# Sync files
rsync -avz --delete \
  "$LOCAL_DIR/index.html" \
  "$LOCAL_DIR/images/" \
  "$NABORIA:$REMOTE_DIR/"

# Copy nginx config
scp "$LOCAL_DIR/deploy/nginx.conf" "$NABORIA:/tmp/innova-barber.conf"
ssh $NABORIA "sudo mv /tmp/innova-barber.conf /etc/nginx/sites-available/innova-barber && \
  sudo ln -sf /etc/nginx/sites-available/innova-barber /etc/nginx/sites-enabled/ && \
  sudo nginx -t && sudo systemctl reload nginx"

echo "=== Done. Live at http://innovabarber.behike.store ==="
