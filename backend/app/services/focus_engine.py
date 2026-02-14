"""Focus Engine for managing focus modes and sessions."""
from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.user import User
from app.models.focus_mode import FocusMode
from app.models.watch_history import WatchHistory


class FocusEngine:
    """Engine for managing focus modes and enforcing time limits."""
    
    def __init__(self, db: AsyncSession, user: User):
        self.db = db
        self.user = user
    
    async def get_active_mode(self) -> Optional[FocusMode]:
        """Get the user's currently active focus mode."""
        result = await self.db.execute(
            select(FocusMode).where(
                FocusMode.user_id == self.user.id,
                FocusMode.is_active == True
            )
        )
        return result.scalar_one_or_none()
    
    async def activate_mode(self, mode_id: str) -> FocusMode:
        """Activate a focus mode and deactivate others."""
        # Check if any mode is locked
        locked = await self._get_locked_mode()
        if locked:
            raise ValueError(
                f"Cannot change mode: '{locked.name}' is locked until {locked.lock_until}"
            )
        
        # Deactivate all modes
        result = await self.db.execute(
            select(FocusMode).where(FocusMode.user_id == self.user.id)
        )
        all_modes = result.scalars().all()
        
        for mode in all_modes:
            mode.is_active = False
            mode.is_locked = False
            mode.lock_until = None
        
        # Activate requested mode
        target_mode = None
        for mode in all_modes:
            if str(mode.id) == str(mode_id):
                mode.is_active = True
                target_mode = mode
                break
        
        if not target_mode:
            raise ValueError("Focus mode not found")
        
        await self.db.commit()
        return target_mode
    
    async def lock_session(self, mode_id: str, duration_minutes: int) -> FocusMode:
        """Lock the current focus session for a specified duration."""
        result = await self.db.execute(
            select(FocusMode).where(
                FocusMode.id == mode_id,
                FocusMode.user_id == self.user.id
            )
        )
        mode = result.scalar_one_or_none()
        
        if not mode:
            raise ValueError("Focus mode not found")
        
        if not mode.is_active:
            raise ValueError("Can only lock an active focus mode")
        
        mode.is_locked = True
        mode.lock_until = datetime.utcnow() + timedelta(minutes=duration_minutes)
        
        await self.db.commit()
        return mode
    
    async def unlock_session(self, mode_id: str) -> FocusMode:
        """Force unlock a session (for emergency use)."""
        result = await self.db.execute(
            select(FocusMode).where(
                FocusMode.id == mode_id,
                FocusMode.user_id == self.user.id
            )
        )
        mode = result.scalar_one_or_none()
        
        if not mode:
            raise ValueError("Focus mode not found")
        
        mode.is_locked = False
        mode.lock_until = None
        
        await self.db.commit()
        return mode
    
    async def _get_locked_mode(self) -> Optional[FocusMode]:
        """Check if any mode is currently locked."""
        result = await self.db.execute(
            select(FocusMode).where(
                FocusMode.user_id == self.user.id,
                FocusMode.is_locked == True
            )
        )
        mode = result.scalar_one_or_none()
        
        if mode and mode.lock_until:
            if mode.lock_until > datetime.utcnow():
                return mode
            else:
                # Lock expired, unlock it
                mode.is_locked = False
                mode.lock_until = None
                await self.db.commit()
        
        return None
    
    async def check_time_limit(self, mode: FocusMode) -> dict:
        """Check if user has exceeded daily time limit."""
        if not mode.daily_time_limit_minutes:
            return {
                "has_limit": False,
                "exceeded": False,
                "used_minutes": 0,
                "limit_minutes": None,
                "remaining_minutes": None
            }
        
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        result = await self.db.execute(
            select(func.sum(WatchHistory.watch_duration_seconds))
            .where(
                WatchHistory.user_id == self.user.id,
                WatchHistory.watched_at >= today_start
            )
        )
        total_seconds = result.scalar() or 0
        used_minutes = total_seconds // 60
        
        exceeded = used_minutes >= mode.daily_time_limit_minutes
        remaining = max(0, mode.daily_time_limit_minutes - used_minutes)
        
        return {
            "has_limit": True,
            "exceeded": exceeded,
            "used_minutes": used_minutes,
            "limit_minutes": mode.daily_time_limit_minutes,
            "remaining_minutes": remaining
        }
    
    async def get_session_stats(self) -> dict:
        """Get current session statistics."""
        mode = await self.get_active_mode()
        
        if not mode:
            return {
                "has_active_mode": False,
                "mode": None,
                "time_limit": None,
                "lock_status": None
            }
        
        time_limit = await self.check_time_limit(mode)
        
        lock_status = None
        if mode.is_locked and mode.lock_until:
            remaining_lock = (mode.lock_until - datetime.utcnow()).total_seconds()
            if remaining_lock > 0:
                lock_status = {
                    "is_locked": True,
                    "remaining_minutes": int(remaining_lock // 60),
                    "unlock_at": mode.lock_until.isoformat()
                }
        
        return {
            "has_active_mode": True,
            "mode": {
                "id": str(mode.id),
                "name": mode.name,
                "description": mode.description
            },
            "time_limit": time_limit,
            "lock_status": lock_status
        }
