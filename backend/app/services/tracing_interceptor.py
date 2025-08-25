#!/usr/bin/env python3
"""Tracing interceptor for A2A client calls."""

from typing import Dict, Any
from a2a.client.middleware import ClientCallInterceptor, ClientCallContext
from app.tracing_config import inject_context_to_headers, add_event, set_attribute


class TracingInterceptor(ClientCallInterceptor):
    """Interceptor that injects trace context into HTTP requests."""
    
    def __init__(self, trace_headers: Dict[str, str] = None):
        self.trace_headers = trace_headers or {}
    
    async def intercept(
        self,
        method_name: str,
        request_payload: dict[str, Any],
        http_kwargs: dict[str, Any],
        agent_card: Any | None,
        context: ClientCallContext | None,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Inject trace headers into the HTTP request."""
        headers = http_kwargs.get('headers', {})
        
        # Add custom trace headers if provided
        if self.trace_headers:
            headers.update(self.trace_headers)
        
        # Inject current trace context into headers
        headers = inject_context_to_headers(headers)
        
        # Update http_kwargs with modified headers
        http_kwargs['headers'] = headers
        
        # Add tracing events
        add_event("a2a_client.interceptor.headers_injected", {
            "method_name": method_name,
            "headers_count": len(headers),
            "trace_headers": list(self.trace_headers.keys()) if self.trace_headers else []
        })
        
        set_attribute("a2a_client.interceptor.method", method_name)
        set_attribute("a2a_client.interceptor.headers_count", len(headers))
        
        print(f"🔗 TracingInterceptor: Injected headers for {method_name}")
        return request_payload, http_kwargs
