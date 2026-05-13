#!/bin/bash

set -e

echo "☁️  Deploying LLM Health Monitor to Azure Kubernetes Service..."

# Configuration
RESOURCE_GROUP="llm-obs-rg"
CLUSTER_NAME="llm-obs-cluster"
LOCATION="eastus"
ACR_NAME="llmobsacr"  # Must be globally unique
NODE_COUNT=2
NODE_SIZE="Standard_D2s_v3"

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI not found. Please install it first."
    echo "   Visit: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

echo "✅ Azure CLI found"

# Check if logged in
if ! az account show &> /dev/null; then
    echo "🔐 Please login to Azure..."
    az login
fi

echo "✅ Logged in to Azure"

# Create resource group
echo "📦 Creating resource group..."
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create Azure Container Registry
echo "🐳 Creating Azure Container Registry..."
az acr create --resource-group $RESOURCE_GROUP \
    --name $ACR_NAME \
    --sku Basic

# Create AKS cluster
echo "☸️  Creating AKS cluster (this may take 10-15 minutes)..."
az aks create \
    --resource-group $RESOURCE_GROUP \
    --name $CLUSTER_NAME \
    --node-count $NODE_COUNT \
    --node-vm-size $NODE_SIZE \
    --enable-managed-identity \
    --attach-acr $ACR_NAME \
    --generate-ssh-keys

# Get AKS credentials
echo "🔑 Getting AKS credentials..."
az aks get-credentials --resource-group $RESOURCE_GROUP --name $CLUSTER_NAME

# Build and push images
echo "🏗️  Building and pushing Docker images..."

# Build llama.cpp image
cd ../llamacpp
docker build -t $ACR_NAME.azurecr.io/llamacpp-custom:latest .
az acr login --name $ACR_NAME
docker push $ACR_NAME.azurecr.io/llamacpp-custom:latest

# Build monitor image
cd ../monitor
docker build -t $ACR_NAME.azurecr.io/llm-monitor:latest .
docker push $ACR_NAME.azurecr.io/llm-monitor:latest

cd ..

# Update K8s manifests with ACR image names
echo "📝 Updating Kubernetes manifests..."
sed -i "s|<your-registry>|$ACR_NAME.azurecr.io|g" k8s/llamacpp-deployment.yaml
sed -i "s|<your-registry>|$ACR_NAME.azurecr.io|g" k8s/monitor-deployment.yaml

# Deploy to Kubernetes
echo "🚀 Deploying to Kubernetes..."
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/llamacpp-deployment.yaml
kubectl apply -f k8s/monitor-deployment.yaml
kubectl apply -f k8s/prometheus-deployment.yaml
kubectl apply -f k8s/grafana-deployment.yaml

# Wait for deployments
echo "⏳ Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=300s \
    deployment/llamacpp deployment/monitor deployment/prometheus deployment/grafana \
    -n llm-obs

# Get external IPs
echo ""
echo "🎉 Deployment complete!"
echo ""
echo "📊 Getting service endpoints..."
echo ""

kubectl get services -n llm-obs

echo ""
echo "⏳ Waiting for LoadBalancer IPs (this may take a few minutes)..."
echo ""

# Wait for external IPs
for service in monitor prometheus grafana; do
    echo "Waiting for $service external IP..."
    kubectl wait --for=jsonpath='{.status.loadBalancer.ingress}' \
        service/$service -n llm-obs --timeout=300s || true
done

echo ""
echo "✅ All services deployed!"
echo ""
echo "📊 Access your services:"
echo ""

MONITOR_IP=$(kubectl get service monitor -n llm-obs -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
PROMETHEUS_IP=$(kubectl get service prometheus -n llm-obs -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
GRAFANA_IP=$(kubectl get service grafana -n llm-obs -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

echo "  - Monitor:    http://$MONITOR_IP"
echo "  - Prometheus: http://$PROMETHEUS_IP:9090"
echo "  - Grafana:    http://$GRAFANA_IP (admin/admin)"
echo ""
echo "🔍 Check pod status:"
echo "  kubectl get pods -n llm-obs"
echo ""
echo "📋 View logs:"
echo "  kubectl logs -f deployment/monitor -n llm-obs"
echo ""
echo "🗑️  To delete everything:"
echo "  az group delete --name $RESOURCE_GROUP --yes --no-wait"

