import asyncio
import json
import uuid
from typing import AsyncGenerator, Dict, Any, Optional
import httpx
from datetime import datetime

from a2a.client import ClientFactory, ClientConfig
from a2a.types import TransportProtocol, Message, Role
from a2a.client.helpers import create_text_message_object
from a2a.client import minimal_agent_card

from app.config import settings
from app.models import OptimizationRequest, OptimizationProgress, OptimizationResults


class A2AService:
    """Service for communicating with A2A supply-chain optimization agents"""
    
    def __init__(self):
        self.agent_url = settings.supply_chain_agent_url
        self.timeout = httpx.Timeout(
            connect=30.0,      # 30 seconds to establish connection
            read=60.0,         # 1 minute to read response
            write=30.0,        # 30 seconds to write request
            pool=30.0          # 30 seconds for connection pool
        )
    
    async def _create_client(self) -> tuple[Any, httpx.AsyncClient]:
        """Create A2A client and HTTP client"""
        httpx_client = httpx.AsyncClient(timeout=self.timeout)
        
        # Create client configuration
        config = ClientConfig(
            httpx_client=httpx_client,
            supported_transports=[TransportProtocol.jsonrpc],
            streaming=False
        )
        
        # Create client factory
        factory = ClientFactory(config)
        
        # Create agent card
        agent_card = minimal_agent_card(
            url=self.agent_url,
            transports=["JSONRPC"]
        )
        
        # Create client
        client = factory.create(agent_card)
        
        return client, httpx_client
    
    async def optimize_supply_chain(
        self, 
        request: OptimizationRequest, 
        user_id: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Optimize supply chain using A2A agent"""
        
        client, httpx_client = None, None
        
        try:
            # Create A2A client
            client, httpx_client = await self._create_client()
            
            # Create optimization message
            message_content = self._create_optimization_message(request)
            message = create_text_message_object(
                role=Role.user, 
                content=message_content
            )
            
            # Send message to agent and stream responses
            async for event in client.send_message(message):
                # Process the event and yield progress updates
                progress_data = self._process_agent_response(event, request, user_id)
                if progress_data:
                    yield progress_data
                
                # Check if optimization is complete
                if self._is_optimization_complete(event):
                    break
                    
        except Exception as e:
            # Yield error information
            error_data = {
                "type": "error",
                "message": f"Optimization failed: {str(e)}",
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_id
            }
            yield error_data
            
        finally:
            # Clean up HTTP client
            if httpx_client:
                await httpx_client.aclose()
    
    def _create_optimization_message(self, request: OptimizationRequest) -> str:
        """Create optimization message for the A2A agent"""
        
        # Extract constraints from the request
        constraints = []
        if hasattr(request, 'constraints'):
            if hasattr(request.constraints, 'budget_limit'):
                constraints.append(f"budget limit: ${request.constraints.budget_limit:,}")
            if hasattr(request.constraints, 'delivery_time'):
                constraints.append(f"delivery time: {request.constraints.delivery_time}")
            if hasattr(request.constraints, 'quality_requirement'):
                constraints.append(f"quality: {request.constraints.quality_requirement}")
        
        # Create the message
        message_parts = [
            "optimize laptop supply chain",
            f"scenario: {getattr(request, 'scenario', 'laptop_procurement')}"
        ]
        
        if constraints:
            message_parts.append(f"constraints: {', '.join(constraints)}")
        
        return ". ".join(message_parts)
    
    def _process_agent_response(
        self, 
        event: Any, 
        request: OptimizationRequest, 
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """Process agent response and convert to progress data"""
        
        try:
            # Extract relevant information from the event
            # This will depend on the actual A2A response format
            if hasattr(event, 'content') and event.content:
                content = event.content
                if isinstance(content, str):
                    return {
                        "type": "progress",
                        "message": content,
                        "timestamp": datetime.utcnow().isoformat(),
                        "user_id": user_id,
                        "request_id": str(uuid.uuid4())
                    }
                elif isinstance(content, dict):
                    return {
                        "type": "progress",
                        "message": content.get("message", "Processing optimization..."),
                        "data": content,
                        "timestamp": datetime.utcnow().isoformat(),
                        "user_id": user_id,
                        "request_id": str(uuid.uuid4())
                    }
            
            # If no content, return a generic progress update
            return {
                "type": "progress",
                "message": "Agent processing optimization request...",
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_id,
                "request_id": str(uuid.uuid4())
            }
            
        except Exception as e:
            # Return error information
            return {
                "type": "error",
                "message": f"Error processing agent response: {str(e)}",
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_id,
                "request_id": str(uuid.uuid4())
            }
    
    def _is_optimization_complete(self, event: Any) -> bool:
        """Check if the optimization is complete based on the event"""
        
        # This logic will depend on the actual A2A response format
        # For now, we'll assume completion after receiving a response
        # In a real implementation, you'd check for completion indicators
        
        if hasattr(event, 'content'):
            content = event.content
            if isinstance(content, str):
                # Check for completion keywords
                completion_indicators = [
                    "complete", "completed", "finished", "done", 
                    "optimization complete", "recommendations"
                ]
                return any(indicator in content.lower() for indicator in completion_indicators)
            elif isinstance(content, dict):
                # Check for completion status in structured response
                return content.get("status") == "complete" or content.get("completed", False)
        
        return False
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test connection to the A2A agent"""
        try:
            client, httpx_client = await self._create_client()
            
            # Try to get agent card to test connection
            from a2a.client import A2ACardResolver
            resolver = A2ACardResolver(httpx_client, self.agent_url.rstrip('/'))
            agent_card = await resolver.get_agent_card()
            
            await httpx_client.aclose()
            
            return {
                "status": "connected",
                "agent_name": getattr(agent_card, 'name', 'Unknown'),
                "agent_description": getattr(agent_card, 'description', 'No description'),
                "url": self.agent_url
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "url": self.agent_url
            }


# Global instance
a2a_service = A2AService()
