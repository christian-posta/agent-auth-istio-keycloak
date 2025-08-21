from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

# Enums
class AgentStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class OptimizationStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

# Authentication Models
class UserLogin(BaseModel):
    username: str = Field(..., description="Username for authentication")
    password: str = Field(..., description="Password for authentication")

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    role: str
    is_active: bool

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

# Agent Models
class DelegationChain(BaseModel):
    sub: str
    aud: str
    scope: str
    act: Optional['DelegationChain'] = None

class AgentActivity(BaseModel):
    id: int
    timestamp: datetime
    agent: str
    action: str
    delegation: DelegationChain
    status: AgentStatus
    details: str

class AgentStatusResponse(BaseModel):
    agent_id: str
    status: AgentStatus
    last_activity: Optional[datetime] = None
    current_task: Optional[str] = None

# Optimization Models
class OptimizationRequest(BaseModel):
    optimization_type: str = "laptop_supply_chain"
    parameters: Optional[Dict[str, Any]] = None

class OptimizationProgress(BaseModel):
    request_id: str
    status: OptimizationStatus
    progress_percentage: float
    current_step: str
    estimated_completion: Optional[datetime] = None
    activities: List[AgentActivity] = []

class PurchaseRecommendation(BaseModel):
    item: str
    quantity: int
    unit_price: float
    supplier: str
    lead_time: str
    total: float

class OptimizationReasoning(BaseModel):
    decision: str
    agent: str
    rationale: str

class OptimizationSummary(BaseModel):
    total_cost: float
    expected_delivery: str
    cost_savings: float
    efficiency: float

class OptimizationResults(BaseModel):
    request_id: str
    summary: OptimizationSummary
    recommendations: List[PurchaseRecommendation]
    reasoning: List[OptimizationReasoning]
    completed_at: datetime

# Response Models
class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    error: Optional[str] = None

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int
