"""Search suggestions router."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.models.user import User
from app.routers.auth import get_current_user
from app.services.youtube_service import YouTubeService

router = APIRouter()


@router.get("", response_model=List[str])
async def get_suggestions(
    query: str = Query(..., min_length=1, max_length=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get search suggestions based on a query prefix."""
    # Common search prefixes for the YouTube focus engine context
    # In production, this would use YouTube's suggestion API or a custom ML model
    
    q = query.lower()
    
    # Base suggestions for educational/entertainment content
    base_suggestions = [
        # Educational
        "python tutorial",
        "python for beginners",
        "python crash course",
        "programming tutorial",
        "machine learning",
        "data science",
        "web development",
        "react tutorial",
        "javascript tutorial",
        "computer science",
        "coding for beginners",
        "learn to code",
        "algorithms explained",
        "system design",
        
        # Music
        "music playlist",
        "lofi beats",
        "study music",
        "relaxing music",
        "classical music",
        "jazz music",
        "pop music",
        "workout playlist",
        
        # Entertainment
        "funny videos",
        "comedy sketches",
        "stand up comedy",
        "movie trailers",
        "gaming highlights",
        "best moments",
        
        # Productivity
        "productivity tips",
        "study tips",
        "how to focus",
        "time management",
        "morning routine",
    ]
    
    # Filter suggestions that match the query
    matching = [s for s in base_suggestions if s.startswith(q) or q in s]
    
    # Sort by relevance (starts with query first)
    matching.sort(key=lambda x: (0 if x.startswith(q) else 1, len(x)))
    
    return matching[:8]  # Return max 8 suggestions
