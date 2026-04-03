#!/bin/bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Blue-Green Deployment Script
# Called by GitHub Actions after image push
# Usage: bash deploy.sh <image_tag>
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

set -e

IMAGE="larexx40/internal-utility-service"
TAG="${1:-latest}"
FULL_IMAGE="${IMAGE}:${TAG}"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Starting Blue-Green Deployment"
echo "Image: ${FULL_IMAGE}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Step 1: Pull the new image
echo "[1/6] Pulling new image..."
docker pull "${FULL_IMAGE}"

# Step 2: Start Green on port 5001
echo "[2/6] Starting Green container..."
docker stop green 2>/dev/null || true
docker rm green 2>/dev/null || true
docker run -d \
    --name green \
    --restart=always \
    -p 5001:5000 \
    -e APP_ENV=production \
    "${FULL_IMAGE}"

# Step 3: Wait and health check Green
echo "[3/6] Checking Green health..."
sleep 10
HEALTH=$(curl -s -o /dev/null -w "%{http_code}" \
    http://localhost:5001/health)

if [ "${HEALTH}" != "200" ]; then
    echo "ERROR: Green failed health check (HTTP ${HEALTH})"
    echo "Rolling back — removing Green, Blue stays active"
    docker stop green && docker rm green
    exit 1
fi

echo "Green is healthy (HTTP ${HEALTH})"

# Step 4: Switch Nginx to Green
echo "[4/6] Switching Nginx to Green..."
sudo sed -i \
    's/proxy_pass http:\/\/localhost:5000/proxy_pass http:\/\/localhost:5001/' \
    /etc/nginx/sites-available/capstone2
sudo nginx -t && sudo nginx -s reload

# Step 5: Stop Blue
echo "[5/6] Stopping Blue..."
docker stop blue 2>/dev/null || true
docker rm blue 2>/dev/null || true

# Step 6: Rename Green to Blue for next cycle
echo "[6/6] Renaming Green to Blue..."
docker stop green
docker rm green
docker run -d \
    --name blue \
    --restart=always \
    -p 5000:5000 \
    -e APP_ENV=production \
    "${FULL_IMAGE}"

sudo sed -i \
    's/proxy_pass http:\/\/localhost:5001/proxy_pass http:\/\/localhost:5000/' \
    /etc/nginx/sites-available/capstone2
sudo nginx -s reload

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Deployment complete!"
echo "Running: ${FULL_IMAGE}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
