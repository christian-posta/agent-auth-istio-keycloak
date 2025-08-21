import os
from typing import List

class Settings:
    # API Configuration
    api_title: str = "Supply Chain Agent API"
    api_version: str = "1.0.0"
    debug: bool = True
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    # CORS Configuration
    allowed_origins: List[str] = ["http://localhost:3000"]
    
    # Keycloak Configuration
    keycloak_url: str = "http://localhost:8080"
    keycloak_realm: str = "mcp-realm"
    keycloak_client_id: str = "supply-chain-ui"
    
    # Agent Configuration
    max_concurrent_agents: int = 5
    agent_timeout_seconds: int = 300

settings = Settings()
