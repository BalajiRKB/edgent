

from typing import List, Optional
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Smart Learning Path Generator API")

# --- Pydantic Models ---

class RoadmapRequest(BaseModel):
    current_skills: List[str]
    goal: str
    weekly_hours: int
    duration_weeks: int

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
    Placeholder endpoint that returns a static example roadmap.
    In future commits, this will use the input parameters and RAG to generate content.
    """
    # Static example data for Commit 1
    example_week_1 = RoadmapWeek(
        week_number=1,
        topic="Foundations",
        description="Introduction to the core concepts.",
        resources=["Resource A", "Resource B"]
    )
    
    example_week_2 = RoadmapWeek(
        week_number=2,
        topic="Advanced Topics",
        description="Deep dive into complex areas.",
        resources=["Resource C"]
    )

    return RoadmapResponse(
        roadmap=[example_week_1, example_week_2],
        total_weeks=2
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
