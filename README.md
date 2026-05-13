# LLM Health Monitor

A production-ready observability system for monitoring LLM inference latency and response quality in real-time using Docker, Prometheus, and Grafana.

## 🎯 Project Overview

This system continuously monitors an LLM service (Ollama/llama.cpp), tracks key metrics, and visualizes them in Grafana dashboards. Perfect for understanding LLM performance characteristics and detecting issues early.

## 🏗️ Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Ollama    │◄─────│   Monitor    │─────►│ Prometheus  │
│  (LLM API)  │      │  (FastAPI)   │      │  (Metrics)  │
└─────────────┘      └──────────────┘      └─────────────┘
                            │                      │
                            │                      ▼
                            │               ┌─────────────┐
                            └──────────────►│   Grafana   │
                                            │ (Dashboard) │
                                            └─────────────┘
```

**Components:**
- **Ollama**: Runs small LLM models (llama3.2:1b)
- **Monitor**: FastAPI service that queries LLM every 30s and exposes Prometheus metrics
- **Prometheus**: Scrapes and stores time-series metrics
- **Grafana**: Visualizes metrics with pre-configured dashboards

## 📊 Metrics Tracked

| Metric | Type | Description |
|--------|------|-------------|
| `llm_requests_total` | Counter | Total LLM requests (success/failure) |
| `llm_request_duration_seconds` | Histogram | Request latency distribution (p50, p95, p99) |
| `llm_response_quality` | Gauge | Response quality score (0.0-1.0) |
| `llm_tokens_count` | Gauge | Tokens generated per request |
| `llm_errors_total` | Counter | Errors by type (timeout, http_500, etc.) |

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- 4GB RAM minimum
- 10GB disk space

### Local Development

1. **Clone and navigate to project:**
```bash
cd llm-obs
```

2. **Start all services:**
```bash
docker compose up -d
```

3. **Pull the LLM model (first time only):**
```bash
docker exec -it llm-obs-ollama ollama pull llama3.2:1b
```

4. **Access the services:**
- Monitor API: http://localhost:8000
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

5. **View metrics:**
```bash
# Check monitor health
curl http://localhost:8000/health

# View raw Prometheus metrics
curl http://localhost:8000/metrics

# Query LLM manually
curl -X POST "http://localhost:8000/api/query?prompt=What%20is%202%2B2%3F"
```

### Verify Setup

1. **Check all containers are running:**
```bash
docker compose ps
```

2. **View monitor logs:**
```bash
docker compose logs -f monitor
```

3. **Open Grafana dashboard:**
   - Go to http://localhost:3000
   - Login: admin/admin
   - Navigate to "LLM Health Monitor" dashboard

## 📁 Project Structure

```
llm-obs/
├── monitor/                    # FastAPI monitoring service
│   ├── app/
│   │   ├── main.py            # FastAPI app + APScheduler
│   │   ├── config.py          # Configuration management
│   │   ├── llm_client.py      # LLM query logic
│   │   └── metrics.py         # Prometheus metrics definitions
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env
├── prometheus/
│   └── prometheus.yml         # Prometheus scrape config
├── grafana/
│   ├── provisioning/
│   │   ├── datasources/       # Auto-configure Prometheus
│   │   └── dashboards/        # Auto-load dashboards
│   └── dashboards/
│       └── llm-health-monitor.json
├── k8s/                       # Kubernetes manifests (for Azure)
├── docker compose.yaml
└── README.md
```

## 🔧 Configuration

### Environment Variables

Edit `monitor/.env`:

```env
LLM_URL=http://ollama:11434
LLM_MODEL=llama3.2:1b
MONITOR_INTERVAL=30
TEST_PROMPT=What is 2+2?
EXPECTED_ANSWER=4
LOG_LEVEL=INFO
```

### Prometheus Scrape Interval

Edit `prometheus/prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'llm-monitor'
    scrape_interval: 10s  # Adjust as needed
```

## 🐛 Troubleshooting

### Ollama not responding
```bash
# Check Ollama logs
docker compose logs ollama

# Restart Ollama
docker compose restart ollama

# Verify model is pulled
docker exec -it llm-obs-ollama ollama list
```

### Monitor service errors
```bash
# Check monitor logs
docker compose logs monitor

# Restart monitor
docker compose restart monitor
```

### Grafana dashboard not showing data
1. Check Prometheus is scraping: http://localhost:9090/targets
2. Verify metrics endpoint: http://localhost:8000/metrics
3. Check Grafana datasource: Settings → Data Sources → Prometheus

## 📈 Grafana Dashboard

The pre-configured dashboard shows:
- **Request Rate**: Requests per second over time
- **Latency**: p50, p95, p99 percentiles
- **Quality Score**: Response correctness (0-1)
- **Token Count**: Tokens generated per request
- **Error Rate**: Errors per second by type
- **Success Rate**: Overall success percentage

## ☁️ Azure Deployment

### Prerequisites
- Azure CLI installed
- Azure subscription with credits
- kubectl installed

### Deploy to AKS

1. **Create AKS cluster:**
```bash
az aks create \
  --resource-group llm-obs-rg \
  --name llm-obs-cluster \
  --node-count 2 \
  --node-vm-size Standard_D2s_v3 \
  --enable-managed-identity
```

2. **Get credentials:**
```bash
az aks get-credentials --resource-group llm-obs-rg --name llm-obs-cluster
```

3. **Deploy services:**
```bash
kubectl apply -f k8s/
```

4. **Get external IPs:**
```bash
kubectl get services
```

## 🎓 Learning Outcomes

By building this project, you've learned:
- ✅ FastAPI with background tasks (APScheduler)
- ✅ Prometheus metrics exposition and scraping
- ✅ Grafana dashboard creation and provisioning
- ✅ Docker Compose for multi-service orchestration
- ✅ Kubernetes deployment patterns
- ✅ Observability best practices
- ✅ LLM monitoring and quality evaluation

## 📝 Resume Line

> "Built an LLM observability system using Docker, Grafana, and Prometheus — monitoring inference latency and response quality in real time."

## 🤝 Contributing

Feel free to open issues or submit PRs for improvements!

## 📄 License

MIT License