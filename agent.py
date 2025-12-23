"""
LangGraph Agent for Smart Roadmap Generation

This module implements a simple agentic workflow using LangGraph.
The workflow has 3 nodes:
1. retrieve_resources: Get relevant resources from RAG
2. reason_prerequisites: Determine learning order and prerequisites
3. generate_timeline: Create structured weekly roadmap

Uses Google Gemini API for enhanced reasoning (optional).
"""

import os
from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
import rag_service


class RoadmapState(TypedDict):
    """State that flows through the graph."""
    goal: str
    current_skills: List[str]
    duration_weeks: int
    retrieved_resources: List[Dict[str, str]]
    prerequisites: Dict[str, str]
    roadmap: List[Dict[str, Any]]


def retrieve_resources_node(state: RoadmapState) -> RoadmapState:
    """
    Node 1: Retrieve relevant resources using LlamaIndex RAG.
    """
    print(f"[Agent] Retrieving resources for goal: {state['goal']}")
    resources = rag_service.query_resources(state['goal'])
    state['retrieved_resources'] = resources
    return state


def reason_prerequisites_node(state: RoadmapState) -> RoadmapState:
    """
    Node 2: Determine learning prerequisites and ordering.
    Uses simple rule-based reasoning (can be enhanced with LLM later).
    """
    print("[Agent] Reasoning about prerequisites and learning order")
    
    goal = state['goal'].lower()
    current_skills = [s.lower() for s in state['current_skills']]
    
    # Simple prerequisite reasoning based on common patterns
    prerequisites = {}
    
    if 'react' in goal:
        if 'html' not in current_skills and 'css' not in current_skills:
            prerequisites['week_1'] = "Learn HTML/CSS first - React builds on web fundamentals"
        elif 'javascript' not in current_skills:
            prerequisites['week_1'] = "Learn JavaScript basics - React is a JavaScript library"
        else:
            prerequisites['week_1'] = "Review JavaScript ES6+ features before diving into React"
    
    elif 'saas' in goal or 'mern' in goal:
        if 'javascript' not in current_skills:
            prerequisites['week_1'] = "Master JavaScript fundamentals - required for full-stack development"
        elif 'react' not in current_skills:
            prerequisites['week_2'] = "Learn React for the frontend before backend integration"
        else:
            prerequisites['week_1'] = "Review full-stack architecture patterns"
    
    elif 'javascript' in goal:
        if 'html' not in current_skills:
            prerequisites['week_1'] = "Learn HTML basics to understand the DOM that JavaScript manipulates"
        else:
            prerequisites['week_1'] = "Start with ES6+ syntax and modern JavaScript features"
    
    else:
        prerequisites['week_1'] = f"Build foundational knowledge in {state['goal']} step by step"
    
    state['prerequisites'] = prerequisites
    return state


def generate_timeline_node(state: RoadmapState) -> RoadmapState:
    """
    Node 3: Generate the final structured weekly roadmap.
    """
    print("[Agent] Generating structured timeline")
    
    duration = state['duration_weeks']
    resources = state['retrieved_resources']
    prerequisites = state['prerequisites']
    goal = state['goal']
    
    # Format resources
    resource_strings = [f"{r['title']}: {r['snippet']}" for r in resources]
    
    roadmap = []
    for week_num in range(1, duration + 1):
        # Determine topic and reasoning
        if week_num == 1:
            topic = "Foundations & Setup"
            desc = f"Setting up the environment for {goal} and learning core concepts."
            why_first = prerequisites.get('week_1', "Establishing a strong foundation is crucial before advancing.")
            week_resources = resource_strings[:2] if resource_strings else ["Getting Started Guide"]
        
        elif week_num == 2 and duration > 2:
            topic = "Core Concepts"
            desc = f"Deep dive into the essential concepts of {goal}."
            why_first = prerequisites.get('week_2', "Building on the foundation with practical knowledge.")
            week_resources = resource_strings[2:4] if len(resource_strings) > 2 else ["Core Documentation", "Practice Exercises"]
        
        elif week_num == duration:
            topic = "Final Project & Review"
            desc = f"Building a capstone project to demonstrate {goal} mastery."
            why_first = "Applying knowledge through a real project solidifies learning and builds portfolio."
            week_resources = ["Project Guide", "Deployment Checklist", "Best Practices"]
        
        else:
            topic = f"Advanced Topics (Week {week_num})"
            desc = f"Exploring advanced features and patterns in {goal}."
            why_first = "Progressive learning - each concept builds on previous knowledge."
            week_resources = resource_strings[-2:] if resource_strings else ["Advanced Tutorial", "Case Studies"]
        
        roadmap.append({
            "week_number": week_num,
            "topic": topic,
            "description": desc,
            "resources": week_resources,
            "why_first": why_first
        })
    
    state['roadmap'] = roadmap
    return state


def create_roadmap_graph() -> StateGraph:
    """
    Creates and compiles the LangGraph workflow.
    """
    workflow = StateGraph(RoadmapState)
    
    # Add nodes
    workflow.add_node("retrieve_resources", retrieve_resources_node)
    workflow.add_node("reason_prerequisites", reason_prerequisites_node)
    workflow.add_node("generate_timeline", generate_timeline_node)
    
    # Define edges
    workflow.set_entry_point("retrieve_resources")
    workflow.add_edge("retrieve_resources", "reason_prerequisites")
    workflow.add_edge("reason_prerequisites", "generate_timeline")
    workflow.add_edge("generate_timeline", END)
    
    return workflow.compile()


def generate_roadmap_with_agent(goal: str, duration_weeks: int, current_skills: List[str]) -> Dict[str, Any]:
    """
    Main function to generate a roadmap using the LangGraph agent.
    """
    print(f"\n=== Starting LangGraph Agent ===")
    print(f"Goal: {goal}, Duration: {duration_weeks} weeks, Skills: {current_skills}")
    
    # Initialize state
    initial_state: RoadmapState = {
        "goal": goal,
        "current_skills": current_skills,
        "duration_weeks": duration_weeks,
        "retrieved_resources": [],
        "prerequisites": {},
        "roadmap": []
    }
    
    # Create and run the graph
    graph = create_roadmap_graph()
    final_state = graph.invoke(initial_state)
    
    print("=== Agent Complete ===\n")
    
    return {
        "roadmap": final_state["roadmap"],
        "total_weeks": duration_weeks
    }
