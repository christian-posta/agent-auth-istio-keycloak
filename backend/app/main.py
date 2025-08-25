from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api import auth, agents, optimization
from app.tracing_config import initialize_tracing
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize tracing before creating the FastAPI app
jaeger_host = os.getenv("JAEGER_HOST", "localhost")  # Default to localhost for development
jaeger_port = int(os.getenv("JAEGER_PORT", "4317"))

print(f"🔗 Initializing tracing with Jaeger at {jaeger_host}:{jaeger_port}")
print(f"🔗 Environment variables loaded from .env file")
print(f"🔗 JAEGER_HOST: {os.getenv('JAEGER_HOST', 'NOT SET')}")
print(f"🔗 JAEGER_PORT: {os.getenv('JAEGER_PORT', 'NOT SET')}")

initialize_tracing(
    service_name="supply-chain-backend",
    jaeger_host=jaeger_host,
    jaeger_port=jaeger_port,
    enable_console_exporter=True
)

app = FastAPI(
    title="Supply Chain Agent API",
    description="Backend API for supply chain optimization with agent workflows",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server (default)
        "http://localhost:3050",  # React dev server (custom port)
        "http://127.0.0.1:3000", # Alternative localhost
        "http://127.0.0.1:3050", # Alternative localhost
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:5173", # Alternative localhost
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Global exception handler to ensure CORS headers are always present
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler that ensures CORS headers are always present"""
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc),
            "type": type(exc).__name__
        }
    )

# Preflight handler for CORS
@app.options("/{full_path:path}")
async def preflight_handler(request: Request):
    """Handle preflight OPTIONS requests for CORS"""
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Credentials": "true",
        }
    )

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(agents.router, prefix="/agents", tags=["Agents"])
app.include_router(optimization.router, prefix="/optimization", tags=["Optimization"])

@app.get("/")
async def root():
    return {"message": "Supply Chain Agent API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "supply-chain-api"}

def main():
    """Main function to run the FastAPI server with uvicorn"""
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()
