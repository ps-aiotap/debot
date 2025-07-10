# DeBot - AI Domain Expert Chatbot

A production-ready AI chatbot that answers domain-specific queries using private documentation and selected public websites, built with Retrieval-Augmented Generation (RAG) architecture.

🎥 **[Watch Demo Video](https://www.loom.com/share/3fa6fbd73fb542b7840c42037b22c024)**

## 🏗️ Architecture

- **Backend**: Python with LlamaIndex for RAG pipeline
- **Vector Database**: ChromaDB for embeddings and similarity search
- **Caching**: Redis for embeddings, API calls, and responses
- **Database**: PostgreSQL for document metadata and chat history
- **Frontend**: Streamlit with interactive chat interface
- **AI Models**: OpenAI GPT-4/3.5 + text-embedding-3-small
- **Data Sources**: PDFs, Markdown/Text docs, Web crawling, Excel/CSV
- **Deployment**: Docker Compose + Kubernetes ready

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- OpenAI API key or Groq API key

### Installation

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd debot
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**:

   ```bash
   cp .env.example .env
   # Update .env with your API keys
   ```

4. **Start Docker services**:

   ```bash
   python start.py
   # Or manually: docker-compose up -d
   ```

5. **Add your data**:

   - Place PDFs in `./data/pdfs/`
   - Place documents in `./data/docs/`
   - Place markdown files in `./data/mds/`
   - Configure websites in `config.yaml`

6. **Setup and index data**:

   ```bash
   python setup.py
   ```

7. **Run the application**:

   ```bash
   # Web Interface
   streamlit run streamlit_app.py

   # CLI Interface
   python main.py
   ```

## 📁 Project Structure

```
debot/
├── ingest/                 # Data ingestion modules
│   ├── load_docs.py       # Markdown/text loader
│   ├── load_pdfs.py       # PDF parser with caching
│   ├── crawler.py         # Async web crawler
│   ├── load_excel.py      # Excel/CSV test cases
│   └── load_sharepoint.py # SharePoint integration
├── providers/             # LLM providers
├── data/                  # Data directories
│   ├── docs/             # Documents (.md, .txt)
│   ├── pdfs/             # PDF files
│   └── mds/              # Markdown files
├── k8s/                   # Kubernetes manifests
├── cache_utils.py         # Redis caching utilities
├── embedding_service.py   # Embedding & indexing
├── qa_service.py         # RAG query engine
├── database.py           # PostgreSQL models
├── main.py               # CLI application
├── streamlit_app.py      # Web UI
├── setup.py              # Setup script
├── start.py              # Docker startup
├── docker-compose.yml    # Docker services
├── config.yaml           # Configuration
└── .env                  # Environment variables
```

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# API Keys
GROQ_API_KEY=your_groq_api_key
OPENAI_API_KEY=your_openai_api_key

# Services
CHROMA_HOST=localhost
CHROMA_PORT=8000
REDIS_HOST=localhost
REDIS_PORT=6379

# Data directories
DOCS_DIR=./data/docs
PDF_DIR=./data/pdfs
MDS_DIR=./data/mds

# LLM Settings
DEFAULT_LLM_PROVIDER=groq
GROQ_MODEL=llama3-8b-8192
```

### Configuration File (config.yaml)

```yaml
crawling:
  urls_to_crawl:
    - 'https://example.com/docs'
  max_pages: 50
  crawl_depth: 2

embedding:
  model: 'all-MiniLM-L6-v2'
  chunk_size: 1000
  chunk_overlap: 200

retrieval:
  top_k: 5
  similarity_threshold: 0.7
```

## 🔧 Usage

### Web Interface

```bash
streamlit run streamlit_app.py
# Open http://localhost:8501
```

### CLI Mode

```bash
python main.py
# Interactive command-line interface
```

### Programmatic Usage

```python
from main import ChatbotApp

app = ChatbotApp()
await app.initialize()
response = app.ask_question("Your question here")
print(response["answer"])
```

## 🐳 Docker Deployment

### Local Development

```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

### Production Deployment

```bash
# Build production image
docker build -t debot:latest .

# Deploy with environment-specific config
docker-compose -f docker-compose.prod.yml up -d
```

## ☸️ Kubernetes Deployment

```bash
# Deploy to Kubernetes
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/documents-pvc.yaml
kubectl apply -f k8s/redis.yaml
kubectl apply -f k8s/chromadb.yaml
kubectl apply -f k8s/chatbot.yaml

# Access the application
kubectl port-forward svc/chatbot-service 8502:8502 -n debot
```

## 🔄 Features

### Data Ingestion

- **Multi-format support**: PDF, Markdown, Text, Excel/CSV
- **Web crawling**: Async crawling with robots.txt compliance
- **SharePoint integration**: Direct document access
- **Azure DevOps Wiki**: Wiki page ingestion
- **Incremental updates**: Smart re-indexing based on content changes

### AI & Search

- **RAG Pipeline**: Retrieval-Augmented Generation
- **Vector Search**: Semantic similarity with ChromaDB
- **Caching**: Redis-based response and embedding cache
- **Multiple LLM Support**: OpenAI, Groq, and extensible providers
- **Source Attribution**: Automatic citation of source documents

### User Interface

- **Streamlit Web UI**: Interactive chat interface
- **CLI Interface**: Command-line interaction
- **Debug Tools**: Environment and connectivity diagnostics
- **Chat History**: Persistent conversation memory
- **Source Filtering**: Filter by document type or source

## 🧪 Development

### Running Tests

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Run with coverage
pytest --cov=debot tests/
```

### Code Quality

```bash
# Format code
black debot/
isort debot/

# Lint code
flake8 debot/
mypy debot/
```

## 📊 Monitoring

### Health Checks

- ChromaDB: `http://localhost:8000/api/v1/heartbeat`
- Redis: `redis-cli ping`
- Application: Built-in health endpoints

### Logging

- Structured logging with configurable levels
- Docker container logs via `docker-compose logs`
- Kubernetes logs via `kubectl logs`

## 🔒 Security

- API key management via environment variables
- No credentials stored in code or containers
- Network isolation in Docker/Kubernetes deployments
- Input validation and sanitization

## 🚀 Performance

- **Caching Strategy**: Multi-layer caching (Redis + in-memory)
- **Async Processing**: Non-blocking I/O for web crawling
- **Batch Operations**: Efficient document processing
- **Resource Optimization**: Configurable chunk sizes and retrieval limits

## 📝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the `/docs` directory for detailed guides
- **Issues**: Report bugs via GitHub Issues
- **Discussions**: Join community discussions in GitHub Discussions

## 🎯 Roadmap

- [ ] Multi-tenant support
- [ ] Advanced analytics dashboard
- [ ] Integration with more data sources
- [ ] Fine-tuning capabilities
- [ ] Mobile-responsive UI
- [ ] API rate limiting and quotas

---

**Built with ❤️ for intelligent document interaction**
