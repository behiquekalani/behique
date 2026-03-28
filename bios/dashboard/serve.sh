#!/bin/bash
# Start BIOS Dashboard server
# Access at http://192.168.0.145:8092
cd "$(dirname "$0")"
echo "BIOS Dashboard at http://192.168.0.145:8092"
python3 -m http.server 8092 --bind 0.0.0.0
