"""Feed router - Uses real YouTube API with demo data fallback."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
import time

from app.database import get_db
from app.models.user import User
from app.models.focus_mode import FocusMode
from app.schemas.video import FeedResponse, FeedItem, VideoResponse
from app.routers.auth import get_current_user
from app.services.youtube_service import YouTubeService
from app.services.ai_classifier import AIClassifier
from app.services.filter_engine import FilterEngine
from app.services.demo_data import get_demo_videos, generate_dynamic_videos

router = APIRouter()


@router.get("", response_model=FeedResponse)
async def get_feed(
    max_results: int = Query(default=20, ge=1, le=50),
    page_token: Optional[str] = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get filtered feed based on active focus mode using real YouTube API."""
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
            detail="No active focus mode. Please activate a mode first."
        )
    
    # Initialize services
    youtube_service = YouTubeService()
    ai_classifier = AIClassifier()
    filter_engine = FilterEngine(active_mode)
    
    use_demo_data = False
    videos = {"items": []}
    next_page_token = None
    
    # Fetch videos from YouTube API
    try:
        if active_mode.allowed_categories:
            # Use categories as search terms to get relevant content
            search_query = " ".join(active_mode.allowed_categories[:2])
            videos = await youtube_service.search_videos(
                query=search_query,
                max_results=max_results * 2,  # Fetch more to account for filtering
                page_token=page_token
            )
        else:
            # Get recommended/trending videos
            videos = await youtube_service.get_recommended_videos(
                max_results=max_results * 2,
                page_token=page_token
            )
            
        # Check if API returned an error
        if "error" in videos:
            use_demo_data = True
        else:
            next_page_token = videos.get("next_page_token")
            
    except Exception as e:
        use_demo_data = True
    
    # Use demo data if YouTube API failed
    if use_demo_data:
        # Parse page token to get page number
        page_num = 0
        if page_token:
            try:
                page_num = int(page_token)
            except:
                page_num = 0
        
        # Use seed based on page for different content per page
        seed = int(time.time() // 300) + page_num * 1000  # Changes every 5 min
        
        # Get demo videos - these are pre-categorized, so we can skip classification
        demo_videos = get_demo_videos(
            categories=active_mode.allowed_categories if active_mode.allowed_categories else None,
            max_results=max_results * 3  # Get more since some may be filtered
        )
        
        # Add dynamically generated videos matching the mode
        dynamic_videos = generate_dynamic_videos(
            categories=active_mode.allowed_categories,
            count=max_results * 2,
            seed=seed
        )
        
        # Combine and shuffle
        all_videos = demo_videos + dynamic_videos
        import random
        random.seed(seed + page_num)
        random.shuffle(all_videos)
        
        # For demo data, skip classification and use pre-assigned categories
        filtered_items = []
        filtered_count = 0
        
        for video in all_videos:
            # Demo videos already have a category assigned based on their source
            video_category = video.get("category", "ENTERTAINMENT")
            
            # Quick check: is this category allowed in the current mode?
            if active_mode.allowed_categories:
                if video_category not in active_mode.allowed_categories:
                    filtered_count += 1
                    continue
            
            # Check blocked categories
            if active_mode.blocked_categories:
                if video_category in active_mode.blocked_categories:
                    filtered_count += 1
                    continue
            
            # Check duration
            duration = video.get("duration_seconds", 0)
            if duration < active_mode.min_duration_seconds:
                filtered_count += 1
                continue
            
            # Check shorts
            if active_mode.block_shorts and video.get("is_short", False):
                filtered_count += 1
                continue
            
            # Passed all checks - add to results
            filtered_items.append(FeedItem(
                video_id=video["id"],
                title=video["title"],
                channel_title=video.get("channel_title"),
                thumbnail_url=video.get("thumbnail_url"),
                duration_seconds=video.get("duration_seconds", 0),
                is_short=video.get("is_short", False),
                view_count=video.get("view_count", 0),
                published_at=video.get("published_at"),
                category=video_category,
                clickbait_score=video.get("clickbait_score", 0.1),
                entertainment_score=video.get("entertainment_score", 0.3),
            ))
            
            if len(filtered_items) >= max_results:
                break
        
        next_page_token = str(page_num + 1)
        
        return FeedResponse(
            items=filtered_items,
            next_page_token=next_page_token,
            total_results=len(filtered_items) + filtered_count,
            filtered_count=filtered_count
        )
    
    # For real YouTube API content, use AI classification
    filtered_items = []
    filtered_count = 0
    
    for video in videos.get("items", []):
        # Classify video with AI
        classification = await ai_classifier.classify_video(video, db)
        
        # Apply focus mode filters
        filter_result = filter_engine.check_video(video, classification)
        
        if filter_result["allowed"]:
            filtered_items.append(FeedItem(
                video_id=video["id"],
                title=video["title"],
                channel_title=video.get("channel_title"),
                thumbnail_url=video.get("thumbnail_url"),
                duration_seconds=video.get("duration_seconds", 0),
                is_short=video.get("is_short", False),
                view_count=video.get("view_count", 0),
                published_at=video.get("published_at"),
                category=classification.category,
                clickbait_score=classification.clickbait_score,
                entertainment_score=classification.entertainment_score,
            ))
            
            if len(filtered_items) >= max_results:
                break
        else:
            filtered_count += 1
    
    return FeedResponse(
        items=filtered_items,
        next_page_token=next_page_token,
        total_results=len(filtered_items) + filtered_count,
        filtered_count=filtered_count
    )


@router.get("/search", response_model=FeedResponse)
async def search_feed(
    query: str = Query(..., min_length=1, max_length=500),
    max_results: int = Query(default=20, ge=1, le=50),
    page_token: Optional[str] = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Search videos with filters applied based on active focus mode."""
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
            detail="No active focus mode. Please activate a mode first."
        )
    
    # Initialize services
    youtube_service = YouTubeService()
    ai_classifier = AIClassifier()
    filter_engine = FilterEngine(active_mode)
    
    # Search videos from YouTube API
    try:
        videos = await youtube_service.search_videos(
            query=query,
            max_results=max_results * 2,
            page_token=page_token
        )
        
        if "error" in videos:
            error_msg = videos.get("error", {})
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"YouTube API error: {error_msg.get('message', 'Unknown error')}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to search videos: {str(e)}"
        )
    
    # Filter and classify
    filtered_items = []
    filtered_count = 0
    
    for video in videos.get("items", []):
        classification = await ai_classifier.classify_video(video, db)
        filter_result = filter_engine.check_video(video, classification)
        
        if filter_result["allowed"]:
            filtered_items.append(FeedItem(
                video_id=video["id"],
                title=video["title"],
                channel_title=video.get("channel_title"),
                thumbnail_url=video.get("thumbnail_url"),
                duration_seconds=video.get("duration_seconds", 0),
                is_short=video.get("is_short", False),
                view_count=video.get("view_count", 0),
                published_at=video.get("published_at"),
                category=classification.category,
                clickbait_score=classification.clickbait_score,
                entertainment_score=classification.entertainment_score,
            ))
            
            if len(filtered_items) >= max_results:
                break
        else:
            filtered_count += 1
    
    return FeedResponse(
        items=filtered_items,
        next_page_token=videos.get("next_page_token"),
        total_results=videos.get("total_results"),
        filtered_count=filtered_count
    )


@router.get("/video/{video_id}", response_model=VideoResponse)
async def get_video(
    video_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get video details with AI classification and filter status."""
    # Get active mode
    result = await db.execute(
        select(FocusMode).where(
            FocusMode.user_id == user.id,
            FocusMode.is_active == True
        )
    )
    active_mode = result.scalar_one_or_none()
    
    # Initialize services
    youtube_service = YouTubeService()
    ai_classifier = AIClassifier()
    
    # Fetch video details from YouTube
    video = await youtube_service.get_video_details(video_id)
    
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    # Classify with AI
    classification = await ai_classifier.classify_video(video, db)
    
    # Check filter if mode is active
    is_allowed = True
    block_reason = None
    
    if active_mode:
        filter_engine = FilterEngine(active_mode)
        filter_result = filter_engine.check_video(video, classification)
        is_allowed = filter_result["allowed"]
        block_reason = filter_result.get("reason")
    
    return VideoResponse(
        video_id=video["id"],
        title=video["title"],
        description=video.get("description"),
        channel_id=video.get("channel_id"),
        channel_title=video.get("channel_title"),
        thumbnail_url=video.get("thumbnail_url"),
        duration_seconds=video.get("duration_seconds", 0),
        is_short=video.get("is_short", False),
        language=video.get("language"),
        view_count=video.get("view_count", 0),
        like_count=video.get("like_count", 0),
        published_at=video.get("published_at"),
        classification=classification,
        is_allowed=is_allowed,
        block_reason=block_reason
    )
