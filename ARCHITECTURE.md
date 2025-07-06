# AI Domain Expert Chatbot - Technical Architecture

## Overview
A production-ready AI chatbot system deployed on Kubernetes that provides domain-specific question answering using Retrieval-Augmented Generation (RAG) architecture with private document knowledge base.

## System Architecture

### High-Level Architecture
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Browser  │────│  Kubernetes      │────│  External APIs  │
│   (Streamlit)   │    │  Cluster         │    │  (Groq/OpenAI)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                    ┌─────────┼─────────┐
                    │         │         │
            ┌───────▼───┐ ┌───▼───┐ ┌───▼────┐
            │ Chatbot   │ │ Redis │ │ChromaDB│
            │   Pods    │ │ Cache │ │Vector  │
            │           │ │       │ │   DB   │
            └───────────┘ └───────┘ └────────┘
```

### Kubernetes Architecture
```
Namespace: debot
├── Deployments
│   ├── chatbot (2 replicas)
│   ├── redis (1 replica)
│   └── chromadb (1 replica)
├── Services
│   ├── chatbot-service (LoadBalancer)
│   ├── redis-service (ClusterIP)
│   └── chromadb-service (ClusterIP)
├── ConfigMaps
│   └── debot-config (Environment variables)
├── Secrets
│   └── debot-secrets (API keys)
└── Volumes
    ├── redis-data (PersistentVolume)
    ├── chromadb-data (PersistentVolume)
    └── documents-data (EmptyDir)
```

## AI/ML Architecture

### RAG (Retrieval-Augmented Generation) Pipeline
```
Document Ingestion → Embedding → Vector Storage → Query → LLM → Response
      │                │            │           │       │        │
   ┌──▼──┐         ┌────▼────┐  ┌────▼────┐ ┌───▼───┐ ┌─▼─┐ ┌───▼───┐
   │PDFs │         │Sentence │  │ChromaDB │ │Vector │ │LLM│ │Context│
   │Docs │────────▶│Transform│─▶│Vector   │◀┤Search │◀┤   │ │+Query │
   │Web  │         │Embedder │  │Database │ │Top-K  │ │   │ │       │
   └─────┘         └─────────┘  └─────────┘ └───────┘ └───┘ └───────┘
```

### AI Components

#### 1. Document Processing Pipeline
- **PDF Parser**: Extracts text from PDF documents with caching
- **Document Loader**: Processes Markdown, TXT, DOCX files
- **Web Crawler**: Async crawling with robots.txt compliance
- **Excel Processor**: Converts test cases to searchable format

#### 2. Embedding System
- **Model**: SentenceTransformers 'all-MiniLM-L6-v2'
- **Caching**: Redis-based embedding cache (TTL: 24h)
- **Vector Dimensions**: 384-dimensional embeddings
- **Storage**: ChromaDB vector database with metadata

#### 3. Large Language Model Integration
- **Primary LLM**: Groq (llama3-8b-8192)
- **Fallback**: OpenAI GPT-4/3.5-turbo
- **Provider Pattern**: Pluggable LLM providers
- **Context Window**: 8192 tokens
- **Temperature**: 0.2 (focused responses)

#### 4. Retrieval System
- **Similarity Search**: Cosine similarity in vector space
- **Top-K Retrieval**: 5 most relevant documents
- **Metadata Filtering**: Source type filtering (docs/web/all)
- **Context Assembly**: Combines retrieved docs with user query

## Kubernetes Implementation

### Container Strategy
```dockerfile
# Multi-stage build for optimization
FROM python:3.11-slim AS base
# System dependencies
RUN apt-get update && apt-get install -y gcc g++

# Application layer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "streamlit_app.py", "--server.address", "0.0.0.0"]
```

### Service Mesh Architecture
- **Chatbot Service**: LoadBalancer (external access)
- **Redis Service**: ClusterIP (internal cache)
- **ChromaDB Service**: ClusterIP (internal vector DB)
- **Inter-service Communication**: DNS-based service discovery

### Data Persistence Strategy
- **Redis**: PersistentVolume for cache persistence
- **ChromaDB**: PersistentVolume for vector data
- **Documents**: Volume mounts for document access
- **Backup Strategy**: Volume snapshots (future)

### Scaling Configuration
```yaml
# Horizontal Pod Autoscaler (future)
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: chatbot-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: chatbot
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## Performance Optimizations

