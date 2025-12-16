import asyncio
from typing import Dict, List, Optional
from urllib.parse import urlencode

from youtube_transcript_api import YouTubeTranscriptApi
from youtubesearchpython import VideosSearch

from base.base_crawler import AbstractApiClient
from tools import utils

class YouTubeClient(AbstractApiClient):
    def __init__(self):
        self.headers = {} # Not strictly used by these libraries but kept for interface

    async def request(self, method, url, **kwargs):
        pass # Not used directly

    async def update_cookies(self, browser_context):
        pass # Not needed for public data

    async def search_videos(self, keyword: str, limit: int = 10) -> List[Dict]:
        """
        Search for videos on YouTube
        """
        try:
            # Run sync library in executor
            loop = asyncio.get_running_loop()
            
            def _search():
                videos_search = VideosSearch(keyword, limit=limit)
                return videos_search.result()

            result = await loop.run_in_executor(None, _search)
            return result.get("result", [])
        except Exception as e:
            utils.logger.error(f"[YouTubeClient] Search failed: {e}")
            return []

    async def get_transcript(self, video_id: str) -> str:
        """
        Get transcript for a video
        """
        try:
            # Run sync library in executor
            loop = asyncio.get_running_loop()
            
            def _get_transcript():
                # Try to get English or Chinese, or auto-generated
                try:
                    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                    # Try to find manually created transcripts first
                    try:
                        transcript = transcript_list.find_transcript(['en', 'zh-Hans', 'zh-Hant'])
                    except:
                        # Fallback to any available (including auto-generated)
                        transcript = transcript_list.find_transcript(['en', 'zh-Hans', 'zh-Hant']) # Wait, this logic is same.
                        # Ideally iterate.
                        # Let's just use get_transcript which picks the first available or auto
                        pass
                    
                    # Actually get_transcript is simpler for basic usage
                    return YouTubeTranscriptApi.get_transcript(video_id, languages=['zh-Hans', 'zh-Hant', 'en'])
                except Exception as e:
                    # Retry with just auto-generated if languages fail
                    return YouTubeTranscriptApi.get_transcript(video_id)

            transcript_data = await loop.run_in_executor(None, _get_transcript)
            
            # Combine text
            full_text = " ".join([item['text'] for item in transcript_data])
            return full_text
            
        except Exception as e:
            utils.logger.warning(f"[YouTubeClient] Transcript not available for {video_id}: {e}")
            return ""
