"""Filter router."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User
from app.models.focus_mode import FocusMode
from app.schemas.video import FilterCheckRequest, FilterCheckResponse
from app.routers.auth import get_current_user
from app.services.youtube_service import YouTubeService
from app.services.ai_classifier import AIClassifier
from app.services.filter_engine import FilterEngine

router = APIRouter()


@router.post("/check", response_model=FilterCheckResponse)
async def check_filter(
    request: FilterCheckRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Check if a video passes the current focus mode filters."""
    # Get active mode
    result = await db.execute(
        select(FocusMode).where(
            FocusMode.user_id == user.id,
            FocusMode.is_active == True
        )
    )
    active_mode = result.scalar_one_or_none()
    
    if not active_mode:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active focus mode"
        )
    
    # Initialize services
    youtube_service = YouTubeService()
    ai_classifier = AIClassifier()
    filter_engine = FilterEngine(active_mode)
    
    # Fetch video
    video = await youtube_service.get_video_details(request.video_id)
    
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    # Classify and filter
    classification = await ai_classifier.classify_video(video, db)
    filter_result = filter_engine.check_video(video, classification)
    
    return FilterCheckResponse(
        video_id=request.video_id,
        is_allowed=filter_result["allowed"],
        block_reason=filter_result.get("reason"),
        classification=classification
    )
