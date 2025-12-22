"""
Smart Learning Path Generator - Backend MVP (Day 1)

Plan for Day 1 (5 Commits):
1. [x] Commit 1: FastAPI skeleton with health check and static roadmap endpoint.
2. [x] Commit 2: Input validation, dynamic week generation (loop-based), and error handling.
3. [ ] Commit 3: RAG setup (LlamaIndex + ChromaDB) with sample data and query helper.
4. [ ] Commit 4: Integrate RAG into roadmap generation (resources + reasoning).
5. [ ] Commit 5: Cleanup, documentation, and manual test instructions.
"""

from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Smart Learning Path Generator API")

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

    roadmap = []
    for week_num in range(1, request.duration_weeks + 1):
        # Simple logic to vary the content slightly
        if week_num == 1:
            topic = "Foundations & Setup"
            desc = f"Setting up the environment for {request.goal} and learning basics."
        elif week_num == request.duration_weeks:
            topic = "Final Project & Review"
            desc = f"Building a capstone project to demonstrate {request.goal} mastery."
        else:
            topic = f"Intermediate Concepts (Week {week_num})"
            desc = f"Deepening understanding of {request.goal}."

        week_data = RoadmapWeek(
            week_number=week_num,
            topic=topic,
            description=desc,
            resources=["Official Documentation", "Community Tutorial"]
        )
        roadmap.append(week_data)

    return RoadmapResponse(
        roadmap=roadmap,
        total_weeks=request.duration_weeks
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
