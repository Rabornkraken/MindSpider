import asyncio
from typing import Dict, List, Optional

from playwright.async_api import BrowserContext, BrowserType

import config
from base.base_crawler import AbstractCrawler
from store import youtube as youtube_store
from tools import utils
from var import crawler_type_var

from .client import YouTubeClient

class YouTubeCrawler(AbstractCrawler):
    def __init__(self):
        self.yt_client = YouTubeClient()

    async def start(self):
        # We don't need a browser for YouTube text crawling
        # But we must respect the interface
        
        crawler_type_var.set(config.CRAWLER_TYPE)
        if config.CRAWLER_TYPE == "search":
            await self.search()
        
        utils.logger.info("[YouTubeCrawler] Crawler finished ...")
        # Print summary for PlatformCrawler
        # (I need to track stats, but for V1 let's just run)

    async def search(self):
        utils.logger.info("[YouTubeCrawler.search] Begin search")
        total_videos = 0
        
        for keyword in config.KEYWORDS.split(","):
            utils.logger.info(f"[YouTubeCrawler] Searching: {keyword}")
            
            # 1. Search Videos
            videos = await self.yt_client.search_videos(keyword, limit=config.CRAWLER_MAX_NOTES_COUNT)
            
            if not videos:
                utils.logger.info(f"[YouTubeCrawler] No videos found for {keyword}")
                continue
                
            for video in videos:
                video_id = video.get("id")
                title = video.get("title")
                
                utils.logger.info(f"[YouTubeCrawler] Processing: {video_id} - {title}")
                
                # 2. Get Transcript
                transcript = await self.yt_client.get_transcript(video_id)
                
                # 3. Prepare Data
                video_item = {
                    "video_id": video_id,
                    "title": title,
                    "desc": video.get("descriptionSnippet", [{}])[0].get("text", "") if video.get("descriptionSnippet") else "",
                    "channel_id": video.get("channel", {}).get("id"),
                    "channel_name": video.get("channel", {}).get("name"),
                    "view_count": video.get("viewCount", {}).get("short", "0"),
                    "publish_time": video.get("publishedTime"),
                    "duration": video.get("duration"),
                    "url": video.get("link"),
                    "transcription": transcript,
                    "create_time": utils.get_current_timestamp(),
                    "last_modify_ts": utils.get_current_timestamp()
                }
                
                # 4. Store
                await youtube_store.update_youtube_video(video_item)
                total_videos += 1
                
        print(f"[Summary] Notes: {total_videos}, Comments: 0")

    async def launch_browser(self, chromium: BrowserType, playwright_proxy: Optional[Dict], user_agent: Optional[str], headless: bool = True) -> BrowserContext:
        return None # Not used
