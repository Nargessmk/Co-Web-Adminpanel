#!/bin/bash
set -e

echo "========================================="
echo "  Cloudland Docker Deployment Script"
echo "========================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Installing..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
fi

# Check if Docker Compose is available
if ! docker compose version &> /dev/null; then
    echo "Docker Compose is not installed. Installing..."
    apt-get update && apt-get install -y docker-compose-plugin
fi

# Check for .env file
if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "Please edit .env with your configuration before starting!"
    exit 1
fi

echo ""
echo "Step 1: Building Docker images..."
docker compose build

echo ""
echo "Step 2: Starting services..."
docker compose up -d

echo ""
echo "Step 3: Checking service status..."
sleep 5
docker compose ps

echo ""
echo "========================================="
echo "  Deployment Complete!"
echo "========================================="
echo ""
echo "Frontend:  http://localhost"
echo "Backend:   http://localhost:4000"
echo "Gateway:   http://localhost:4001"
echo ""
echo "Useful commands:"
echo "  View logs:    docker compose logs -f"
echo "  Stop:         docker compose down"
echo "  Restart:      docker compose restart"
echo "  Rebuild:      docker compose up -d --build"
echo ""
