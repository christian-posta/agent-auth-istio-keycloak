import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from app.models import (
    OptimizationRequest, OptimizationProgress, OptimizationResults,
    OptimizationSummary, PurchaseRecommendation, OptimizationReasoning
)

class OptimizationService:
    def __init__(self):
        self.optimizations: Dict[str, OptimizationProgress] = {}
        self.results: Dict[str, OptimizationResults] = {}
    
    def create_optimization_request(self, request: OptimizationRequest, user_id: str) -> str:
        """Create a new optimization request"""
        request_id = str(uuid.uuid4())
        
        progress = OptimizationProgress(
            request_id=request_id,
            status="pending",
            progress_percentage=0.0,
            current_step="Initializing optimization",
            estimated_completion=None,
            activities=[]
        )
        
        self.optimizations[request_id] = progress
        return request_id
    
    def get_optimization_progress(self, request_id: str) -> Optional[OptimizationProgress]:
        """Get current progress of an optimization request"""
        return self.optimizations.get(request_id)
    
    def update_progress(self, request_id: str, progress_percentage: float, current_step: str):
        """Update the progress of an optimization request"""
        if request_id in self.optimizations:
            self.optimizations[request_id].progress_percentage = progress_percentage
            self.optimizations[request_id].current_step = current_step
    
    def complete_optimization(self, request_id: str, activities: List):
        """Mark optimization as completed and generate results"""
        if request_id in self.optimizations:
            self.optimizations[request_id].status = "completed"
            self.optimizations[request_id].progress_percentage = 100.0
            self.optimizations[request_id].current_step = "Optimization completed"
            self.optimizations[request_id].activities = activities
            
            # Generate results
            results = self._generate_optimization_results(request_id, activities)
            self.results[request_id] = results
    
    def _generate_optimization_results(self, request_id: str, activities: List) -> OptimizationResults:
        """Generate optimization results based on activities"""
        # Mock data - in real implementation, this would be based on actual analysis
        summary = OptimizationSummary(
            total_cost=89750.0,
            expected_delivery="2025-09-15",
            cost_savings=12500.0,
            efficiency=94.0
        )
        
        recommendations = [
            PurchaseRecommendation(
                item="MacBook Pro 14\" M4",
                quantity=25,
                unit_price=2399.0,
                supplier="Apple Business",
                lead_time="7-10 days",
                total=59975.0
            ),
            PurchaseRecommendation(
                item="Dell XPS 13 Plus",
                quantity=15,
                unit_price=1985.0,
                supplier="Dell Direct",
                lead_time="5-7 days",
                total=29775.0
            )
        ]
        
        reasoning = [
            OptimizationReasoning(
                decision="Prioritize MacBook Pro orders",
                agent="market-analysis-agent",
                rationale="Higher employee satisfaction scores and lower support costs"
            ),
            OptimizationReasoning(
                decision="Use Apple Business direct",
                agent="procurement-agent",
                rationale="Best pricing tier achieved with bulk order"
            ),
            OptimizationReasoning(
                decision="Schedule delivery for September 15",
                agent="supply-chain-optimizer",
                rationale="Aligns with Q4 onboarding schedule and budget cycle"
            )
        ]
        
        return OptimizationResults(
            request_id=request_id,
            summary=summary,
            recommendations=recommendations,
            reasoning=reasoning,
            completed_at=datetime.utcnow()
        )
    
    def get_optimization_results(self, request_id: str) -> Optional[OptimizationResults]:
        """Get results of a completed optimization"""
        return self.results.get(request_id)
    
    def get_all_optimizations(self) -> List[OptimizationProgress]:
        """Get all optimization requests"""
        return list(self.optimizations.values())
    
    def clear_optimizations(self):
        """Clear all optimizations (useful for testing)"""
        self.optimizations.clear()
        self.results.clear()

# Global instance
optimization_service = OptimizationService()
