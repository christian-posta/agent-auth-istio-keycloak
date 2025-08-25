import asyncio
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List
from app.models import (
    OptimizationRequest, OptimizationProgress, OptimizationResults, OptimizationStatus, AgentStatus
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
        print(f"🔄 Starting optimization workflow for request: {request_id}")
        print(f"👤 User ID: {user_id}")
        print(f"📋 Request: {request}")
        
        # Update progress to running
        optimization_service.update_progress(request_id, 0.0, "Connecting to A2A supply-chain agent")
        print("📊 Progress updated: Connecting to A2A agent")
        
        # Get response from A2A agent
        print("🤖 Calling A2A service...")
        response = await a2a_service.optimize_supply_chain(request, user_id)
        print(f"📨 A2A service response: {response}")
        
        if response["type"] == "success":
            print("✅ A2A optimization successful")
            # Update progress to completed
            optimization_service.update_progress(request_id, 100.0, "Optimization completed by A2A agent")
            print("📊 Progress updated: Optimization completed")
            
            # Create activity from A2A agent response
            from app.models import AgentActivity, DelegationChain
            activity = AgentActivity(
                id=1,
                timestamp=response["timestamp"],
                agent="a2a-supply-chain-agent",
                action="supply_chain_optimization",
                delegation=DelegationChain(sub=user_id, aud="a2a-agent", scope="supply-chain:optimize"),
                status=AgentStatus.COMPLETED,
                details=response["agent_response"]
            )
            print(f"📝 Created activity: {activity}")
            
            print("🎯 Calling complete_optimization...")
            optimization_service.complete_optimization(request_id, [activity])
            print("🎯 Optimization marked as completed")
            
            # Verify results were created
            print("🔍 Verifying results were created...")
            results = optimization_service.get_optimization_results(request_id)
            if results:
                print(f"✅ Results found: {results}")
            else:
                print("❌ No results found after completion")
            
        elif response["type"] == "error":
            print(f"❌ A2A optimization failed: {response['message']}")
            # Handle error
            optimization_service.update_progress(request_id, 0.0, f"Error: {response['message']}")
            if request_id in optimization_service.optimizations:
                optimization_service.optimizations[request_id].status = OptimizationStatus.FAILED
            print("📊 Progress updated: Optimization failed")
        
    except Exception as e:
        print(f"💥 Exception in optimization workflow: {e}")
        print(f"💥 Exception type: {type(e)}")
        import traceback
        traceback.print_exc()
        # Update progress with error
        optimization_service.update_progress(request_id, 0.0, f"Error: {str(e)}")
        # Mark as failed
        if request_id in optimization_service.optimizations:
            optimization_service.optimizations[request_id].status = OptimizationStatus.FAILED
        print("📊 Progress updated: Exception occurred")

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
    print(f"🔍 Results endpoint called for request: {request_id}")
    print(f"👤 Current user: {current_user}")
    
    results = optimization_service.get_optimization_results(request_id)
    print(f"📋 Results returned from service: {results}")
    
    if not results:
        print(f"❌ No results found for request: {request_id}")
        raise HTTPException(
            status_code=404,
            detail="Optimization results not found or optimization not completed"
        )
    
    print(f"✅ Returning results for request: {request_id}")
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
