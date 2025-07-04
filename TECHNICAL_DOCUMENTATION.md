# DHHS AI Domain Expert Chatbot - Technical Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Core Components](#core-components)
4. [Data Flow](#data-flow)
5. [Implementation Details](#implementation-details)
6. [Configuration](#configuration)
7. [Deployment](#deployment)
8. [Performance & Scalability](#performance--scalability)
9. [Security](#security)
10. [Troubleshooting](#troubleshooting)

## System Overview

### Purpose
AI-powered chatbot that answers domain-specific queries using private documentation, test cases, and selected public websites. Built following IndexCopilot.ai principles for enterprise knowledge management.

### Key Features
- **Multi-source ingestion**: PDFs, Word docs, Markdown, CSV test cases, websites
- **Business knowledge extraction**: Converts test cases to business requirements
- **Contextual tagging**: Automatic categorization of content
- **Hybrid search**: Vector similarity + keyword matching
- **Multiple LLM providers**: OpenAI, Groq, OpenRouter support
- **Caching layer**: Redis for performance optimization
- **Web interface**: Streamlit-based chat UI

## Architecture

### High-Level Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Sources  │    │   Processing    │    │   Query Layer   │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • PDFs          │───▶│ • Document      │───▶│ • Vector Search │
│ • Word Docs     │    │   Loaders       │    │ • LLM Provider  │
│ • Markdown      │    │ • Text          │    │ • Response      │
│ • CSV Tests     │    │   Extraction    │    │   Generation    │
│ • Websites      │    │ • Embeddings    │    │ • Caching       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Storage       │    │   Vector DB     │    │   User Interface│
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • PostgreSQL    │    │ • ChromaDB      │    │ • Streamlit UI  │
│ • Redis Cache   │    │ • Embeddings    │    │ • CLI Interface │
│ • File System   │    │ • Metadata      │    │ • API Endpoints │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Technology Stack
- **Backend**: Python 3.11+
- **Vector Database**: ChromaDB (Docker)
- **Caching**: Redis (Docker)
- **Database**: PostgreSQL
- **Embeddings**: sentence-transformers (local)
- **LLM**: Groq (primary), OpenAI/OpenRouter (optional)
- **UI**: Streamlit
- **Containerization**: Docker Compose

## Core Components

### 1. Data Ingestion Layer (`ingest/`)

#### Document Loaders
```python
# load_docs.py - Handles .md, .txt, .docx files
def load_documents(docs_dir: str) -> List[Dict[str, str]]

# load_pdfs.py - PDF text extraction with caching
def load_pdfs(pdf_dir: str) -> List[Dict[str, str]]

# load_excel.py - CSV/Excel test case processing
def load_excel_testcases(excel_dir: str) -> List[Dict[str, str]]

# crawler.py - Async web crawling
async def crawl_websites(urls: List[str]) -> List[Dict[str, str]]
```

#### Test Case Converter
```python
# convert_csv_to_md.py - Business knowledge extraction
def convert_csv_to_md() -> None
```

### 2. Embedding & Vector Storage

#### Simple Embedding Service
```python
class SimpleEmbeddingService:
    def __init__(self):
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.chroma_client = chromadb.HttpClient()
    
    def get_embedding(self, text: str) -> List[float]
    def add_documents(self, documents: List[Dict])
    def search(self, query: str, n_results: int) -> List[Dict]
```

### 3. Query & Response Layer

#### QA Service
```python
class SimpleQAService:
    def __init__(self, embedding_service: SimpleEmbeddingService):
        self.embedding_service = embedding_service
        self.llm_provider = GroqProvider()
    
    def answer_question(self, question: str) -> Dict[str, any]
```

### 4. LLM Provider Abstraction (`providers/`)
```python
# Supports multiple LLM providers
class GroqProvider:
    async def generate_response(self, system_prompt: str, user_prompt: str) -> str

class OpenAIProvider:
    async def generate_response(self, system_prompt: str, user_prompt: str) -> str
```

### 5. Context Tagging System

#### Extensible Tagging
```python
# context_tags.py - Business domain categorization
CONTEXT_TAGS = {
    'Authentication': ['login', 'password', 'credentials'],
    'Dashboard': ['dashboard', 'landing page', 'kpi'],
    'Acquisition Management': ['acquisition', 'contract', 'procurement']
}

def get_context_tags(content_text: str) -> List[str]
```

### 6. Caching Layer (`cache_utils.py`)
```python
# Redis-based caching for performance
def cache_embedding(text: str, embedding: List[float])
def get_cached_embedding(text: str) -> Optional[List[float]]
def cache_response(question: str, response: str)
```

### 7. Database Layer (`database.py`)
```python
# PostgreSQL for metadata and chat history
class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    filename = Column(String)
    source = Column(String)
    content_hash = Column(String)

class ChatHistory(Base):
    __tablename__ = "chat_history"
    id = Column(Integer, primary_key=True)
    question = Column(Text)
    answer = Column(Text)
    timestamp = Column(DateTime)
```

## Data Flow

### 1. Document Ingestion Flow
```
Raw Documents → Text Extraction → Chunking → Embedding Generation → Vector Storage
     ↓              ↓              ↓              ↓                    ↓
  [PDF/DOCX]    [Clean Text]   [1024 chars]   [768-dim vector]   [ChromaDB]
     ↓              ↓              ↓              ↓                    ↓
  Metadata → PostgreSQL Storage ← Cache Layer ← Redis Cache ← Context Tags
```

### 2. Query Processing Flow
```
User Query → Embedding → Vector Search → Context Retrieval → LLM Generation → Response
     ↓           ↓            ↓              ↓                 ↓              ↓
[Natural Lang] [Vector]  [Top-K Docs]   [Relevant Text]   [Groq API]   [Formatted Answer]
     ↓           ↓            ↓              ↓                 ↓              ↓
Cache Check → Redis → ChromaDB Query → Context Assembly → Prompt Engineering → User
```

### 3. Test Case Processing Flow
```
CSV Test Cases → Business Knowledge Extraction → Markdown Generation → Document Ingestion
       ↓                    ↓                         ↓                      ↓
[Step Action/Expected] → [Business Rules] → [Structured MD] → [Vector Index]
       ↓                    ↓                         ↓                      ↓
Context Tagging → Domain Classification → Searchable Knowledge → Query Results
```

## Implementation Details

### Environment Configuration (`.env`)
```bash
# LLM Provider
DEFAULT_LLM_PROVIDER=groq
GROQ_API_KEY=your_groq_key
GROQ_MODEL=llama3-8b-8192

# Data Directories
PDF_DIR=./data/pdfs
DOCS_DIR=./data/docs
MDS_DIR=./data/mds
EXCEL_DIR=./data/excel

# Services
POSTGRES_HOST=localhost
POSTGRES_PORT=5434
REDIS_HOST=localhost
REDIS_PORT=6380
CHROMA_HOST=localhost
CHROMA_PORT=8008
```

### Docker Services (`docker-compose.yml`)
```yaml
services:
  redis:
    image: redis:7-alpine
    ports: ["${REDIS_PORT}:6379"]
    
  chromadb:
    image: chromadb/chroma:latest
    ports: ["${CHROMA_PORT}:8000"]
    
  postgres:
    image: postgres:15
    ports: ["${POSTGRES_PORT}:5432"]
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
```

### Application Configuration (`config.yaml`)
```yaml
crawling:
  urls_to_crawl: []
  crawl_depth: 0
  max_pages: 0

ingestion:
  chunk_size: 1024
  chunk_overlap: 200

embedding:
  model: 'all-MiniLM-L6-v2'
  batch_size: 100

retrieval:
  top_k: 5
  similarity_threshold: 0.7

llm:
  model: 'llama3-8b-8192'
  temperature: 0.2
  max_tokens: 800
```

## Configuration

### Directory Structure
```
debot/
├── ingest/                 # Data ingestion modules
│   ├── load_docs.py       # Document loaders
│   ├── load_pdfs.py       # PDF processing
│   ├── load_excel.py      # CSV/Excel handling
│   └── crawler.py         # Web crawling
├── providers/             # LLM provider abstractions
├── data/                  # Data storage
│   ├── docs/             # Word documents
│   ├── mds/              # Markdown files
│   ├── pdfs/             # PDF files
│   └── excel/            # CSV test cases
├── simple_embedding.py    # Vector operations
├── simple_qa.py          # Query processing
├── simple_main.py        # Main application
├── convert_csv_to_md.py  # Test case converter
├── context_tags.py       # Tagging system
├── cache_utils.py        # Caching utilities
├── database.py           # Database models
├── docker-compose.yml    # Container orchestration
├── config.yaml           # Application config
└── .env                  # Environment variables
```

### Key Configuration Files

#### 1. Environment Variables (`.env`)
- **LLM Provider Settings**: API keys, model selection
- **Data Directories**: Source document locations
- **Service Endpoints**: Database, cache, vector DB connections
- **Cache Settings**: TTL values for different cache types

#### 2. Application Config (`config.yaml`)
- **Ingestion Parameters**: Chunk size, overlap settings
- **Retrieval Settings**: Top-K results, similarity thresholds
- **LLM Parameters**: Temperature, max tokens, model selection
- **Web Crawling**: URLs, depth limits (currently disabled)

## Deployment

### Local Development Setup
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your settings

# 3. Start services
python start.py  # Starts Docker containers

# 4. Initialize database
python setup.py

# 5. Convert test cases (optional)
python convert_csv_to_md.py

# 6. Run application
python simple_main.py  # CLI interface
streamlit run streamlit_app.py  # Web interface
```

### Production Deployment
```bash
# 1. Container deployment
docker-compose up -d

# 2. Environment-specific configuration
# - Update .env for production settings
# - Configure external databases
# - Set up monitoring and logging

# 3. Data ingestion
python reindex_local_only.py

# 4. Application startup
python simple_main.py
```

## Performance & Scalability

### Caching Strategy
- **Embedding Cache**: Redis storage for computed embeddings (24h TTL)
- **Response Cache**: Cached LLM responses for repeated queries (1h TTL)
- **Document Cache**: Processed document content caching

### Performance Optimizations
- **Local Embeddings**: sentence-transformers eliminates API calls
- **Async Processing**: Web crawling and batch operations
- **Chunking Strategy**: Optimal 1024-character chunks with 200-char overlap
- **Vector Search**: ChromaDB optimized for similarity search

### Scalability Considerations
- **Horizontal Scaling**: Multiple application instances
- **Database Scaling**: PostgreSQL read replicas
- **Cache Scaling**: Redis clustering
- **Vector DB Scaling**: ChromaDB distributed deployment

## Security

### Data Protection
- **Environment Variables**: Sensitive configuration in .env files
- **API Key Management**: Secure storage of LLM provider keys
- **Input Validation**: Sanitization of user queries and document content
- **Access Control**: Role-based access to different document sources

### Network Security
- **Container Isolation**: Docker network segmentation
- **Port Management**: Minimal exposed ports
- **TLS/SSL**: Encrypted connections to external services

## Troubleshooting

### Common Issues

#### 1. ChromaDB Connection Issues
```bash
# Check ChromaDB status
docker ps | grep chroma

# Restart ChromaDB
docker-compose restart chromadb

# Clear and reindex
python reindex_local_only.py
```

#### 2. Empty Search Results
```bash
# Verify document loading
python test_csv_content.py

# Check indexing
python clear_and_test.py

# Disable web crawling
# Set urls_to_crawl: [] in config.yaml
```

#### 3. LLM Provider Errors
```bash
# Check API keys in .env
# Switch providers: DEFAULT_LLM_PROVIDER=groq
# Verify model availability
```

#### 4. Memory Issues
```bash
# Reduce batch size in config.yaml
# Increase Docker memory limits
# Implement document chunking
```

### Monitoring & Logging
- **Application Logs**: Python logging to files
- **Container Logs**: Docker compose logs
- **Performance Metrics**: Response times, cache hit rates
- **Error Tracking**: Exception logging and alerting

### Maintenance Tasks
- **Index Rebuilding**: Periodic reindexing for data updates
- **Cache Cleanup**: Redis memory management
- **Database Maintenance**: PostgreSQL vacuum and analyze
- **Document Updates**: Automated ingestion pipelines

## Future Enhancements

### Planned Features
- **Advanced Analytics**: Query pattern analysis
- **Multi-language Support**: International document processing
- **API Gateway**: RESTful API for external integrations
- **Advanced Security**: OAuth integration, audit logging
- **Real-time Updates**: Live document synchronization
- **Advanced UI**: Rich web interface with document preview

### Technical Improvements
- **Hybrid Search**: Combining vector and keyword search
- **Advanced Chunking**: Semantic document segmentation
- **Model Fine-tuning**: Domain-specific embedding models
- **Distributed Architecture**: Microservices deployment
- **Advanced Caching**: Multi-level cache hierarchy

---

**Document Version**: 1.0  
**Last Updated**: December 2024  
**Maintained By**: Development Team