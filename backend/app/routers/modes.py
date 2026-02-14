"""Focus Modes router."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID
from datetime import datetime, timedelta

from app.database import get_db
from app.models.user import User
from app.models.focus_mode import FocusMode
from app.models.filter_rule import FilterRule
from app.schemas.mode import (
    FocusModeCreate, FocusModeUpdate, FocusModeResponse,
    LockSessionRequest, FilterRuleCreate, FilterRuleResponse
)
from app.routers.auth import get_current_user

router = APIRouter()


# Preset focus modes with all YouTube categories
PRESET_MODES = {
    "study": {
        "name": "Study Mode",
        "description": "Focus on educational content only",
        "allowed_categories": ["EDUCATION"],
        "blocked_categories": ["ENTERTAINMENT", "COMEDY", "GAMING", "MUSIC", "SCIENCE_TECH", "HOWTO_STYLE"],
        "min_duration_seconds": 180,  # 3 minutes (more practical)
        "max_clickbait_score": 0.5,
        "max_entertainment_score": 0.6,
        "block_shorts": True,
        "block_trending": False,
        "blocked_keywords": ["prank", "gone wrong", "challenge"],
    },
    "deep_work": {
        "name": "Deep Work",
        "description": "Maximum focus with strict filtering",
        "allowed_categories": ["EDUCATION", "SCIENCE_TECH"],
        "blocked_categories": ["ENTERTAINMENT", "COMEDY", "GAMING", "NEWS_POLITICS", "MUSIC", "SPORTS"],
        "min_duration_seconds": 300,  # 5 minutes
        "max_clickbait_score": 0.3,
        "max_entertainment_score": 0.4,
        "block_shorts": True,
        "block_trending": True,
        "daily_time_limit_minutes": 60,
    },
    "music": {
        "name": "Music Mode",
        "description": "Background music only",
        "allowed_categories": ["MUSIC"],
        "blocked_categories": [],
        "min_duration_seconds": 0,
        "max_clickbait_score": 1.0,
        "max_entertainment_score": 1.0,
        "block_shorts": False,
        "block_trending": False,
    },
    "relax": {
        "name": "Relax Mode",
        "description": "Controlled leisure with time limits",
        "allowed_categories": [],  # Allow all
        "blocked_categories": ["NEWS_POLITICS"],
        "min_duration_seconds": 0,
        "max_clickbait_score": 0.5,
        "max_entertainment_score": 0.8,
        "block_shorts": True,
        "block_trending": False,
        "daily_time_limit_minutes": 60,
    },
    "gaming": {
        "name": "Gaming Mode",
        "description": "Gaming content only",
        "allowed_categories": ["GAMING", "ENTERTAINMENT"],
        "blocked_categories": [],
        "min_duration_seconds": 0,
        "max_clickbait_score": 0.7,
        "max_entertainment_score": 1.0,
        "block_shorts": False,
        "block_trending": False,
    },
    "news": {
        "name": "News Mode",
        "description": "Stay informed with news content",
        "allowed_categories": ["NEWS_POLITICS", "EDUCATION"],
        "blocked_categories": ["ENTERTAINMENT", "COMEDY", "GAMING"],
        "min_duration_seconds": 0,
        "max_clickbait_score": 0.4,
        "max_entertainment_score": 0.5,
        "block_shorts": True,
        "block_trending": False,
    },
    "fitness": {
        "name": "Fitness Mode", 
        "description": "Sports and fitness content",
        "allowed_categories": ["SPORTS", "HOWTO_STYLE", "PEOPLE_BLOGS"],
        "blocked_categories": ["GAMING", "COMEDY"],
        "min_duration_seconds": 0,
        "max_clickbait_score": 0.5,
        "max_entertainment_score": 0.7,
        "block_shorts": False,
        "block_trending": False,
    },
    "travel": {
        "name": "Travel Mode",
        "description": "Travel and exploration content",
        "allowed_categories": ["TRAVEL_EVENTS", "PEOPLE_BLOGS", "FILM_ANIMATION"],
        "blocked_categories": ["GAMING", "NEWS_POLITICS"],
        "min_duration_seconds": 0,
        "max_clickbait_score": 0.5,
        "max_entertainment_score": 0.8,
        "block_shorts": False,
        "block_trending": False,
    },
    "tech": {
        "name": "Tech Mode",
        "description": "Technology and science content",
        "allowed_categories": ["SCIENCE_TECH", "EDUCATION", "HOWTO_STYLE"],
        "blocked_categories": ["ENTERTAINMENT", "COMEDY"],
        "min_duration_seconds": 300,
        "max_clickbait_score": 0.4,
        "max_entertainment_score": 0.5,
        "block_shorts": True,
        "block_trending": False,
    },
}


@router.get("", response_model=List[FocusModeResponse])
async def list_modes(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all focus modes for the current user."""
    result = await db.execute(
        select(FocusMode).where(FocusMode.user_id == user.id)
    )
    modes = result.scalars().all()
    
    # Create preset modes if user has none
    if not modes:
        for preset_key, preset_data in PRESET_MODES.items():
            mode = FocusMode(user_id=user.id, **preset_data)
            db.add(mode)
        await db.commit()
        
        result = await db.execute(
            select(FocusMode).where(FocusMode.user_id == user.id)
        )
        modes = result.scalars().all()
    
    return modes


