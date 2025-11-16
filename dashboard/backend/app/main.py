from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import alerts, fl_status, mitre, predictions, test_events, websocket
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Starting ICS Threat Detection API...")
    yield
    # Shutdown
    print("👋 Shutting down ICS Threat Detection API...")


app = FastAPI(
    title="ICS Threat Detection API",
    description="Federated Network-Based ICS Threat Detection System",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ICS Threat Detection API",
        "version": "1.0.0",
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "ICS Threat Detection API",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/ws/status")
async def websocket_status():
    """Get WebSocket connection status"""
    from app.websocket.manager import manager

    return {
        "active_connections": len(manager.active_connections),
        "rooms": {room: len(connections) for room, connections in manager.rooms.items()},
        "total_rooms": len(manager.rooms),
    }


# Include routers
app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])
app.include_router(fl_status.router, prefix="/api/fl", tags=["fl"])
app.include_router(predictions.router, prefix="/api/predictions", tags=["predictions"])
app.include_router(mitre.router)
app.include_router(websocket.router, tags=["websocket"])
app.include_router(test_events.router, prefix="/api", tags=["test-events"])
