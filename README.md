# EDGENT-Smart Learning Path Generator (Backend MVP)

## Day 2 Goals (Production & Async)
- Containerize the application with Docker.
- Implement async task queue with Redis and Celery.
- Integrate persistent Vector DB (ChromaDB).
- Add intelligent agent reasoning with LangGraph (multi-node workflow).
- Production-ready setup with health checks and monitoring.

## Quick Start

### Development Mode

1. **Setup Environment:**
   ```bash
   cp .env.example .env
   # Edit .env and add your GOOGLE_API_KEY (optional)
   ```

2. **Build and Start Services:**
   ```bash
   docker compose up --build
   ```

3. **Access API Docs:**
   Open [http://localhost:8000/docs](http://localhost:8000/docs).

### Production Mode

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Testing

### Health Check
```bash
curl http://localhost:8000/health
```

### Generate Roadmap (Async)
```bash
# 1. Start Task
curl -X POST http://localhost:8000/generate-roadmap \
  -H "Content-Type: application/json" \
  -d '{
        "current_skills": ["HTML"],
        "goal": "React",
        "weekly_hours": 10,
        "duration_weeks": 4
      }'
# Returns: {"task_id": "...", "status": "processing"}

# 2. Poll Result (replace <task_id>)
curl http://localhost:8000/tasks/<task_id>
```

### Load Testing
```bash
python test_load.py
```

## Architecture

### Services
- **FastAPI**: REST API server
- **Redis**: Message broker for Celery
- **ChromaDB**: Vector database for RAG
- **Worker**: Celery worker for background tasks

### LangGraph Agent Workflow
1. **retrieve_resources**: Query ChromaDB for relevant learning materials
2. **reason_prerequisites**: Determine optimal learning order
3. **generate_timeline**: Create structured weekly roadmap

## Environment Variables

See `.env.example` for all configuration options.

## Health Checks

All services include health checks:
- **FastAPI**: `GET /health`
- **Redis**: `redis-cli ping`
- **Worker**: Celery inspect ping

Check status:
```bash
docker compose ps
```

## Day 1 Goals
- Build a FastAPI backend.
- Generate a structured weekly learning roadmap based on user input.
- Integrate basic RAG (Retrieval-Augmented Generation) using LlamaIndex and ChromaDB to suggest resources.

## How to Run

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Server:**
   ```bash
   uvicorn main:app --reload
   ```

3. **Access API Docs:**
   Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to test the endpoints interactively.

## Manual Testing (Curl Examples)

**1. Health Check:**
```bash
curl -X GET http://127.0.0.1:8000/health
# Expected: {"status": "ok"}
```

**2. Generate Roadmap (React Example):**
```bash
curl -X POST http://127.0.0.1:8000/generate-roadmap \
     -H "Content-Type: application/json" \
     -d '{
           "current_skills": ["HTML", "CSS"],
           "goal": "React",
           "weekly_hours": 10,
           "duration_weeks": 4
         }'
```
*Expected Output:* A JSON object with 4 weeks. Week 1 should contain resources related to React (retrieved from RAG).

**3. Generate Roadmap (SaaS Example):**
```bash
curl -X POST http://127.0.0.1:8000/generate-roadmap \
     -H "Content-Type: application/json" \
     -d '{
           "current_skills": ["Python"],
           "goal": "SaaS",
           "weekly_hours": 5,
           "duration_weeks": 2
         }'
```


