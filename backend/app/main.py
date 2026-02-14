"""
FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import get_settings
from app.database import init_db
from app.routers import auth, modes, feed, filter, analytics, suggestions

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    await init_db()
    yield
    # Shutdown
    pass


# Create FastAPI app
app = FastAPI(
    title="FocusTube",
    description="AI-Powered YouTube content filtering and focus management",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}


# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(modes.router, prefix="/api/modes", tags=["Focus Modes"])
app.include_router(feed.router, prefix="/api/feed", tags=["Feed"])
app.include_router(filter.router, prefix="/api/filter", tags=["Filtering"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(suggestions.router, prefix="/api/suggestions", tags=["Suggestions"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
