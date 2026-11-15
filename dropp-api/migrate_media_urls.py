import asyncio
import sys
sys.path.append('/app')
from app.core.database import AsyncSessionLocal
from app.models.post import Post
from app.models.post_social import PostComment
from sqlalchemy.future import select

async def main():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Post))
        posts = result.scalars().all()
        for p in posts:
            if p.media_urls:
                p.media_urls = [url.replace('http://localhost:8001', '') for url in p.media_urls]
        c_result = await db.execute(select(PostComment))
        comments = c_result.scalars().all()
        for c in comments:
            if c.media_urls:
                c.media_urls = [url.replace('http://localhost:8001', '') for url in c.media_urls]
        await db.commit()
        print(f"Migrated {len(posts)} posts and {len(comments)} comments to relative URLs")

if __name__ == "__main__":
    asyncio.run(main())
