import asyncio
import sys
sys.path.append('/app')
from app.core.database import AsyncSessionLocal
from app.models.post import Post
from sqlalchemy.future import select

async def main():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Post))
        posts = result.scalars().all()
        for p in posts:
            if p.media_urls:
                # If URL is relative, make it absolute
                fixed = []
                for url in p.media_urls:
                    if url.startswith('/media/'):
                        fixed.append(f"http://localhost:8001{url}")
                    else:
                        fixed.append(url)
                p.media_urls = fixed
        await db.commit()
        print(f"Fixed {len(posts)} posts")

if __name__ == "__main__":
    asyncio.run(main())
