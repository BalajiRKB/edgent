"""
Simplified RAG service for quick testing without heavy ML dependencies.
"""
import os
from typing import List, Dict

_mock_data = {
    "react": [
        {"title": "React Documentation", "snippet": "Learn React hooks, components, and state management..."},
        {"title": "React Tutorial", "snippet": "Build your first React application step by step..."},
        {"title": "React Best Practices", "snippet": "Modern patterns for React development..."}
    ],
    "python": [
        {"title": "Python Docs", "snippet": "Learn Python fundamentals, OOP, and advanced topics..."},
        {"title": "Python Tutorial", "snippet": "Getting started with Python programming..."},
        {"title": "Python Best Practices", "snippet": "Writing clean, maintainable Python code..."}
    ],
    "javascript": [
        {"title": "JavaScript Guide", "snippet": "Master ES6+, async/await, and modern JavaScript..."},
        {"title": "JavaScript Tutorial", "snippet": "Learn JavaScript from basics to advanced..."},
        {"title": "JavaScript Patterns", "snippet": "Design patterns in JavaScript..."}
    ]
}

def build_sample_index(data_dir: str = "data", force_reload: bool = False):
    """Mock index builder - does nothing for quick testing."""
    print(f"[Mock] Index initialized (skipping actual ChromaDB for quick test)")

def query_resources(goal: str) -> List[Dict[str, str]]:
    """
    Mock query function - returns hardcoded results based on goal.
    """
    goal_lower = goal.lower()
    
    # Find matching mock data
    for key in _mock_data:
        if key in goal_lower:
            return _mock_data[key]
    
    # Default response
    return [
        {"title": f"Resource for {goal}", "snippet": f"Learn {goal} fundamentals and best practices..."},
        {"title": f"{goal} Tutorial", "snippet": f"Getting started with {goal}..."},
        {"title": f"{goal} Guide", "snippet": f"Complete guide to mastering {goal}..."}
    ]
