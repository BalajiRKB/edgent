"""
Smart Learning Path Generator - Backend MVP (Day 1)

Plan for Day 1 (5 Commits):
1. [x] Commit 1: FastAPI skeleton with health check and static roadmap endpoint.
2. [x] Commit 2: Input validation, dynamic week generation (loop-based), and error handling.
3. [x] Commit 3: RAG setup (LlamaIndex + ChromaDB) with sample data and query helper.
4. [x] Commit 4: Integrate RAG into roadmap generation (resources + reasoning).
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
    why_first: Optional[str] = None

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

    # 1. Retrieve relevant resources using RAG
    # We query for the overall goal to find the best matching documents
    rag_resources = rag_service.query_resources(request.goal)
    
    # Flatten resources to a list of strings (title + snippet)
    # In a real app, we might distribute these more intelligently across weeks
    all_resource_strings = [f"{r['title']}: {r['snippet']}" for r in rag_resources]

    roadmap = []
    for week_num in range(1, request.duration_weeks + 1):
        # 2. Generate Topic and Reasoning (Simple Logic)
        if week_num == 1:
            topic = "Foundations & Setup"
            desc = f"Setting up the environment for {request.goal} and learning basics."
            why_first = "You need to understand the core concepts before moving to advanced topics."
            # Give the most relevant resources in the first week
            week_resources = all_resource_strings[:2] 
        elif week_num == request.duration_weeks:
            topic = "Final Project & Review"
            desc = f"Building a capstone project to demonstrate {request.goal} mastery."
            why_first = "Applying knowledge in a project is the best way to solidify skills."
            week_resources = ["Project Guide", "Deployment Docs"]
        else:
            topic = f"Intermediate Concepts (Week {week_num})"
            desc = f"Deepening understanding of {request.goal}."
            why_first = "Building upon the foundations to handle more complex scenarios."
            # Distribute remaining resources if available, or generic ones
            if len(all_resource_strings) > 2:
                week_resources = all_resource_strings[2:]
            else:
                week_resources = ["Advanced Tutorial", "Practice Exercises"]

        week_data = RoadmapWeek(
            week_number=week_num,
            topic=topic,
            description=desc,
            resources=week_resources,
            why_first=why_first
        )
        roadmap.append(week_data)

    return RoadmapResponse(
        roadmap=roadmap,
        total_weeks=request.duration_weeks
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
