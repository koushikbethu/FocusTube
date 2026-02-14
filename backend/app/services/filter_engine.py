"""Filter Engine for enforcing focus mode rules."""
from typing import Dict, Any
from app.models.focus_mode import FocusMode
from app.schemas.video import VideoClassification


class FilterEngine:
    """Hard filtering engine based on focus mode configuration."""
    
    def __init__(self, mode: FocusMode):
        self.mode = mode
    
    def check_video(
        self,
        video: Dict[str, Any],
        classification: VideoClassification
    ) -> Dict[str, Any]:
        """
        Check if video passes all filter rules.
        
        Returns:
            {
                "allowed": bool,
                "reason": str (if blocked)
            }
        """
        # Step 1: Check if video is a Short
        if self.mode.block_shorts and video.get("is_short", False):
            return {
                "allowed": False,
                "reason": "Shorts are blocked in this focus mode"
            }
        
        # Step 2: Duration check
        duration = video.get("duration_seconds", 0)
        if duration < self.mode.min_duration_seconds:
            return {
                "allowed": False,
                "reason": f"Video too short (minimum {self.mode.min_duration_seconds // 60} minutes required)"
            }
        
        # Step 3: Category check
        category = classification.category
        
        # Check blocked categories
        if self.mode.blocked_categories:
            if category in self.mode.blocked_categories:
                return {
                    "allowed": False,
                    "reason": f"Category '{category}' is blocked in this focus mode"
                }
        
        # Check allowed categories (if specified, only these are allowed)
        if self.mode.allowed_categories:
            if category not in self.mode.allowed_categories:
                return {
                    "allowed": False,
                    "reason": f"Category '{category}' is not allowed in this focus mode"
                }
        
        # Step 4: Language check
        if self.mode.allowed_languages:
            video_lang = video.get("language", "")
            if video_lang and video_lang not in self.mode.allowed_languages:
                return {
                    "allowed": False,
                    "reason": f"Language '{video_lang}' is not allowed in this focus mode"
                }
        
        # Step 5: Clickbait score check
        if classification.clickbait_score > self.mode.max_clickbait_score:
            return {
                "allowed": False,
                "reason": f"Video detected as clickbait (score: {classification.clickbait_score:.2f})"
            }
        
        # Step 6: Entertainment score check
        if classification.entertainment_score > self.mode.max_entertainment_score:
            return {
                "allowed": False,
                "reason": f"Video too entertaining for this focus mode (score: {classification.entertainment_score:.2f})"
            }
        
        # Step 7: Blocked keywords check
        if self.mode.blocked_keywords:
            title_lower = video.get("title", "").lower()
            description_lower = video.get("description", "").lower()
            
            for keyword in self.mode.blocked_keywords:
                keyword_lower = keyword.lower()
                if keyword_lower in title_lower or keyword_lower in description_lower:
                    return {
                        "allowed": False,
                        "reason": f"Video contains blocked keyword: '{keyword}'"
                    }
        
        # Step 8: Trending check
        # Note: We'd need to mark videos as trending from the API
        # For now, this is handled at the feed level
        
        # All checks passed
        return {"allowed": True}
    
    def get_filter_summary(self) -> Dict[str, Any]:
        """Get a summary of active filters for display."""
        return {
            "mode_name": self.mode.name,
            "block_shorts": self.mode.block_shorts,
            "block_trending": self.mode.block_trending,
            "min_duration_minutes": self.mode.min_duration_seconds // 60,
            "max_clickbait_score": self.mode.max_clickbait_score,
            "max_entertainment_score": self.mode.max_entertainment_score,
            "allowed_categories": self.mode.allowed_categories,
            "blocked_categories": self.mode.blocked_categories,
            "allowed_languages": self.mode.allowed_languages,
            "blocked_keywords_count": len(self.mode.blocked_keywords or []),
            "daily_time_limit_minutes": self.mode.daily_time_limit_minutes,
            "is_locked": self.mode.is_locked,
        }