@router.post("/reset", response_model=List[FocusModeResponse])
async def reset_modes(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Reset all focus modes to default presets. Deletes all existing modes."""
    # Delete all existing modes for the user
    result = await db.execute(
        select(FocusMode).where(FocusMode.user_id == user.id)
    )
    existing_modes = result.scalars().all()
    for mode in existing_modes:
        await db.delete(mode)
    await db.commit()
    
    # Create fresh preset modes
    new_modes = []
    first_mode = True
    for preset_key, preset_data in PRESET_MODES.items():
        mode = FocusMode(user_id=user.id, is_active=first_mode, **preset_data)
        db.add(mode)
        new_modes.append(mode)
        first_mode = False
    await db.commit()
    
    # Refresh to get IDs
    result = await db.execute(
        select(FocusMode).where(FocusMode.user_id == user.id)
    )
    modes = result.scalars().all()
    
    return modes


@router.post("", response_model=FocusModeResponse, status_code=status.HTTP_201_CREATED)
async def create_mode(
    mode_data: FocusModeCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new focus mode."""
    mode = FocusMode(user_id=user.id, **mode_data.model_dump())
    db.add(mode)
    await db.commit()
    await db.refresh(mode)
    return mode


@router.get("/active", response_model=FocusModeResponse)
async def get_active_mode(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get the currently active focus mode."""
    result = await db.execute(
        select(FocusMode).where(
            FocusMode.user_id == user.id,
            FocusMode.is_active == True
        )
    )
    mode = result.scalar_one_or_none()
    
    if not mode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active focus mode"
        )
    
    return mode


@router.get("/{mode_id}", response_model=FocusModeResponse)
async def get_mode(
    mode_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific focus mode."""
    result = await db.execute(
        select(FocusMode).where(
            FocusMode.id == mode_id,
            FocusMode.user_id == user.id
        )
    )
    mode = result.scalar_one_or_none()
    
    if not mode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Focus mode not found"
        )
    
    return mode


@router.put("/{mode_id}", response_model=FocusModeResponse)
async def update_mode(
    mode_id: UUID,
    mode_data: FocusModeUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a focus mode."""
    result = await db.execute(
        select(FocusMode).where(
            FocusMode.id == mode_id,
            FocusMode.user_id == user.id
        )
    )
    mode = result.scalar_one_or_none()
    
    if not mode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Focus mode not found"
        )
    
    if mode.is_locked and mode.lock_until and mode.lock_until > datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify locked focus mode"
        )
    
    for key, value in mode_data.model_dump(exclude_unset=True).items():
        setattr(mode, key, value)
    
    await db.commit()
    await db.refresh(mode)
    return mode


@router.delete("/{mode_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mode(
    mode_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a focus mode."""
    result = await db.execute(
        select(FocusMode).where(
            FocusMode.id == mode_id,
            FocusMode.user_id == user.id
        )
    )
    mode = result.scalar_one_or_none()
    
    if not mode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Focus mode not found"
        )
    
    await db.delete(mode)
    await db.commit()


@router.post("/{mode_id}/activate", response_model=FocusModeResponse)
async def activate_mode(
    mode_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Activate a focus mode (deactivates others)."""
    # Check if any mode is locked
    result = await db.execute(
        select(FocusMode).where(
            FocusMode.user_id == user.id,
            FocusMode.is_locked == True
        )
    )
    locked_mode = result.scalar_one_or_none()
    
    if locked_mode and locked_mode.lock_until and locked_mode.lock_until > datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Cannot change mode: '{locked_mode.name}' is locked until {locked_mode.lock_until}"
        )
    
    # Deactivate all modes
    result = await db.execute(
        select(FocusMode).where(FocusMode.user_id == user.id)
    )
    all_modes = result.scalars().all()
    for m in all_modes:
        m.is_active = False
        m.is_locked = False
        m.lock_until = None
    
    # Activate the requested mode
    result = await db.execute(
        select(FocusMode).where(
            FocusMode.id == mode_id,
            FocusMode.user_id == user.id
        )
    )
    mode = result.scalar_one_or_none()
    
    if not mode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Focus mode not found"
        )
    
    mode.is_active = True
    await db.commit()
    await db.refresh(mode)
    return mode


@router.post("/{mode_id}/lock", response_model=FocusModeResponse)
async def lock_session(
    mode_id: UUID,
    lock_data: LockSessionRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Lock a focus session (cannot change mode until time expires)."""
    result = await db.execute(
        select(FocusMode).where(
            FocusMode.id == mode_id,
            FocusMode.user_id == user.id
        )
    )
    mode = result.scalar_one_or_none()
    
    if not mode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Focus mode not found"
        )
    
    if not mode.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only lock an active focus mode"
        )
    
    mode.is_locked = True
    mode.lock_until = datetime.utcnow() + timedelta(minutes=lock_data.duration_minutes)
    
    await db.commit()
    await db.refresh(mode)
    return mode


@router.get("/{mode_id}/rules", response_model=List[FilterRuleResponse])
async def list_mode_rules(
    mode_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List filter rules for a focus mode."""
    # Verify mode ownership
    result = await db.execute(
        select(FocusMode).where(
            FocusMode.id == mode_id,
            FocusMode.user_id == user.id
        )
    )
    mode = result.scalar_one_or_none()
    
    if not mode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Focus mode not found"
        )
    
    result = await db.execute(
        select(FilterRule).where(FilterRule.mode_id == mode_id).order_by(FilterRule.priority.desc())
    )
    return result.scalars().all()


@router.post("/{mode_id}/rules", response_model=FilterRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_rule(
    mode_id: UUID,
    rule_data: FilterRuleCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a filter rule for a focus mode."""
    # Verify mode ownership
    result = await db.execute(
        select(FocusMode).where(
            FocusMode.id == mode_id,
            FocusMode.user_id == user.id
        )
    )
    mode = result.scalar_one_or_none()
    
    if not mode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Focus mode not found"
        )
    
    rule = FilterRule(mode_id=mode_id, **rule_data.model_dump())
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return rule
