# DocNest

A locally deployable, Paperless-NGX-like document collection / OCR / summarization / semantic search (RAG) system.

[中文文档](README_CN.md)

## Features

- **Document Ingestion**: Upload PDFs and images (PNG/JPG/TIFF/HEIC), batch import, automatic thumbnail and preview generation
- **Intelligent Processing**: OCR text recognition (PaddleOCR), AI summarization (Ollama/LLM), vector embeddings (BGE)
- **Search & Organization**: Tags, collections, hybrid search (BM25 + Vector similarity)
- **RAG Chat**: Intelligent Q&A based on document content with citations
- **Visual Interface**: Grid view, list view, detail pages - complete document management UI
- **Offline Capable**: All components can be deployed locally without cloud services
- **One-Click Deploy**: Quick startup with Docker Compose

## Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL
- **Vector Database**: Qdrant
- **Message Queue**: Redis + Celery
- **OCR**: PaddleOCR
- **LLM**: Ollama (supports Qwen, LLaMA, etc.)
- **Embedding Model**: BGE-M3 (sentence-transformers)

### Frontend
- **Framework**: React + Vite
- **Routing**: React Router
- **State Management**: TanStack Query
- **Styling**: Native CSS

## Quick Start

### Prerequisites

- Docker & Docker Compose
- At least 8GB RAM
- 20GB available disk space

### Installation Steps

1. **Clone the repository**

```bash
git clone https://github.com/riverbaby/nopaper.git
cd nopaper
```

2. **Configure environment variables**

```bash
cp .env.example .env
# Edit the .env file to modify necessary configurations
```

3. **Start services**

```bash
# First startup will pull Ollama models (may take a while)
docker-compose up -d

# Wait for all services to start
docker-compose ps

# Pull Ollama model (first time use)
docker-compose exec ollama ollama pull qwen2.5:7b-instruct
```

4. **Access the application**

- Frontend UI: http://localhost:3000
- API Documentation: http://localhost:8000/api/docs
- Qdrant Dashboard: http://localhost:6333/dashboard

## User Guide

### Upload Documents

1. Visit http://localhost:3000
2. Click the "Upload" navigation link
3. Select PDF or image files
4. Click "Upload" to submit

Documents will automatically enter the processing pipeline:
- OCR text recognition
- AI summary generation
- Vector embeddings
- Thumbnail and preview generation

### Search Documents

1. Click the "Search" navigation link
2. Enter keywords or questions
3. The system will use hybrid search (BM25 + vector similarity) to return results

### RAG Chat

1. Click the "Chat" navigation link
2. Enter your question
3. AI will answer based on document content and provide citations

## Project Structure

```
nopaper/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── models/         # Database models
│   │   ├── routers/        # API routes
│   │   ├── services/       # Business services
│   │   │   ├── ocr/       # OCR services
│   │   │   ├── llm/       # LLM services
│   │   │   ├── embed/     # Embedding services
│   │   │   ├── vector/    # Vector store
│   │   │   └── preview/   # Preview generation
│   │   ├── workers/       # Celery tasks
│   │   └── main.py        # Main entry
│   └── requirements.txt
├── frontend/               # React frontend
│   ├── src/
│   │   ├── pages/         # Page components
│   │   ├── api/           # API client
│   │   └── App.tsx
│   └── package.json
├── deploy/                 # Deployment configs
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── nginx.conf
├── data/                   # Data directory (auto-created)
│   ├── docs/              # Document files
│   ├── thumbs/            # Thumbnails
│   ├── previews/          # Preview images
│   ├── pg/                # PostgreSQL data
│   └── qdrant/            # Qdrant data
├── docker-compose.yml
└── .env.example
```

## Configuration

### OCR Configuration

Supports multiple OCR engines (configurable in `.env`):

- `paddleocr` (default): Supports Chinese and English, balanced performance
- `tesseract`: Open source, multi-language support
- `deepseek-ocr`: Requires API key

### LLM Configuration

Supports multiple LLM providers:

- `ollama` (default): Local deployment, supports Qwen, LLaMA, etc.
- `openai_compatible`: OpenAI API compatible interface
- `deepseek`: DeepSeek API

### Vector Database

Supports multiple vector databases:

- `qdrant` (default): Lightweight, high performance
- `pgvector`: PostgreSQL extension
- `weaviate`, `milvus`, `chroma`

## Development

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

### Worker Development

```bash
cd backend
celery -A app.workers.celery_app worker -l INFO
```

## API Documentation

After starting services, visit: http://localhost:8000/api/docs

Main API endpoints:

- `POST /api/v1/documents/` - Upload documents
- `GET /api/v1/documents/` - List documents
- `GET /api/v1/documents/{id}` - Get document details
- `POST /api/v1/search/` - Search documents
- `POST /api/v1/search/chat` - RAG chat

## Performance Optimization

- Worker concurrency: Recommended to set to CPU core count
- PDF rendering: 150 DPI preview, 600px width thumbnails
- Chunk embeddings: 512 tokens + 64 overlap
- Qdrant HNSW parameters: m=16, ef_construct=128

## Troubleshooting

### Ollama Model Download Failed

```bash
# Manually pull the model
docker-compose exec ollama ollama pull qwen2.5:7b-instruct
```

### Poor OCR Recognition

- Adjust `OCR_LANGS` configuration
- Try different OCR engines
- Increase scan DPI (in preprocessing)

### Inaccurate Vector Search

- Adjust hybrid search weights (`weights` parameter)
- Increase retrieval count (`k` parameter)
- Use different embedding models

## License

MIT License

## Contributing

Issues and Pull Requests are welcome!

## Acknowledgments

- PaddleOCR
- Ollama
- Qdrant
- FastAPI
- React
