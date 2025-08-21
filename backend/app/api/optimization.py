import asyncio
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List
from app.models import (
    OptimizationRequest, OptimizationProgress, OptimizationResults
)
from app.services.optimization_service import optimization_service
from app.services.agent_service import agent_service
from app.services.keycloak_service import keycloak_service

router = APIRouter()
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency to get current authenticated user"""
    token = credentials.credentials
    payload = keycloak_service.verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )
    
    return payload

async def run_optimization_workflow(request_id: str, user_id: str):
    """Background task to run the optimization workflow"""
    try:
        # Update progress to running
        optimization_service.update_progress(request_id, 0.0, "Starting agent workflow")
        
        # Run the agent workflow
        activities = await agent_service.simulate_agent_workflow(user_id)
        
        # Update progress as agents complete
        total_steps = len(activities)
        for i, activity in enumerate(activities):
            progress = ((i + 1) / total_steps) * 100
            step_name = f"Completed: {activity.agent} - {activity.action}"
            optimization_service.update_progress(request_id, progress, step_name)
            await asyncio.sleep(0.5)  # Small delay for progress updates
        
        # Mark optimization as completed
        optimization_service.complete_optimization(request_id, activities)
        
    except Exception as e:
        # In a real application, you'd want better error handling
        optimization_service.update_progress(request_id, 0.0, f"Error: {str(e)}")

@router.post("/start", response_model=dict)
async def start_optimization(
    request: OptimizationRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Start a new supply chain optimization"""
    # Create optimization request with user_id from current_user
    user_id = current_user.get("sub") or current_user.get("preferred_username")
    request_id = optimization_service.create_optimization_request(request, user_id)
    
    # Start background task for optimization
    background_tasks.add_task(run_optimization_workflow, request_id, user_id)
    
    return {
        "request_id": request_id,
        "message": "Optimization started",
        "status": "pending"
    }

@router.get("/progress/{request_id}", response_model=OptimizationProgress)
async def get_optimization_progress(
    request_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get progress of an optimization request"""
    progress = optimization_service.get_optimization_progress(request_id)
    
    if not progress:
        raise HTTPException(
            status_code=404,
            detail="Optimization request not found"
        )
    
    return progress

@router.get("/results/{request_id}", response_model=OptimizationResults)
async def get_optimization_results(
    request_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get results of a completed optimization"""
    results = optimization_service.get_optimization_results(request_id)
    
    if not results:
        raise HTTPException(
            status_code=404,
            detail="Optimization results not found or optimization not completed"
        )
    
    return results

@router.get("/all", response_model=List[OptimizationProgress])
async def get_all_optimizations(current_user: dict = Depends(get_current_user)):
    """Get all optimization requests for the current user"""
    # In a real application, you'd filter by user_id
    optimizations = optimization_service.get_all_optimizations()
    return optimizations

@router.delete("/clear")
async def clear_optimizations(current_user: dict = Depends(get_current_user)):
    """Clear all optimizations (useful for testing)"""
    optimization_service.clear_optimizations()
    return {"message": "All optimizations cleared"}
