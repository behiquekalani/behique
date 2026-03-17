#!/bin/bash
# ============================================
# Naboria — SSH Remote Access Setup
# Sets up your Mac to accept SSH connections
# from iPhone (Termius/Blink Shell)
# ============================================

set -e

echo ""
echo "╔══════════════════════════════════════╗"
echo "║   NABORIA — Remote Access Setup     ║"
echo "║   SSH into Mac from iPhone          ║"
echo "╚══════════════════════════════════════╝"
echo ""

# Step 1: Check if Remote Login is already enabled
echo "[1/4] Checking Remote Login (SSH) status..."
SSH_STATUS=$(sudo systemsetup -getremotelogin 2>/dev/null || echo "unknown")

if echo "$SSH_STATUS" | grep -qi "on"; then
  echo "  ✓ Remote Login is already ON"
else
  echo "  ✗ Remote Login is OFF"
  echo "  → Enabling Remote Login..."
  sudo systemsetup -setremotelogin on
  echo "  ✓ Remote Login enabled"
fi

# Step 2: Get network info
echo ""
echo "[2/4] Getting network info..."
LOCAL_IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || echo "unknown")
HOSTNAME=$(hostname)
USERNAME=$(whoami)

echo "  ✓ Local IP:  $LOCAL_IP"
echo "  ✓ Hostname:  $HOSTNAME"
echo "  ✓ Username:  $USERNAME"

# Step 3: Create SSH config for easier access
echo ""
echo "[3/4] Setting up SSH config..."

mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Create authorized_keys if it doesn't exist
if [ ! -f ~/.ssh/authorized_keys ]; then
  touch ~/.ssh/authorized_keys
  chmod 600 ~/.ssh/authorized_keys
  echo "  ✓ Created ~/.ssh/authorized_keys"
else
  echo "  ✓ authorized_keys exists"
fi

# Step 4: Print connection info
echo ""
echo "[4/4] Setup complete!"
echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║   CONNECT FROM iPHONE                       ║"
echo "╠══════════════════════════════════════════════╣"
echo "║                                              ║"
echo "║  1. Install Termius (free) from App Store    ║"
echo "║                                              ║"
echo "║  2. Create new host:                         ║"
echo "║     Host:     $LOCAL_IP"
echo "║     Username: $USERNAME"
echo "║     Port:     22                             ║"
echo "║     Auth:     Your Mac password              ║"
echo "║                                              ║"
echo "║  3. Connect, then run:                       ║"
echo "║     cd ~/behique && claude                   ║"
echo "║                                              ║"
echo "╠══════════════════════════════════════════════╣"
echo "║   FOR KEY-BASED AUTH (no password):          ║"
echo "║                                              ║"
echo "║  In Termius: Settings → Keys → Generate      ║"
echo "║  Copy the public key, then on Mac run:       ║"
echo "║  echo 'KEY' >> ~/.ssh/authorized_keys        ║"
echo "║                                              ║"
echo "╠══════════════════════════════════════════════╣"
echo "║   QUICK TEST (from another terminal):        ║"
echo "║   ssh $USERNAME@$LOCAL_IP                    ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# Save connection info to a file for reference
cat > ~/.ssh/naboria-connection.txt << CONN
# Naboria — SSH Connection Info
# Generated: $(date)
#
# Local IP:  $LOCAL_IP
# Hostname:  $HOSTNAME
# Username:  $USERNAME
# Port:      22
#
# From iPhone (Termius):
#   Host: $LOCAL_IP
#   User: $USERNAME
#   Port: 22
#
# From terminal:
#   ssh $USERNAME@$LOCAL_IP
#
# Then run:
#   cd ~/behique && claude
CONN

echo "Connection info saved to ~/.ssh/naboria-connection.txt"
echo ""
echo "Naboria daca. 🕷️"
