import asyncio
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List
from app.models import (
    OptimizationRequest, OptimizationProgress, OptimizationResults
)
from app.services.optimization_service import optimization_service
from app.services.a2a_service import a2a_service
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

async def run_optimization_workflow(request_id: str, user_id: str, request: OptimizationRequest):
    """Background task to run the optimization workflow using A2A agent"""
    try:
        # Update progress to running
        optimization_service.update_progress(request_id, 0.0, "Connecting to A2A supply-chain agent")
        
        # Collect all responses from the A2A agent
        responses = []
        progress_count = 0
        
        async for response in a2a_service.optimize_supply_chain(request, user_id):
            if response["type"] == "progress":
                # Update progress
                progress_count += 1
                progress_percentage = min(progress_count * 20, 90)  # Cap at 90% until completion
                optimization_service.update_progress(
                    request_id, 
                    progress_percentage, 
                    response["message"]
                )
                responses.append(response)
                
            elif response["type"] == "error":
                # Handle error
                optimization_service.update_progress(request_id, 0.0, f"Error: {response['message']}")
                return
        
        # Mark optimization as completed
        optimization_service.update_progress(request_id, 100.0, "Optimization completed by A2A agent")
        
        # Create mock activities from responses for now (can be enhanced later)
        from app.models import AgentActivity, DelegationChain
        activities = []
        for i, response in enumerate(responses):
            activity = AgentActivity(
                id=i + 1,
                timestamp=response["timestamp"],
                agent="a2a-supply-chain-agent",
                action="optimization_step",
                delegation=DelegationChain(sub=user_id, aud="a2a-agent", scope="supply-chain:optimize"),
                status="completed",
                details=response["message"]
            )
            activities.append(activity)
        
        optimization_service.complete_optimization(request_id, activities)
        
    except Exception as e:
        # Update progress with error
        optimization_service.update_progress(request_id, 0.0, f"Error: {str(e)}")
        # Mark as failed
        if request_id in optimization_service.optimizations:
            optimization_service.optimizations[request_id].status = "failed"

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
    background_tasks.add_task(run_optimization_workflow, request_id, user_id, request)
    
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

@router.get("/test-a2a-connection")
async def test_a2a_connection(current_user: dict = Depends(get_current_user)):
    """Test connection to the A2A supply-chain agent"""
    try:
        connection_status = await a2a_service.test_connection()
        return connection_status
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "url": a2a_service.agent_url
        }
