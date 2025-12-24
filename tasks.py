import os
import time
from celery import Celery
from typing import List, Dict, Any
# import rag_service
import rag_service_mock as rag_service  # Use mock for quick testing
import agent

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
    Background task to generate the roadmap using LangGraph agent.
    """
    # Simulate some processing time
    time.sleep(1)
    
    # Use the LangGraph agent to generate the roadmap
    result = agent.generate_roadmap_with_agent(
        goal=goal,
        duration_weeks=duration_weeks,
        current_skills=current_skills
    )
    
    return result
