#!/usr/bin/env python3
"""
Simple load test script for the Smart Learning Path Generator API.
Tests concurrent roadmap generation requests.
"""

import requests
import time
import concurrent.futures
import json
from typing import List, Dict

API_URL = "http://localhost:8000"

def create_roadmap_request(goal: str) -> Dict:
    """Send a roadmap generation request and return the task_id."""
    payload = {
        "current_skills": ["HTML", "CSS"],
        "goal": goal,
        "weekly_hours": 10,
        "duration_weeks": 4
    }
    
    try:
        response = requests.post(f"{API_URL}/generate-roadmap", json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def poll_task_result(task_id: str, max_attempts: int = 30) -> Dict:
    """Poll for task completion."""
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{API_URL}/tasks/{task_id}", timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "completed":
                return data
            elif data.get("status") == "failed":
                return data
            
            time.sleep(2)  # Wait 2 seconds between polls
        except Exception as e:
            return {"error": str(e)}
    
    return {"error": "Timeout waiting for task completion"}

def test_single_request(goal: str) -> Dict:
    """Test a single roadmap generation request end-to-end."""
    start_time = time.time()
    
    # Step 1: Create request
    task_response = create_roadmap_request(goal)
    if "error" in task_response:
        return {"goal": goal, "success": False, "error": task_response["error"]}
    
    task_id = task_response.get("task_id")
    if not task_id:
        return {"goal": goal, "success": False, "error": "No task_id returned"}
    
    # Step 2: Poll for result
    result = poll_task_result(task_id)
    
    elapsed = time.time() - start_time
    
    if "error" in result:
        return {"goal": goal, "success": False, "error": result["error"], "elapsed": elapsed}
    
    if result.get("status") == "completed":
        weeks = len(result.get("result", {}).get("roadmap", []))
        return {"goal": goal, "success": True, "weeks": weeks, "elapsed": elapsed}
    
    return {"goal": goal, "success": False, "error": "Unexpected response", "elapsed": elapsed}

def run_load_test(num_concurrent: int = 10):
    """Run concurrent load test."""
    print(f"\n{'='*60}")
    print(f"Smart Learning Path Generator - Load Test")
    print(f"{'='*60}\n")
    print(f"Testing with {num_concurrent} concurrent requests...\n")
    
    # Test different goals
    goals = ["React", "Python", "JavaScript", "SaaS", "MERN", 
             "Vue", "Django", "Node.js", "TypeScript", "Docker"]
    
    # Health check first
    try:
        health = requests.get(f"{API_URL}/health", timeout=5)
        if health.status_code == 200:
            print("✓ API health check passed\n")
        else:
            print("✗ API health check failed\n")
            return
    except Exception as e:
        print(f"✗ Cannot connect to API: {e}\n")
        return
    
    # Run concurrent requests
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_concurrent) as executor:
        futures = [executor.submit(test_single_request, goal) for goal in goals[:num_concurrent]]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    total_time = time.time() - start_time
    
    # Print results
    print(f"\n{'='*60}")
    print("Results:")
    print(f"{'='*60}\n")
    
    successful = [r for r in results if r.get("success")]
    failed = [r for r in results if not r.get("success")]
    
    print(f"Total requests: {len(results)}")
    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(failed)}")
    print(f"Total time: {total_time:.2f}s")
    print(f"Average time per request: {total_time/len(results):.2f}s\n")
    
    if successful:
        avg_elapsed = sum(r["elapsed"] for r in successful) / len(successful)
        print(f"Average successful request time: {avg_elapsed:.2f}s\n")
    
    # Show individual results
    print("Individual Results:")
    for i, result in enumerate(results, 1):
        status = "✓" if result.get("success") else "✗"
        goal = result.get("goal", "Unknown")
        elapsed = result.get("elapsed", 0)
        
        if result.get("success"):
            weeks = result.get("weeks", 0)
            print(f"{status} {i}. {goal}: {elapsed:.2f}s ({weeks} weeks generated)")
        else:
            error = result.get("error", "Unknown error")
            print(f"{status} {i}. {goal}: Failed - {error}")
    
    print(f"\n{'='*60}\n")

if __name__ == "__main__":
    run_load_test(num_concurrent=10)
