import os
import time
from celery import Celery
from typing import List, Dict, Any
import rag_service

# Configure Celery
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

celery_app = Celery(
    "tasks",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND
)

# Initialize the RAG index when the worker starts
@celery_app.task(bind=True)
def initialize_rag_index(self):
    """Initialize the RAG index on worker startup."""
    try:
        rag_service.build_sample_index()
        return {"status": "success", "message": "RAG index initialized"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@celery_app.task(name="generate_roadmap_task")
def generate_roadmap_task(goal: str, duration_weeks: int, current_skills: List[str]) -> Dict[str, Any]:
    """
    Background task to generate the roadmap.
    Currently uses the same logic as the synchronous endpoint, but offloaded.
    """
    # Simulate some heavy processing time
    time.sleep(2)
    
    # 1. Retrieve relevant resources using RAG
    rag_resources = rag_service.query_resources(goal)
    
    all_resource_strings = [f"{r['title']}: {r['snippet']}" for r in rag_resources]

    roadmap = []
    for week_num in range(1, duration_weeks + 1):
        # 2. Generate Topic and Reasoning (Simple Logic)
        if week_num == 1:
            topic = "Foundations & Setup"
            desc = f"Setting up the environment for {goal} and learning basics."
            why_first = "You need to understand the core concepts before moving to advanced topics."
            week_resources = all_resource_strings[:2] 
        elif week_num == duration_weeks:
            topic = "Final Project & Review"
            desc = f"Building a capstone project to demonstrate {goal} mastery."
            why_first = "Applying knowledge in a project is the best way to solidify skills."
            week_resources = ["Project Guide", "Deployment Docs"]
        else:
            topic = f"Intermediate Concepts (Week {week_num})"
            desc = f"Deepening understanding of {goal}."
            why_first = "Building upon the foundations to handle more complex scenarios."
            if len(all_resource_strings) > 2:
                week_resources = all_resource_strings[2:]
            else:
                week_resources = ["Advanced Tutorial", "Practice Exercises"]

        week_data = {
            "week_number": week_num,
            "topic": topic,
            "description": desc,
            "resources": week_resources,
            "why_first": why_first
        }
        roadmap.append(week_data)

    return {
        "roadmap": roadmap,
        "total_weeks": duration_weeks
    }
