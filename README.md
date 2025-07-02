# AI Domain Expert Chatbot

A modular AI chatbot application that answers domain-specific queries using private documentation and selected public websites, built following IndexCopilot.ai principles.

## 🏗️ Architecture

- **Backend**: Python with LlamaIndex for RAG
- **Database**: PostgreSQL for document metadata and chat history
- **Caching**: Redis (Docker) for embeddings, API calls, and responses
- **Vector DB**: ChromaDB (Docker) for embeddings
- **UI**: Streamlit with chat interface
- **AI**: OpenAI GPT-4/3.5 + text-embedding-3-small
- **Data Sources**: PDFs, Markdown/Text docs, Web crawling

## 🚀 Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   - Update `.env` with your OpenAI API key
   - Ensure PostgreSQL is running (port 5434)

3. **Start Docker services**:
   ```bash
   python start.py
   # Or manually: docker-compose up -d
   ```

4. **Add your data**:
   - Place PDFs in `./data/pdfs/`
   - Place documents in `./data/docs/`
   - Configure websites in `config.yaml`

5. **Setup and index data**:
   ```bash
   python setup.py
   ```

6. **Run the Streamlit app**:
   ```bash
   streamlit run streamlit_app.py
   ```

## 📁 Project Structure

```
debot/
├── ingest/                 # Data ingestion modules
│   ├── load_docs.py       # Markdown/text loader
│   ├── load_pdfs.py       # PDF parser with caching
│   ├── crawler.py         # Async web crawler
│   └── load_chat_logs.py  # Future: Slack/Teams support
├── providers/             # LLM providers (from IndexCopilot.ai)
├── data/                  # Data directories
│   ├── docs/             # Documents (.md, .txt)
│   └── pdfs/             # PDF files
├── cache_utils.py         # Redis caching utilities
├── embedding_service.py   # Embedding & indexing
├── qa_service.py         # RAG query engine
├── database.py           # PostgreSQL models
├── main.py               # Application orchestrator
├── streamlit_app.py      # Streamlit UI
├── setup.py              # Setup script
├── start.py              # Docker startup script
├── docker-compose.yml    # Docker services
├── config.yaml           # Configuration
└── .env                  # Environment variables
```

## ⚙️ Configuration

### Environment Variables (.env)
- `OPENAI_API_KEY`: Your OpenAI API key
- `POSTGRES_*`: PostgreSQL connection settings
- `REDIS_HOST`, `REDIS_PORT`: Redis Docker connection
- `CHROMA_HOST`, `CHROMA_PORT`: ChromaDB Docker connection
- `PDF_DIR`, `DOCS_DIR`: Data directories

### Config File (config.yaml)
- Crawling settings (URLs, depth, limits)
- Embedding and retrieval parameters
- LLM model configuration

## 🔧 Features

- **Multi-source ingestion**: PDFs, documents, websites
- **PostgreSQL storage**: Document metadata and chat history
- **Docker services**: Redis and ChromaDB in containers
- **Redis caching**: Embeddings, crawled content, responses
- **Source filtering**: docs only, web only, or all
- **Async crawling**: Respects robots.txt, handles rate limits
- **Chat interface**: Streamlit with source citations
- **Modular design**: Easy to extend and maintain

## 🔄 Usage

### CLI Mode
```bash
python main.py
```

### Web Interface
```bash
streamlit run streamlit_app.py
```

### Programmatic Usage
```python
from main import ChatbotApp

app = ChatbotApp()
await app.initialize()
response = app.ask_question("Your question here")
```

## 🧪 Phase 2 Preparation

The `ingest/load_chat_logs.py` module is prepared for future Slack/Teams support chat ingestion.

## 📝 Notes

- All caching uses Redis (Docker) with configurable TTL
- Embeddings are cached by content hash
- Web content respects robots.txt by default
- Vector database runs in ChromaDB Docker container
- Document metadata and chat history stored in PostgreSQL
- Services can be started with `python start.py`