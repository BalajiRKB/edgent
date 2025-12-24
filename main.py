from typing import List, Optional, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from celery.result import AsyncResult
import tasks

app = FastAPI(title="Smart Learning Path Generator API")

# Initialize RAG index on startup (optional, but good for performance)
# Note: In async mode, the worker will need the index, not necessarily the API
@app.on_event("startup")
async def startup_event():
    pass


# --- Pydantic Models ---

class RoadmapRequest(BaseModel):
    current_skills: List[str] = Field(..., description="List of current skills")
    goal: str = Field(..., min_length=3, description="The learning goal")
    weekly_hours: int = Field(..., ge=1, le=168, description="Hours available per week")
    duration_weeks: int = Field(..., ge=1, le=52, description="Duration of the roadmap in weeks")

class RoadmapWeek(BaseModel):
    week_number: int
    topic: str
    description: str
    resources: List[str]
    why_first: Optional[str] = None

class RoadmapResponse(BaseModel):
    roadmap: List[RoadmapWeek]
    total_weeks: int

class TaskResponse(BaseModel):
    task_id: str
    status: str

# --- Endpoints ---

@app.get("/health")
async def health_check():
    """Health check endpoint to verify service status."""
    return {"status": "ok"}

@app.post("/generate-roadmap", response_model=TaskResponse)
async def generate_roadmap(request: RoadmapRequest):
    """
    Starts a background task to generate the roadmap.
    Returns a task_id to poll for results.
    """
    if not request.goal.strip():
        raise HTTPException(status_code=400, detail="Goal cannot be empty.")

    task = tasks.generate_roadmap_task.delay(
        goal=request.goal,
        duration_weeks=request.duration_weeks,
        current_skills=request.current_skills
    )
    
    return TaskResponse(task_id=task.id, status="processing")

@app.get("/tasks/{task_id}")
async def get_task_result(task_id: str):
    """
    Polls the status and result of a background task.
    """
    task_result = AsyncResult(task_id, app=tasks.celery_app)
    
    if task_result.state == 'PENDING':
        return {"task_id": task_id, "status": "processing"}
    elif task_result.state == 'SUCCESS':
        return {"task_id": task_id, "status": "completed", "result": task_result.result}
    elif task_result.state == 'FAILURE':
        return {"task_id": task_id, "status": "failed", "error": str(task_result.result)}
    
    return {"task_id": task_id, "status": task_result.state}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
