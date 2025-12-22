"""
Smart Learning Path Generator - Backend MVP (Day 1)

Plan for Day 1 (5 Commits):
1. [x] Commit 1: FastAPI skeleton with health check and static roadmap endpoint.
2. [x] Commit 2: Input validation, dynamic week generation (loop-based), and error handling.
3. [x] Commit 3: RAG setup (LlamaIndex + ChromaDB) with sample data and query helper.
4. [ ] Commit 4: Integrate RAG into roadmap generation (resources + reasoning).
5. [ ] Commit 5: Cleanup, documentation, and manual test instructions.
"""

from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import rag_service

app = FastAPI(title="Smart Learning Path Generator API")

# Initialize RAG index on startup (optional, but good for performance)
@app.on_event("startup")
async def startup_event():
    # In a real app, we might do this async or in background
    try:
        rag_service.build_sample_index()
    except Exception as e:
        print(f"Warning: Could not build index on startup: {e}")

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

class RoadmapResponse(BaseModel):
    roadmap: List[RoadmapWeek]
    total_weeks: int

# --- Endpoints ---

@app.get("/health")
async def health_check():
    """Health check endpoint to verify service status."""
    return {"status": "ok"}

@app.post("/generate-roadmap", response_model=RoadmapResponse)
async def generate_roadmap(request: RoadmapRequest):
    """
    Generates a basic weekly roadmap based on the input duration.
    Currently returns placeholder topics and resources.
    """
    # Basic error handling example (though Pydantic handles the constraints above)
    if not request.goal.strip():
        raise HTTPException(status_code=400, detail="Goal cannot be empty.")

    # Temporary: Query RAG for the goal to see it working
    # We will integrate this properly into weeks in Commit 4
    rag_resources = rag_service.query_resources(request.goal)
    # Flatten for display in the first week just to prove it works
    rag_titles = [r["title"] for r in rag_resources]

    roadmap = []
    for week_num in range(1, request.duration_weeks + 1):
        # Simple logic to vary the content slightly
        if week_num == 1:
            topic = "Foundations & Setup"
            desc = f"Setting up the environment for {request.goal} and learning basics."
            # Attach RAG results here for now
            current_resources = ["Official Documentation"] + rag_titles
        elif week_num == request.duration_weeks:
            topic = "Final Project & Review"
            desc = f"Building a capstone project to demonstrate {request.goal} mastery."
            current_resources = ["Project Guide", "Deployment Docs"]
        else:
            topic = f"Intermediate Concepts (Week {week_num})"
            desc = f"Deepening understanding of {request.goal}."
            current_resources = ["Advanced Tutorial", "Practice Exercises"]

        week_data = RoadmapWeek(
            week_number=week_num,
            topic=topic,
            description=desc,
            resources=current_resources
        )
        roadmap.append(week_data)

    return RoadmapResponse(
        roadmap=roadmap,
        total_weeks=request.duration_weeks
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
