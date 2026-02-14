"""Analytics router."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from datetime import datetime, timedelta

from app.database import get_db
from app.models.user import User
from app.models.watch_history import WatchHistory
from app.models.feedback import UserFeedback
from app.schemas.feedback import (
    FeedbackCreate, FeedbackResponse, WatchEvent,
    WatchHistoryItem, WatchHistoryResponse, AnalyticsSummary, DailyStats
)
from app.routers.auth import get_current_user

router = APIRouter()


@router.post("/watch", status_code=201)
async def track_watch(
    event: WatchEvent,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Track a watch event."""
    watch_percentage = 0.0
    if event.video_duration_seconds > 0:
        watch_percentage = (event.watch_duration_seconds / event.video_duration_seconds) * 100
    
    history = WatchHistory(
        user_id=user.id,
        video_id=event.video_id,
        watch_duration_seconds=event.watch_duration_seconds,
        video_duration_seconds=event.video_duration_seconds,
        watch_percentage=watch_percentage,
        was_skipped=event.was_skipped,
        skip_position_percent=event.skip_position_percent,
        completed=event.completed,
        mode_id=event.mode_id,
    )
    db.add(history)
    await db.commit()
    
    return {"status": "tracked"}


@router.get("/history", response_model=WatchHistoryResponse)
async def get_history(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's watch history."""
    offset = (page - 1) * per_page
    
    # Get total count
    count_result = await db.execute(
        select(func.count()).where(WatchHistory.user_id == user.id)
    )
    total = count_result.scalar()
    
    # Get items
    result = await db.execute(
        select(WatchHistory)
        .where(WatchHistory.user_id == user.id)
        .order_by(WatchHistory.watched_at.desc())
        .offset(offset)
        .limit(per_page)
    )
    items = result.scalars().all()
    
    return WatchHistoryResponse(
        items=[WatchHistoryItem(
            video_id=h.video_id,
            watch_duration_seconds=h.watch_duration_seconds,
            watch_percentage=h.watch_percentage,
            was_skipped=h.was_skipped,
            completed=h.completed,
            watched_at=h.watched_at
        ) for h in items],
        total=total,
        page=page,
        per_page=per_page
    )


@router.post("/feedback", response_model=FeedbackResponse, status_code=201)
async def submit_feedback(
    feedback_data: FeedbackCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Submit feedback on a video."""
    feedback = UserFeedback(
        user_id=user.id,
        video_id=feedback_data.video_id,
        feedback_type=feedback_data.feedback_type,
        reason=feedback_data.reason,
        suggested_category=feedback_data.suggested_category,
    )
    db.add(feedback)
    await db.commit()
    await db.refresh(feedback)
    
    return feedback


@router.get("/summary", response_model=AnalyticsSummary)
async def get_analytics_summary(
    days: int = Query(default=7, ge=1, le=30),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get analytics summary for the user."""
    since = datetime.utcnow() - timedelta(days=days)
    
    # Get basic watch history stats
    result = await db.execute(
        select(
            func.sum(WatchHistory.watch_duration_seconds).label("total_seconds"),
            func.count().label("total_videos"),
            func.avg(WatchHistory.watch_percentage).label("avg_percentage")
        )
        .where(
            WatchHistory.user_id == user.id,
            WatchHistory.watched_at >= since
        )
    )
    stats = result.first()
    
    # Count skipped videos separately
    skipped_result = await db.execute(
        select(func.count())
        .where(
            WatchHistory.user_id == user.id,
            WatchHistory.watched_at >= since,
            WatchHistory.was_skipped == True
        )
    )
    skipped_count = skipped_result.scalar() or 0
    
    # Count completed videos separately
    completed_result = await db.execute(
        select(func.count())
        .where(
            WatchHistory.user_id == user.id,
            WatchHistory.watched_at >= since,
            WatchHistory.completed == True
        )
    )
    completed_count = completed_result.scalar() or 0
    
    # Get daily usage for chart
    daily_result = await db.execute(
        select(
            func.date(WatchHistory.watched_at).label("watch_date"),
            func.sum(WatchHistory.watch_duration_seconds).label("daily_seconds")
        )
        .where(
            WatchHistory.user_id == user.id,
            WatchHistory.watched_at >= since
        )
        .group_by(func.date(WatchHistory.watched_at))
        .order_by(func.date(WatchHistory.watched_at))
    )
    daily_rows = daily_result.all()
    daily_usage = [
        {"date": str(row.watch_date), "minutes": int((row.daily_seconds or 0) / 60)}
        for row in daily_rows
    ]
    
    return AnalyticsSummary(
        total_watch_time_minutes=int((stats.total_seconds or 0) / 60),
        videos_watched=stats.total_videos or 0,
        videos_skipped=skipped_count,
        videos_completed=completed_count,
        average_watch_percentage=float(stats.avg_percentage or 0),
        top_categories=[],  # Would require joining with content cache
        daily_usage=daily_usage,
        focus_mode_usage=[]  # Would require mode grouping
    )


@router.get("/daily", response_model=DailyStats)
async def get_daily_stats(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get today's usage statistics."""
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    result = await db.execute(
        select(
            func.sum(WatchHistory.watch_duration_seconds).label("total_seconds"),
            func.count().label("total_videos")
        )
        .where(
            WatchHistory.user_id == user.id,
            WatchHistory.watched_at >= today_start
        )
    )
    stats = result.first()
    
    # Get active mode time limit
    from app.models.focus_mode import FocusMode
    mode_result = await db.execute(
        select(FocusMode).where(
            FocusMode.user_id == user.id,
            FocusMode.is_active == True
        )
    )
    active_mode = mode_result.scalar_one_or_none()
    
    time_limit = active_mode.daily_time_limit_minutes if active_mode else None
    watch_minutes = int((stats.total_seconds or 0) / 60)
    
    return DailyStats(
        date=today_start.strftime("%Y-%m-%d"),
        watch_time_minutes=watch_minutes,
        videos_watched=stats.total_videos or 0,
        time_limit_minutes=time_limit,
        time_remaining_minutes=max(0, time_limit - watch_minutes) if time_limit else None
    )
