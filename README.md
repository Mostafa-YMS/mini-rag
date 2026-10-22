# mini-rag

A small, modular Retrieval-Augmented Generation (RAG) backend built with **FastAPI**. It provides API workflows for uploading documents, splitting them into chunks, embedding and indexing those chunks, and searching a project's vector index.

> This repository is an implementation project. Review the configuration and provider implementations before using it with real or sensitive data.

## What it does

- **Project-scoped document workflows** for managing files and text chunks.
- **Document ingestion** for PDF and plain-text files.
- **Chunking** with configurable chunk size and overlap.
- **Embedding and indexing** through provider interfaces.
- **Vector search** with configurable result limits.
- **Provider factories** for selecting generation, embedding, and vector-database backends through settings.
- **MongoDB persistence** for project, asset, and chunk metadata.
- **Docker Compose configuration** for the MongoDB service.

## Architecture

The application is organized around a few responsibilities:

- `src/main.py` — initializes FastAPI and application-lifetime clients.
- `src/routes/` — exposes file-processing and NLP/index endpoints.
- `src/controllers/` — coordinates file processing, chunking, embeddings, indexing, and search.
- `src/models/` — persistence models and schemas.
- `src/stores/` — language-model and vector-database provider abstractions.
- `src/helpers/config.py` — environment-based settings.

The ingestion path is:

1. Upload a PDF or TXT file to a project.
2. Process the file into text chunks.
3. Generate embeddings for the chunks.
4. Index the vectors and associated text/metadata in the configured vector database.
5. Embed a query and search the project's index.

## Technology

- Python
- FastAPI
- Pydantic Settings
- MongoDB with Motor
- LangChain community document loaders and text splitters
- PyMuPDF for PDF loading
- OpenAI/Cohere client libraries
- Qdrant client
- Docker Compose

The actual provider and model used at runtime depend on the configured backend settings and the corresponding implementation.

## Requirements

- Python compatible with the pinned dependencies in `src/requirements.txt`
- MongoDB
- Credentials and configuration for whichever model and vector-store providers you choose
- Docker Compose is optional if MongoDB is already available locally

## Setup

### 1. Start MongoDB

The repository includes a Compose file under `docker/`. Configure the MongoDB root credentials expected by the Compose file, then start the service:

```bash
cd docker
docker compose up -d
cd ..
```

The Compose configuration maps host port `27016` to MongoDB's container port `27017`.

### 2. Configure the application

Create `src/.env` (the settings loader reads `.env` from the `src` working directory). Add the values required by `src/helpers/config.py` and the selected providers.

At minimum, the configuration model declares:

```dotenv
NAME=mini-rag
MONGO_URL=mongodb://<username>:<password>@localhost:27016/?authSource=admin
DATABASE=mini_rag

GENERATION_BACKEND=<configured-generation-provider>
EMBEDDING_BACKEND=<configured-embedding-provider>
GENERATION_MODEL_ID=<generation-model-id>
EMBEDDING_MODEL_ID=<embedding-model-id>
EMBEDDING_MODEL_SIZE=<embedding-vector-size>

VDB_BACKEND=<configured-vector-database-provider>
VDB_PATH=<provider-specific-path-or-configuration>
```

Set any provider-specific credentials and options required by your chosen implementations (for example, API keys, model endpoints, distance method, generation limits, or temperature). The placeholders above are examples, not working credentials or guaranteed provider names. Check the code under `src/stores/` for supported options. Do not commit real secrets.

### 3. Install Python dependencies

From the repository root:

```bash
./i
```

The helper script installs the pinned dependencies from `src/requirements.txt`.

### 4. Run the API

From the repository root:

```bash
./run
```

The helper script changes into `src/` and starts FastAPI's development server. For local development, consult the FastAPI CLI output for the server address and interactive API documentation.

## API workflows

The current routes include:

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/files/upload/{project_id}` | Upload a file to a project |
| `POST` | `/files/process/{project_id}` | Process uploaded files into chunks |
| `POST` | `/nlp/index/push/{project_id}` | Embed and index stored chunks |
| `GET` | `/nlp/index/info/{project_id}` | Inspect index/collection information |
| `POST` | `/nlp/index/search/{project_id}` | Search the project's vector index |

Use the FastAPI interactive docs to inspect request schemas and response formats. File processing currently defines loaders for PDF and TXT files; other formats are not implied to be supported.

## Configuration and safety notes

- Keep API keys, database passwords, and private endpoints out of source control.
- Use test documents and non-sensitive data during development.
- Confirm file-size limits, validation, authentication, and access controls before exposing the service beyond a trusted local environment.
- Provider behavior depends on the implementation selected in configuration.
- This README describes the code currently present; it does not claim production readiness or benchmarked retrieval quality.

## Possible next improvements

- Add a safe `.env.example` with placeholders for every required setting.
- Add API examples and representative request/response payloads.
- Add automated tests for document processing, indexing, and retrieval.
- Add evaluation fixtures for retrieval quality and failure cases.
- Document supported providers and their configuration options explicitly.
