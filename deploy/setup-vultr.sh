#!/bin/bash
# Run this on a fresh Vultr Ubuntu 22.04+ VPS
# Usage: ssh root@YOUR_IP 'bash -s' < deploy/setup-vultr.sh

set -euo pipefail

echo "=== Installing Docker ==="
apt-get update
apt-get install -y ca-certificates curl
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" > /etc/apt/sources.list.d/docker.list
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

echo "=== Cloning repo ==="
apt-get install -y git
cd /opt
git clone https://github.com/gopalakrishnans/myrepo.git clearprice
cd clearprice
git checkout claude/healthcare-price-transparency-HvUVZ

echo "=== Building and starting ==="
docker compose up -d --build

echo ""
echo "=== Done! ==="
echo "App is running at http://$(curl -s ifconfig.me)"
echo ""
echo "Useful commands:"
echo "  cd /opt/clearprice"
echo "  docker compose logs -f        # View logs"
echo "  docker compose restart         # Restart services"
echo "  docker compose down && docker compose up -d --build  # Rebuild"
