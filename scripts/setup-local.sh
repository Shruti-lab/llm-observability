#!/bin/bash

set -e

echo "🚀 Setting up LLM Health Monitor with llama.cpp..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

echo "✅ Docker is running"

# Check if docker compose is available
if ! command -v docker compose &> /dev/null; then
    echo "❌ docker compose not found. Please install it."
    exit 1
fi

echo "✅ docker compose found"

# Navigate to project root
cd "$(dirname "$0")/.."

# Create .env file if it doesn't exist
if [ ! -f monitor/.env ]; then
    echo "📝 Creating monitor/.env file..."
    cat > monitor/.env << EOF
LLM_URL=http://llamacpp:8080
LLM_MODEL=llama-3.2-1b-instruct
MONITOR_INTERVAL=30
TEST_PROMPT=What is 2+2?
EXPECTED_ANSWER=4
LOG_LEVEL=INFO
EOF
    echo "✅ Created monitor/.env"
fi

# Download model if not exists
echo "📥 Checking for model..."
if [ ! -f models/llama-3.2-1b-instruct-q4_k_m.gguf ]; then
    echo "Model not found. Downloading..."
    bash scripts/download-model.sh
else
    echo "✅ Model already exists"
fi

# Start services
echo "🐳 Starting Docker containers..."
docker compose up -d

echo "⏳ Waiting for services to be healthy..."
sleep 15

# Check if llama.cpp is running
if docker compose ps | grep -q "llamacpp.*Up"; then
    echo "✅ llama.cpp server is running"
else
    echo "⚠️  llama.cpp container not running. Check logs with: docker compose logs llamacpp"
fi

# Wait for monitor to be ready
echo "⏳ Waiting for monitor service..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Monitor service is healthy"
        break
    fi
    sleep 2
done

# Test LLM endpoint
echo "🧪 Testing LLM endpoint..."
if curl -s http://localhost:8080/health > /dev/null 2>&1; then
    echo "✅ llama.cpp server is responding"
else
    echo "⚠️  llama.cpp server not responding yet. It may still be loading the model..."
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📊 Access your services:"
echo "  - Monitor API:    http://localhost:8000"
echo "  - llama.cpp API:  http://localhost:8080"
echo "  - Prometheus:     http://localhost:9090"
echo "  - Grafana:        http://localhost:3000 (admin/admin)"
echo ""
echo "📈 View metrics:"
echo "  curl http://localhost:8000/metrics"
echo ""
echo "🧪 Test LLM query:"
echo "  curl -X POST 'http://localhost:8000/api/query?prompt=What%20is%202%2B2%3F'"
echo ""
echo "🔍 Check logs:"
echo "  docker compose logs -f monitor"
echo "  docker compose logs -f llamacpp"
echo ""
echo "🛑 Stop services:"
echo "  docker compose down"

 
