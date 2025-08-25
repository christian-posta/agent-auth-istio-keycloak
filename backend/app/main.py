from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, agents, optimization

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
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