### Caching Strategy
1. **Embedding Cache**: Redis stores computed embeddings
2. **Response Cache**: Caches LLM responses for identical queries
3. **Document Cache**: Prevents re-processing unchanged documents
4. **Vector Cache**: ChromaDB internal caching

### Startup Optimization
1. **Content Hash Comparison**: Skips re-indexing unchanged documents
2. **Incremental Loading**: Only processes new/modified files
3. **Persistent Volumes**: Maintains indexed data across restarts
4. **Connection Pooling**: Reuses database connections

## Security Architecture

### Secrets Management
- **API Keys**: Kubernetes Secrets (base64 encoded)
- **Environment Variables**: ConfigMaps for non-sensitive config
- **Network Policies**: Pod-to-pod communication restrictions (future)
- **RBAC**: Role-based access control (future)

### Data Security
- **In-Transit**: TLS for external API calls
- **At-Rest**: Encrypted persistent volumes (future)
- **Access Control**: Namespace isolation
- **Audit Logging**: Kubernetes audit logs (future)

## Monitoring & Observability

### Health Checks
```yaml
livenessProbe:
  httpGet:
    path: /_stcore/health
    port: 8501
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /_stcore/health
    port: 8501
  initialDelaySeconds: 5
  periodSeconds: 5
```

### Metrics Collection (Future)
- **Prometheus**: Metrics scraping
- **Grafana**: Visualization dashboards
- **Custom Metrics**: Query response times, accuracy scores
- **Resource Metrics**: CPU, memory, storage usage

## Deployment Pipeline

### CI/CD Workflow
```bash
# Build & Deploy Script
1. Docker build -t debot:latest .
2. kubectl apply -f k8s/
3. kubectl wait --for=condition=ready pod -l app=chatbot
4. Data synchronization to pods
5. Health check verification
```

### Environment Management
- **Development**: Local Docker Compose
- **Staging**: Kubernetes cluster (reduced replicas)
- **Production**: Kubernetes cluster (full scaling)

## Technology Stack

### Core Technologies
- **Container Platform**: Docker + Kubernetes
- **Application Framework**: Streamlit (Python)
- **Vector Database**: ChromaDB
- **Cache Layer**: Redis
- **LLM Provider**: Groq (Llama 3)
- **Embedding Model**: SentenceTransformers

### Infrastructure
- **Orchestration**: Kubernetes
- **Service Mesh**: Native K8s services
- **Storage**: Persistent Volumes
- **Networking**: ClusterIP/LoadBalancer services
- **Configuration**: ConfigMaps + Secrets

## Future Enhancements

### AI/ML Improvements
- [ ] Fine-tuned domain-specific embeddings
- [ ] Multi-modal document processing (images, tables)
- [ ] Conversation memory and context tracking
- [ ] Answer quality scoring and feedback loop
- [ ] A/B testing for different LLM providers

### Kubernetes Enhancements
- [ ] Horizontal Pod Autoscaling
- [ ] Vertical Pod Autoscaling
- [ ] Network Policies for security
- [ ] Ingress Controller with TLS
- [ ] Service Mesh (Istio) integration
- [ ] GitOps deployment (ArgoCD)

### Operational Improvements
- [ ] Comprehensive monitoring stack
- [ ] Automated backup and disaster recovery
- [ ] Multi-environment deployment pipeline
- [ ] Performance testing and optimization
- [ ] Cost optimization and resource management

## Conclusion

This architecture provides a production-ready, scalable AI chatbot system that combines modern containerization practices with advanced AI/ML capabilities. The Kubernetes deployment ensures high availability, scalability, and maintainability while the RAG architecture delivers accurate, context-aware responses from private document collections.

The system is designed for enterprise deployment with considerations for security, monitoring, and operational excellence built into the foundation.