import asyncio
from typing import Dict

import config
from base.base_crawler import AbstractStore
from db import db_conn_pool_var
from tools import utils

class YouTubeStore(AbstractStore):
    async def store_content(self, content_item: Dict):
        """
        Store youtube video content
        """
        pool = db_conn_pool_var.get()
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                insert_sql = """
                    INSERT INTO youtube_video(
                        video_id, title, `desc`, channel_id, channel_name, 
                        view_count, publish_time, duration, url, transcription, 
                        create_time, last_modify_ts
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE 
                        view_count=VALUES(view_count), 
                        transcription=VALUES(transcription),
                        last_modify_ts=VALUES(last_modify_ts)
                """
                
                params = (
                    content_item.get("video_id"),
                    content_item.get("title"),
                    content_item.get("desc"),
                    content_item.get("channel_id"),
                    content_item.get("channel_name"),
                    content_item.get("view_count"),
                    content_item.get("publish_time"),
                    content_item.get("duration"),
                    content_item.get("url"),
                    content_item.get("transcription"),
                    content_item.get("create_time"),
                    content_item.get("last_modify_ts")
                )
                
                await cursor.execute(insert_sql, params)
                await conn.commit()
                utils.logger.info(f"[YouTubeStore] Insert video: {content_item.get('video_id')}")

    async def store_comment(self, comment_item: Dict):
        pass # Not implementing comments for now

    async def store_creator(self, creator: Dict):
        pass

async def update_youtube_video(video_item: Dict):
    store = YouTubeStore()
    await store.store_content(video_item)
