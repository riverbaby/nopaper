# DocNest

一款可本地部署、类 Paperless-NGX 的文档收集 / OCR / 总结 / 语义检索（RAG）系统。

## 功能特点

- **文档接入**：支持上传 PDF、图片（PNG/JPG/TIFF/HEIC），批量导入，自动生成缩略图和预览
- **智能处理**：OCR 文字识别（PaddleOCR）、AI 摘要（Ollama/LLM）、向量化嵌入（BGE）
- **检索与组织**：标签、分类、关键字 + 向量混合检索（BM25 + Vector）
- **RAG 对话**：基于文档内容的智能问答，带引用来源
- **可视化视图**：网格、列表、详情页面，完整的文档管理界面
- **离线可用**：所有组件可本地部署，无需云服务
- **Docker 一键部署**：使用 Docker Compose 快速启动

## 技术栈

### 后端
- **框架**：FastAPI (Python)
- **数据库**：PostgreSQL
- **向量数据库**：Qdrant
- **消息队列**：Redis + Celery
- **OCR**：PaddleOCR
- **LLM**：Ollama (支持 Qwen, LLaMA 等)
- **嵌入模型**：BGE-M3 (sentence-transformers)

### 前端
- **框架**：React + Vite
- **路由**：React Router
- **状态管理**：TanStack Query
- **样式**：原生 CSS

## 快速开始

### 前置要求

- Docker & Docker Compose
- 至少 8GB RAM
- 20GB 可用磁盘空间

### 安装步骤

1. **克隆仓库**

```bash
git clone https://github.com/riverbaby/nopaper.git
cd nopaper
```

2. **配置环境变量**

```bash
cp .env.example .env
# 编辑 .env 文件，修改必要的配置
```

3. **启动服务**

```bash
# 首次启动，会拉取 Ollama 模型（可能需要较长时间）
docker-compose up -d

# 等待所有服务启动
docker-compose ps

# 拉取 Ollama 模型（首次使用）
docker-compose exec ollama ollama pull qwen2.5:7b-instruct
```

4. **访问应用**

- 前端界面：http://localhost:3000
- API 文档：http://localhost:8000/api/docs
- Qdrant 控制台：http://localhost:6333/dashboard

## 使用指南

### 上传文档

1. 访问 http://localhost:3000
2. 点击 "Upload" 导航链接
3. 选择 PDF 或图片文件
4. 点击 "Upload" 上传

文档将自动进入处理流水线：
- OCR 文字识别
- AI 摘要生成
- 向量化嵌入
- 生成缩略图和预览

### 搜索文档

1. 点击 "Search" 导航链接
2. 输入关键词或问题
3. 系统会使用混合检索（BM25 + 向量相似度）返回结果

### RAG 对话

1. 点击 "Chat" 导航链接
2. 输入问题
3. AI 会基于文档内容回答，并提供引用来源

## 项目结构

```
nopaper/
├── backend/                 # FastAPI 后端
│   ├── app/
│   │   ├── models/         # 数据库模型
│   │   ├── routers/        # API 路由
│   │   ├── services/       # 业务服务
│   │   │   ├── ocr/       # OCR 服务
│   │   │   ├── llm/       # LLM 服务
│   │   │   ├── embed/     # 嵌入服务
│   │   │   ├── vector/    # 向量存储
│   │   │   └── preview/   # 预览生成
│   │   ├── workers/       # Celery 任务
│   │   └── main.py        # 主入口
│   └── requirements.txt
├── frontend/               # React 前端
│   ├── src/
│   │   ├── pages/         # 页面组件
│   │   ├── api/           # API 客户端
│   │   └── App.tsx
│   └── package.json
├── deploy/                 # 部署配置
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── nginx.conf
├── data/                   # 数据目录（自动创建）
│   ├── docs/              # 文档文件
│   ├── thumbs/            # 缩略图
│   ├── previews/          # 预览图
│   ├── pg/                # PostgreSQL 数据
│   └── qdrant/            # Qdrant 数据
├── docker-compose.yml
└── .env.example
```

## 配置说明

### OCR 配置

支持多种 OCR 引擎（可在 `.env` 中配置）：

- `paddleocr`（默认）：支持中英文，效果均衡
- `tesseract`：开源，多语言支持
- `deepseek-ocr`：需要 API key

### LLM 配置

支持多种 LLM 提供商：

- `ollama`（默认）：本地部署，支持 Qwen、LLaMA 等
- `openai_compatible`：OpenAI API 兼容接口
- `deepseek`：DeepSeek API

### 向量数据库

支持多种向量数据库：

- `qdrant`（默认）：轻量、高性能
- `pgvector`：PostgreSQL 扩展
- `weaviate`、`milvus`、`chroma`

## 开发

### 后端开发

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 前端开发

```bash
cd frontend
npm install
npm run dev
```

### Worker 开发

```bash
cd backend
celery -A app.workers.celery_app worker -l INFO
```

## API 文档

启动服务后访问：http://localhost:8000/api/docs

主要 API 端点：

- `POST /api/v1/documents/` - 上传文档
- `GET /api/v1/documents/` - 列出文档
- `GET /api/v1/documents/{id}` - 获取文档详情
- `POST /api/v1/search/` - 搜索文档
- `POST /api/v1/search/chat` - RAG 对话

## 性能优化

- Worker 并发：建议设置为 CPU 核心数
- PDF 渲染：150 DPI 预览，600px 宽度缩略图
- 分块嵌入：512 token + 64 overlap
- Qdrant HNSW 参数：m=16, ef_construct=128

## 故障排除

### Ollama 模型下载失败

```bash
# 手动拉取模型
docker-compose exec ollama ollama pull qwen2.5:7b-instruct
```

### OCR 识别效果不佳

- 调整 `OCR_LANGS` 配置
- 尝试不同的 OCR 引擎
- 提高扫描 DPI（在预处理中）

### 向量搜索不准确

- 调整混合搜索权重（`weights` 参数）
- 增加检索数量（`k` 参数）
- 使用不同的嵌入模型

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 致谢

- PaddleOCR
- Ollama
- Qdrant
- FastAPI
- React
