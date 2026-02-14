"""YouTube API service."""
import httpx
import re
from typing import Optional, Dict, List, Any
from datetime import datetime
from youtube_transcript_api import YouTubeTranscriptApi

from app.config import get_settings

settings = get_settings()


class YouTubeService:
    """Service for interacting with YouTube Data API v3."""
    
    BASE_URL = "https://www.googleapis.com/youtube/v3"
    
    def __init__(self):
        self.api_key = settings.youtube_api_key
    
    async def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict:
        """Make authenticated request to YouTube API."""
        params["key"] = self.api_key
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/{endpoint}",
                params=params,
                timeout=30.0
            )
            
            if response.status_code != 200:
                return {"error": response.json(), "items": []}
            
            return response.json()
    
    def _parse_duration(self, duration: str) -> int:
        """Parse ISO 8601 duration to seconds."""
        # PT1H2M3S -> 3723 seconds
        pattern = re.compile(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?')
        match = pattern.match(duration)
        
        if not match:
            return 0
        
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        
        return hours * 3600 + minutes * 60 + seconds
    
    def _is_short(self, duration_seconds: int, title: str) -> bool:
        """Determine if video is a YouTube Short."""
        # Shorts are typically 60 seconds or less
        if duration_seconds <= 60:
            return True
        # Also check for #shorts in title
        if "#shorts" in title.lower() or "#short" in title.lower():
            return True
        return False
    
    def _format_video(self, item: Dict, details: Optional[Dict] = None) -> Dict:
        """Format video data into standard structure."""
        snippet = item.get("snippet", {})
        statistics = details.get("statistics", {}) if details else {}
        content_details = details.get("contentDetails", {}) if details else {}
        
        duration_seconds = self._parse_duration(
            content_details.get("duration", "PT0S")
        )
        title = snippet.get("title", "")
        
        # Handle id being either a dict (from search) or string (from videos)
        item_id = item.get("id", "")
        if isinstance(item_id, dict):
            video_id = item_id.get("videoId", "")
        else:
            video_id = item_id
        
        # Get best thumbnail
        thumbnails = snippet.get("thumbnails", {})
        thumbnail_url = (
            thumbnails.get("maxres", {}).get("url") or
            thumbnails.get("high", {}).get("url") or
            thumbnails.get("medium", {}).get("url") or
            thumbnails.get("default", {}).get("url")
        )
        
        # Parse published date
        published_at = None
        if snippet.get("publishedAt"):
            try:
                published_at = datetime.fromisoformat(
                    snippet["publishedAt"].replace("Z", "+00:00")
                )
            except:
                pass
        
        return {
            "id": video_id,
            "title": title,
            "description": snippet.get("description", ""),
            "channel_id": snippet.get("channelId"),
            "channel_title": snippet.get("channelTitle"),
            "thumbnail_url": thumbnail_url,
            "duration_seconds": duration_seconds,
            "is_short": self._is_short(duration_seconds, title),
            "language": snippet.get("defaultLanguage") or snippet.get("defaultAudioLanguage"),
            "tags": snippet.get("tags", []),
            "view_count": int(statistics.get("viewCount", 0)),
            "like_count": int(statistics.get("likeCount", 0)),
            "comment_count": int(statistics.get("commentCount", 0)),
            "published_at": published_at,
            "category_id": snippet.get("categoryId"),
        }
    
    async def search_videos(
        self,
        query: str,
        max_results: int = 20,
        page_token: Optional[str] = None
    ) -> Dict:
        """Search for videos."""
        params = {
            "part": "snippet",
            "type": "video",
            "q": query,
            "maxResults": max_results,
            "order": "relevance",
            "safeSearch": "moderate",
        }
        
        if page_token:
            params["pageToken"] = page_token
        
        result = await self._make_request("search", params)
        
        if "error" in result:
            return result
        
        # Get video details for duration and stats
        video_ids = [item["id"]["videoId"] for item in result.get("items", [])]
        details = await self._get_videos_details(video_ids)
        
        videos = []
        for item in result.get("items", []):
            video_id = item["id"]["videoId"]
            video_details = details.get(video_id, {})
            videos.append(self._format_video(item, video_details))
        
        return {
            "items": videos,
            "next_page_token": result.get("nextPageToken"),
            "total_results": result.get("pageInfo", {}).get("totalResults")
        }
    
    async def _get_videos_details(self, video_ids: List[str]) -> Dict[str, Dict]:
        """Get detailed info for multiple videos."""
        if not video_ids:
            return {}
        
        params = {
            "part": "snippet,contentDetails,statistics",
            "id": ",".join(video_ids)
        }
        
        result = await self._make_request("videos", params)
        
        details = {}
        for item in result.get("items", []):
            details[item["id"]] = item
        
        return details
    
    async def get_video_details(self, video_id: str) -> Optional[Dict]:
        """Get detailed info for a single video."""
        params = {
            "part": "snippet,contentDetails,statistics",
            "id": video_id
        }
        
        result = await self._make_request("videos", params)
        
        items = result.get("items", [])
        if not items:
            return None
        
        item = items[0]
        return self._format_video({"id": video_id, "snippet": item.get("snippet", {})}, item)
    
    async def get_recommended_videos(
        self,
        max_results: int = 20,
        page_token: Optional[str] = None
    ) -> Dict:
        """Get recommended/popular videos (uses trending as proxy)."""
        params = {
            "part": "snippet,contentDetails,statistics",
            "chart": "mostPopular",
            "regionCode": "US",
            "maxResults": max_results,
        }
        
        if page_token:
            params["pageToken"] = page_token
        
        result = await self._make_request("videos", params)
        
        videos = []
        for item in result.get("items", []):
            videos.append(self._format_video(
                {"id": item["id"], "snippet": item.get("snippet", {})},
                item
            ))
        
        return {
            "items": videos,
            "next_page_token": result.get("nextPageToken"),
            "total_results": result.get("pageInfo", {}).get("totalResults")
        }
    
    async def get_transcript(self, video_id: str) -> Optional[str]:
        """Get video transcript/captions."""
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            return " ".join([t["text"] for t in transcript_list])
        except Exception:
            # Transcript not available
            return None
    
    async def get_channel_videos(
        self,
        channel_id: str,
        max_results: int = 20,
        page_token: Optional[str] = None
    ) -> Dict:
        """Get videos from a specific channel."""
        params = {
            "part": "snippet",
            "channelId": channel_id,
            "type": "video",
            "order": "date",
            "maxResults": max_results,
        }
        
        if page_token:
            params["pageToken"] = page_token
        
        result = await self._make_request("search", params)
        
        video_ids = [item["id"]["videoId"] for item in result.get("items", [])]
        details = await self._get_videos_details(video_ids)
        
        videos = []
        for item in result.get("items", []):
            video_id = item["id"]["videoId"]
            videos.append(self._format_video(item, details.get(video_id, {})))
        
        return {
            "items": videos,
            "next_page_token": result.get("nextPageToken"),
            "total_results": result.get("pageInfo", {}).get("totalResults")
        }
