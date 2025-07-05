#!/bin/bash

echo "🚀 Deploying Debot to Kind Kubernetes..."

# Create Kind cluster
echo "📦 Creating Kind cluster..."
kind create cluster --config=kind-config.yaml

# Build Docker image and load into Kind
echo "🔨 Building Docker image..."
docker build -t debot:latest .

echo "📥 Loading image into Kind cluster..."
kind load docker-image debot:latest --name debot

# Deploy to Kubernetes
echo "☸️ Deploying to Kubernetes..."
kubectl apply -f k8s/

# Wait for deployments
echo "⏳ Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/redis -n debot
kubectl wait --for=condition=available --timeout=300s deployment/chromadb -n debot
kubectl wait --for=condition=available --timeout=300s deployment/postgres -n debot
kubectl wait --for=condition=available --timeout=300s deployment/chatbot -n debot

# Get service info
echo "✅ Deployment complete!"
echo ""
echo "📊 Service Status:"
kubectl get pods -n debot
echo ""
echo "🌐 Access the application:"
echo "Streamlit UI: http://localhost:8501"
echo ""
echo "🔧 Useful commands:"
echo "  kubectl logs -f deployment/chatbot -n debot"
echo "  kubectl get pods -n debot"
echo "  kubectl port-forward svc/chatbot-service 8501:8501 -n debot"