#!/bin/bash
# Deploy all client sites to Naboria
# Usage: bash deploy-all.sh
# Requires: Naboria online at 192.168.0.152, SSH key configured

NABORIA="kalani@192.168.0.152"
REPO="$(cd "$(dirname "$0")" && pwd)"

echo "============================================"
echo "  BEHIKE DEPLOY - All Sites to Naboria"
echo "============================================"

# Check Naboria is online
echo -n "Checking Naboria... "
if ssh -o ConnectTimeout=5 $NABORIA 'echo ok' 2>/dev/null; then
    echo "ONLINE"
else
    echo "OFFLINE - Turn on Naboria first"
    exit 1
fi

# Install nginx if not present
echo -n "Checking nginx... "
ssh $NABORIA 'which nginx > /dev/null 2>&1' && echo "installed" || {
    echo "installing..."
    ssh $NABORIA 'sudo apt-get update -qq && sudo apt-get install -y -qq nginx certbot python3-certbot-nginx'
}

echo ""
echo "--- Deploying Innova Barber ---"
ssh $NABORIA "sudo mkdir -p /var/www/innova-barber && sudo chown kalani:kalani /var/www/innova-barber"
rsync -avz --delete \
    --exclude='deploy/' \
    --exclude='.DS_Store' \
    --exclude='*.html' \
    "$REPO/projects/innova-barber/" "$NABORIA:/var/www/innova-barber/"
# Copy index.html separately (we want it)
rsync -avz "$REPO/projects/innova-barber/index.html" "$NABORIA:/var/www/innova-barber/"
scp "$REPO/projects/innova-barber/deploy/nginx.conf" "$NABORIA:/tmp/innova-barber.conf"
ssh $NABORIA "sudo mv /tmp/innova-barber.conf /etc/nginx/sites-available/innova-barber && \
    sudo ln -sf /etc/nginx/sites-available/innova-barber /etc/nginx/sites-enabled/"
echo "Innova Barber: DEPLOYED"

echo ""
echo "--- Deploying Hogar Ana Gabriel ---"
ssh $NABORIA "sudo mkdir -p /var/www/hogar-ana-gabriel && sudo chown kalani:kalani /var/www/hogar-ana-gabriel"
rsync -avz --delete \
    --exclude='deploy/' \
    --exclude='logo.html' \
    --exclude='.DS_Store' \
    "$REPO/projects/hogar-ana-gabriel/" "$NABORIA:/var/www/hogar-ana-gabriel/"
scp "$REPO/projects/hogar-ana-gabriel/deploy/nginx.conf" "$NABORIA:/tmp/hogar-ana-gabriel.conf"
ssh $NABORIA "sudo mv /tmp/hogar-ana-gabriel.conf /etc/nginx/sites-available/hogar-ana-gabriel && \
    sudo ln -sf /etc/nginx/sites-available/hogar-ana-gabriel /etc/nginx/sites-enabled/"
echo "Hogar Ana Gabriel: DEPLOYED"

echo ""
echo "--- Testing nginx config ---"
ssh $NABORIA 'sudo nginx -t' && {
    ssh $NABORIA 'sudo systemctl reload nginx'
    echo "nginx: RELOADED"
} || {
    echo "nginx: CONFIG ERROR - check manually"
    exit 1
}

echo ""
echo "============================================"
echo "  DEPLOY COMPLETE"
echo "============================================"
echo "  Innova Barber:      http://innovabarber.behike.store"
echo "  Hogar Ana Gabriel:  http://hogaranagabriel.behike.store"
echo ""
echo "  Next: Configure DNS A records pointing to Naboria's IP"
echo "  Next: Run certbot for SSL:"
echo "    ssh $NABORIA 'sudo certbot --nginx -d innovabarber.behike.store -d hogaranagabriel.behike.store'"
echo "============================================"
