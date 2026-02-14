"""Personalization service for learning user preferences."""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.user import User
from app.models.watch_history import WatchHistory
from app.models.feedback import UserFeedback
from app.models.content_cache import ContentCache


class PersonalizationService:
    """Service for learning and applying user preferences."""
    
    def __init__(self, db: AsyncSession, user: User):
        self.db = db
        self.user = user
    
    async def get_user_preferences(self) -> Dict:
        """Analyze user behavior to determine preferences."""
        # Get watch history stats
        history_stats = await self._analyze_watch_history()
        
        # Get feedback stats
        feedback_stats = await self._analyze_feedback()
        
        # Calculate preferences
        preferences = {
            "preferred_categories": [],
            "avoided_categories": [],
            "preferred_duration_range": {"min": 0, "max": 3600},
            "skip_threshold": 0.3,  # Videos skipped before 30% are bad
            "engagement_patterns": {}
        }
        
        # Determine preferred categories from completed videos
        if history_stats.get("completed_by_category"):
            sorted_cats = sorted(
                history_stats["completed_by_category"].items(),
                key=lambda x: x[1],
                reverse=True
            )
            preferences["preferred_categories"] = [c[0] for c in sorted_cats[:3]]
        
        # Determine avoided categories from skipped videos
        if history_stats.get("skipped_by_category"):
            sorted_cats = sorted(
                history_stats["skipped_by_category"].items(),
                key=lambda x: x[1],
                reverse=True
            )
            preferences["avoided_categories"] = [c[0] for c in sorted_cats[:3]]
        
        # Add explicitly disliked categories from feedback
        if feedback_stats.get("disliked_categories"):
            for cat in feedback_stats["disliked_categories"]:
                if cat not in preferences["avoided_categories"]:
                    preferences["avoided_categories"].append(cat)
        
        return preferences
    
    async def _analyze_watch_history(self, days: int = 30) -> Dict:
        """Analyze watch history patterns."""
        since = datetime.utcnow() - timedelta(days=days)
        
        # Get watch history with content cache
        result = await self.db.execute(
            select(WatchHistory, ContentCache)
            .join(ContentCache, WatchHistory.video_id == ContentCache.video_id, isouter=True)
            .where(
                WatchHistory.user_id == self.user.id,
                WatchHistory.watched_at >= since
            )
        )
        rows = result.all()
        
        completed_by_category = {}
        skipped_by_category = {}
        duration_preferences = []
        
        for watch, content in rows:
            category = content.category if content else "UNKNOWN"
            
            if watch.completed:
                completed_by_category[category] = completed_by_category.get(category, 0) + 1
                if content:
                    duration_preferences.append(content.duration_seconds)
            
            if watch.was_skipped:
                skipped_by_category[category] = skipped_by_category.get(category, 0) + 1
        
        return {
            "completed_by_category": completed_by_category,
            "skipped_by_category": skipped_by_category,
            "avg_preferred_duration": sum(duration_preferences) / len(duration_preferences) if duration_preferences else 0,
            "total_videos": len(rows)
        }
    
    async def _analyze_feedback(self, days: int = 30) -> Dict:
        """Analyze explicit user feedback."""
        since = datetime.utcnow() - timedelta(days=days)
        
        result = await self.db.execute(
            select(UserFeedback, ContentCache)
            .join(ContentCache, UserFeedback.video_id == ContentCache.video_id, isouter=True)
            .where(
                UserFeedback.user_id == self.user.id,
                UserFeedback.created_at >= since
            )
        )
        rows = result.all()
        
        liked_categories = []
        disliked_categories = []
        
        for feedback, content in rows:
            category = content.category if content else None
            
            if feedback.feedback_type == "like" and category:
                liked_categories.append(category)
            elif feedback.feedback_type in ("dislike", "not_interested") and category:
                disliked_categories.append(category)
        
        return {
            "liked_categories": list(set(liked_categories)),
            "disliked_categories": list(set(disliked_categories)),
            "total_feedback": len(rows)
        }
    
    async def adjust_scores(
        self,
        video_id: str,
        classification: Dict
    ) -> Dict:
        """Adjust AI scores based on learned preferences."""
        preferences = await self.get_user_preferences()
        
        # Start with original scores
        adjusted = classification.copy()
        
        category = classification.get("category", "")
        
        # Boost preferred categories
        if category in preferences.get("preferred_categories", []):
            adjusted["preference_boost"] = 0.2
        
        # Penalize avoided categories
        if category in preferences.get("avoided_categories", []):
            adjusted["preference_penalty"] = 0.3
        
        return adjusted
    
    async def get_personalized_ranking(
        self,
        videos: List[Dict]
    ) -> List[Dict]:
        """Re-rank videos based on user preferences."""
        preferences = await self.get_user_preferences()
        
        scored_videos = []
        for video in videos:
            score = 1.0
            
            category = video.get("category", "")
            
            # Boost preferred categories
            if category in preferences.get("preferred_categories", []):
                score += 0.5
            
            # Penalize avoided categories
            if category in preferences.get("avoided_categories", []):
                score -= 0.5
            
            # Factor in engagement scores
            depth = video.get("depth_score", 0.5)
            score += depth * 0.3
            
            clickbait = video.get("clickbait_score", 0)
            score -= clickbait * 0.4
            
            scored_videos.append({
                **video,
                "personalization_score": score
            })
        
        # Sort by personalization score
        sorted_videos = sorted(
            scored_videos,
            key=lambda x: x["personalization_score"],
            reverse=True
        )
        
        return sorted_videos
