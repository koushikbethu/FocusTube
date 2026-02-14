"""AI Content Classifier using Gemini API."""
import json
import google.generativeai as genai
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta

from app.config import get_settings
from app.models.content_cache import ContentCache
from app.schemas.video import VideoClassification

settings = get_settings()


class AIClassifier:
    """AI-powered video content classifier using Gemini."""
    
    CATEGORIES = [
        "EDUCATION", "STUDY", "TECH", "MUSIC", "PODCAST",
        "NEWS", "ENTERTAINMENT", "MEME", "CLICKBAIT", "GAMING"
    ]
    
    CLASSIFICATION_PROMPT = """You are a video content classifier. Analyze the following video metadata and classify it.

VIDEO INFORMATION:
Title: {title}
Description: {description}
Tags: {tags}
Channel: {channel}
Duration: {duration} seconds
{transcript_section}

TASK: Classify this video and provide scores. Respond ONLY with valid JSON in this exact format:
{{
    "category": "one of: EDUCATION, STUDY, TECH, MUSIC, PODCAST, NEWS, ENTERTAINMENT, MEME, CLICKBAIT, GAMING",
    "confidence_score": 0.0 to 1.0 (how confident you are in the classification),
    "entertainment_score": 0.0 to 1.0 (0 = purely educational, 1 = purely entertainment),
    "depth_score": 0.0 to 1.0 (0 = shallow/superficial, 1 = deep/informative),
    "clickbait_score": 0.0 to 1.0 (0 = no clickbait, 1 = extreme clickbait)
}}

CLASSIFICATION GUIDELINES:
- EDUCATION: Formal courses, tutorials, lectures from educational channels
- STUDY: Academic content, research, study techniques
- TECH: Technology reviews, coding tutorials, tech news
- MUSIC: Songs, albums, concerts, music videos
- PODCAST: Long-form discussions, interviews (usually 20+ minutes)
- NEWS: Current events, news analysis
- ENTERTAINMENT: General entertainment, vlogs, comedy (not meme)
- MEME: Short viral content, memes, compilations
- CLICKBAIT: Sensationalized titles, misleading thumbnails, low value
- GAMING: Game streams, reviews, gameplay

Clickbait indicators:
- ALL CAPS words in title
- Excessive punctuation (!!!, ???)
- Phrases like "You won't believe", "Gone wrong", "SHOCKING"
- Misleading or sensationalized claims

Respond with ONLY the JSON, no other text."""
    
    def __init__(self):
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    async def classify_video(
        self,
        video: Dict[str, Any],
        db: AsyncSession,
        force_refresh: bool = False,
        use_ai: bool = False  # Default to fast heuristic mode
    ) -> VideoClassification:
        """Classify a video using cache, heuristics, or AI.
        
        For speed, uses heuristics by default. Set use_ai=True for Gemini API.
        """
        video_id = video.get("id")
        
        # Check cache first
        if not force_refresh:
            cached = await self._get_cached(video_id, db)
            if cached:
                return VideoClassification(
                    category=cached.category,
                    confidence_score=cached.confidence_score,
                    entertainment_score=cached.entertainment_score,
                    depth_score=cached.depth_score,
                    clickbait_score=cached.clickbait_score,
                )
        
        # Use fast heuristic classification by default for speed
        if not use_ai:
            classification = self._fallback_classification(video)
            # Cache result in background (don't await)
            await self._cache_result(video, classification, db)
            return classification
        
        # Classify with AI (slower but more accurate)
        classification = await self._classify_with_ai(video)
        
        # Cache result
        await self._cache_result(video, classification, db)
        
        return classification
    
    async def _get_cached(
        self,
        video_id: str,
        db: AsyncSession
    ) -> Optional[ContentCache]:
        """Get cached classification if not expired."""
        result = await db.execute(
            select(ContentCache).where(ContentCache.video_id == video_id)
        )
        cached = result.scalar_one_or_none()
        
        if cached and not cached.is_expired():
            return cached
        
        return None
    
    async def _classify_with_ai(self, video: Dict[str, Any]) -> VideoClassification:
        """Classify video content using Gemini API."""
        # Build transcript section if available
        transcript = video.get("transcript", "")
        transcript_section = ""
        if transcript:
            # Limit transcript length for API
            transcript_preview = transcript[:2000]
            transcript_section = f"\nTranscript Preview (first 2000 chars):\n{transcript_preview}"
        
        # Format prompt
        prompt = self.CLASSIFICATION_PROMPT.format(
            title=video.get("title", ""),
            description=video.get("description", "")[:500],  # Limit description
            tags=", ".join(video.get("tags", [])[:20]),  # Limit tags
            channel=video.get("channel_title", "Unknown"),
            duration=video.get("duration_seconds", 0),
            transcript_section=transcript_section
        )
        
        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            # Parse JSON response
            # Handle potential markdown code blocks
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
                text = text.strip()
            
            result = json.loads(text)
            
            # Validate and normalize
            category = result.get("category", "ENTERTAINMENT").upper()
            if category not in self.CATEGORIES:
                category = "ENTERTAINMENT"
            
            return VideoClassification(
                category=category,
                confidence_score=min(1.0, max(0.0, float(result.get("confidence_score", 0.5)))),
                entertainment_score=min(1.0, max(0.0, float(result.get("entertainment_score", 0.5)))),
                depth_score=min(1.0, max(0.0, float(result.get("depth_score", 0.5)))),
                clickbait_score=min(1.0, max(0.0, float(result.get("clickbait_score", 0.0)))),
            )
        
        except Exception as e:
            # Fallback classification
            return self._fallback_classification(video)
    
    def _fallback_classification(self, video: Dict[str, Any]) -> VideoClassification:
        """Smart rule-based classification with proper priority ordering.
        
        PRIORITY ORDER (first match wins):
        1. MUSIC - Check for songs/music first (most commonly misclassified)
        2. GAMING - Gaming content
        3. ENTERTAINMENT - General entertainment
        4. COMEDY - Comedy content
        5. Then check educational/study content
        """
        title = video.get("title", "").lower()
        original_title = video.get("title", "")
        description = video.get("description", "").lower()[:500]
        tags = [t.lower() for t in video.get("tags", [])]
        channel = video.get("channel_title", "").lower()
        duration = video.get("duration_seconds", 0)
        
        # Default values
        category = "ENTERTAINMENT"
        clickbait_score = 0.1
        entertainment_score = 0.5
        depth_score = 0.5
        
        # Combined text for keyword matching
        text = f"{title} {' '.join(tags)} {description} {channel}"
        
        # ============= PRIORITY 1: MUSIC DETECTION =============
        # Check music FIRST because songs are often misclassified as education
        music_keywords = [
            # Direct music indicators
            "song", "music", "album", "concert", "lyrics", "lyrical", "audio",
            "official video", "official audio", "music video", "full song",
            "video song", "vedio song",  # Common typo
            # Music genres
            "lofi", "lo-fi", "hip hop", "rap", "rock", "pop", "jazz", "classical",
            "edm", "dubstep", "remix", "cover", "acoustic", "instrumental",
            # Indian/Regional music 
            "tollywood", "bollywood", "kollywood", "sandalwood",
            "telugu", "hindi", "tamil", "kannada", "malayalam", "bhojpuri",
            "item song", "romantic song", "melody", "gaana", "gana",
            "promo song", "title song", "theme song", "trending song",
            # Artist/Music terms
            "singer", "vocalist", "rapper", "dj", "producer",
            "beats", "track", "playlist", "mixtape",
            # Performance
            "live performance", "stage", "concert", "mtv", "spotify", "gaana",
        ]
        
        for kw in music_keywords:
            if kw in text:
                category = "MUSIC"
                entertainment_score = 0.8
                depth_score = 0.2
                break
        
        # Also check for music-related channel names
        music_channel_indicators = [
            "music", "records", "audio", "songs", "entertainment", "media",
            "films", "pictures", "studios", "mangavaram", "lahari", "aditya",
            "zee", "t-series", "sony", "tips", "saregama", "eros"
        ]
        if category != "MUSIC":
            for ind in music_channel_indicators:
                if ind in channel:
                    category = "MUSIC"
                    entertainment_score = 0.7
                    depth_score = 0.3
                    break
        
        # ============= PRIORITY 2: GAMING DETECTION =============
        if category == "ENTERTAINMENT":  # Only check if not already music
            gaming_keywords = [
                "gameplay", "gaming", "playthrough", "stream", "gamer", "game",
                "walkthrough", "let's play", "esports", "twitch", "streamer",
                "minecraft", "fortnite", "valorant", "gta", "cod", "pubg",
                "elden ring", "zelda", "pokemon", "nintendo", "playstation", "xbox",
                "speedrun", "pro player", "rank", "competitive"
            ]
            for kw in gaming_keywords:
                if kw in text:
                    category = "GAMING"
                    entertainment_score = 0.8
                    depth_score = 0.3
                    break
        
        # ============= PRIORITY 3: COMEDY/ENTERTAINMENT DETECTION =============
        if category == "ENTERTAINMENT":
            comedy_keywords = [
                "comedy", "funny", "laugh", "humor", "joke", "stand up", "skit",
                "prank", "roast", "meme", "compilation", "try not to laugh",
                "fails", "bloopers", "reaction", "challenge"
            ]
            for kw in comedy_keywords:
                if kw in text:
                    category = "COMEDY"
                    entertainment_score = 0.9
                    depth_score = 0.1
                    break
        
        general_entertainment = [
            "movie", "film", "trailer", "teaser", "scenes", "clips",
            "vlog", "day in", "haul", "unboxing", "reaction",
            "celebrity", "interview", "talk show", "reality", "drama"
        ]
        if category == "ENTERTAINMENT":
            for kw in general_entertainment:
                if kw in text:
                    entertainment_score = 0.7
                    depth_score = 0.3
                    break
        
        # ============= PRIORITY 4: EDUCATIONAL/STUDY CONTENT =============
        # Only classify as EDUCATION if it's clearly educational
        if category == "ENTERTAINMENT":
            education_keywords = [
                "tutorial", "course", "lecture", "lesson", "learn", "teaching",
                "education", "educational", "academy", "university", "college",
                "programming", "coding", "developer", "software development",
                "science", "physics", "chemistry", "mathematics", "biology",
                "history", "geography", "economics", "psychology",
                "certification", "exam prep", "study with me", "study tips"
            ]
            for kw in education_keywords:
                if kw in text:
                    category = "EDUCATION"
                    entertainment_score = 0.2
                    depth_score = 0.8
                    break
        
        # Tech detection (separate from pure education)
        if category == "ENTERTAINMENT":
            tech_keywords = [
                "technology", "tech review", "python", "javascript", "java",
                "machine learning", "ai", "artificial intelligence", "data science",
                "cloud", "devops", "kubernetes", "docker", "programming tutorial",
                "code", "developer", "engineering", "computer science"
            ]
            for kw in tech_keywords:
                if kw in text:
                    category = "SCIENCE_TECH"
                    entertainment_score = 0.3
                    depth_score = 0.7
                    break
        
        # How-to/Style detection
        if category == "ENTERTAINMENT":
            howto_keywords = [
                "how to", "diy", "tips", "tricks", "guide", "step by step",
                "recipe", "cooking", "baking", "makeup", "fashion", "style",
                "workout", "fitness", "yoga", "meditation", "self improvement"
            ]
            for kw in howto_keywords:
                if kw in text:
                    category = "HOWTO_STYLE"
                    entertainment_score = 0.4
                    depth_score = 0.6
                    break
        
        # ============= DURATION-BASED ADJUSTMENTS =============
        if duration < 60:  # Shorts are usually entertainment
            if category not in ["MUSIC"]:
                entertainment_score = max(entertainment_score, 0.7)
                depth_score = min(depth_score, 0.3)
        elif duration > 1200:  # 20+ minutes
            depth_score = min(depth_score + 0.2, 1.0)
        
        # ============= CLICKBAIT DETECTION =============
        clickbait_patterns = [
            "you won't believe", "gone wrong", "shocking", "exposed",
            "prank", "😱", "🔥", "secret", "revealed", "must see",
            "insane", "crazy", "epic fail", "best ever", "unbelievable"
        ]
        for pattern in clickbait_patterns:
            if pattern in text:
                clickbait_score = 0.7
                break
        
        # ALL CAPS detection
        caps_ratio = sum(1 for c in original_title if c.isupper()) / max(len(original_title), 1)
        if caps_ratio > 0.5:
            clickbait_score = max(clickbait_score, 0.5)
        
        # Excessive punctuation
        if "!!!" in original_title or "???" in original_title or "🔴" in original_title:
            clickbait_score = max(clickbait_score, 0.4)
        
        return VideoClassification(
            category=category,
            confidence_score=0.6,  # Moderate confidence for heuristics
            entertainment_score=entertainment_score,
            depth_score=depth_score,
            clickbait_score=clickbait_score,
        )
    
    async def _cache_result(
        self,
        video: Dict[str, Any],
        classification: VideoClassification,
        db: AsyncSession
    ):
        """Cache classification result in database."""
        video_id = video.get("id")
        
        # Check if entry exists
        result = await db.execute(
            select(ContentCache).where(ContentCache.video_id == video_id)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            # Update existing
            existing.category = classification.category
            existing.confidence_score = classification.confidence_score
            existing.entertainment_score = classification.entertainment_score
            existing.depth_score = classification.depth_score
            existing.clickbait_score = classification.clickbait_score
            existing.analyzed_at = datetime.utcnow()
            existing.expires_at = datetime.utcnow() + timedelta(hours=24)
        else:
            # Create new
            cache = ContentCache(
                video_id=video_id,
                title=video.get("title", ""),
                description=video.get("description", ""),
                channel_id=video.get("channel_id"),
                channel_title=video.get("channel_title"),
                tags=video.get("tags", []),
                thumbnail_url=video.get("thumbnail_url"),
                duration_seconds=video.get("duration_seconds", 0),
                is_short=video.get("is_short", False),
                language=video.get("language"),
                view_count=video.get("view_count", 0),
                like_count=video.get("like_count", 0),
                published_at=video.get("published_at"),
                category=classification.category,
                confidence_score=classification.confidence_score,
                entertainment_score=classification.entertainment_score,
                depth_score=classification.depth_score,
                clickbait_score=classification.clickbait_score,
            )
            db.add(cache)
        
        await db.commit()
