#!/bin/bash
set -e

echo "Refreshing documents using shared persistent volume..."

# Get first pod name (all pods share same volume)
POD_NAME=$(kubectl get pods -n debot -l app=chatbot -o jsonpath='{.items[0].metadata.name}')
echo "Using pod: $POD_NAME"

# Clear existing documents (affects all pods)
echo "Clearing existing documents from shared volume..."
kubectl exec $POD_NAME -n debot -- rm -rf /app/data/*

# Copy new documents to proper subdirectories (visible to all pods)
echo "Copying new documents to shared volume with proper structure..."
# Create subdirectories
kubectl exec $POD_NAME -n debot -- mkdir -p /app/data/docs /app/data/pdfs /app/data/mds

cd data
# Copy to docs subdirectory (adjust based on your document types)
kubectl cp . "$POD_NAME:/app/data/docs/" -n debot
echo "Documents copied to /app/data/docs/"
cd ..

# Clear ChromaDB to remove old embeddings
echo "Clearing ChromaDB vector database..."
CHROMA_POD=$(kubectl get pods -n debot -l app=chromadb -o jsonpath='{.items[0].metadata.name}')
kubectl exec $CHROMA_POD -n debot -- rm -rf /chroma/chroma/*
echo "Restarting ChromaDB..."
kubectl rollout restart deployment/chromadb -n debot
kubectl rollout status deployment/chromadb -n debot

# Force re-indexing with rolling restart (no downtime)
echo "Triggering rolling restart to re-index documents..."
kubectl set env deployment/chatbot FORCE_REINDEX=true -n debot
kubectl rollout status deployment/chatbot -n debot
kubectl set env deployment/chatbot FORCE_REINDEX- -n debot

echo "Document refresh and re-indexing complete!"