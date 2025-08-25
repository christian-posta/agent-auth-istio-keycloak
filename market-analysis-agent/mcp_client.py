"""
MCP Client for Market Analysis Agent

This module uses the official Model Context Protocol Python SDK to communicate
with MCP servers and discover available tools.
"""

import logging
from typing import Dict, Any, List, Optional
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

logger = logging.getLogger(__name__)

# Configuration
MCP_SERVER_BASE_URL = "http://localhost:3000"
MCP_SERVER_PATH = "/general/mcp"


class MCPClient:
    """Client for communicating with MCP servers using the official SDK."""
    
    def __init__(self, base_url: str = MCP_SERVER_BASE_URL, mcp_path: str = MCP_SERVER_PATH):
        self.base_url = base_url
        self.mcp_path = mcp_path
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
        
    async def discover_tools(self) -> List[Dict[str, Any]]:
        """
        Discover available tools from the MCP server.
        
        Returns:
            List of available tools with their descriptions
            
        Raises:
            Exception: If connection to MCP server fails
        """
        try:
            # Use the official MCP SDK to connect and discover tools
            async with streamablehttp_client(f"{self.base_url}{self.mcp_path}") as (read, write, _):
                async with ClientSession(read, write) as session:
                    # Initialize the connection
                    await session.initialize()
                    
                    # List available tools
                    tools_response = await session.list_tools()
                    
                    # Format tools for our response
                    tools = []
                    for tool in tools_response.tools:
                        tool_info = {
                            "name": tool.name,
                            "description": tool.description or "No description available",
                            "type": "tool"
                        }
                        
                        # Add additional metadata if available
                        if hasattr(tool, 'title') and tool.title:
                            tool_info["display_name"] = tool.title
                        if hasattr(tool, 'annotations') and tool.annotations:
                            tool_info["annotations"] = tool.annotations
                            
                        tools.append(tool_info)
                    
                    return tools
                    
        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {e}")
            raise Exception("Could not connect to MCP servers")
