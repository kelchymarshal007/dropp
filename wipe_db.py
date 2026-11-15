import asyncio
import sys
sys.path.append('/app')
from app.core.database import AsyncSessionLocal
from app.models.post import Post
from app.models.post_social import PostLike, PostComment
from sqlalchemy import delete

async def main():
    async with AsyncSessionLocal() as db:
        await db.execute(delete(PostLike))
        await db.execute(delete(PostComment))
        await db.execute(delete(Post))
        await db.commit()
        print("Database wiped. All posts, likes, and comments deleted.")

if __name__ == "__main__":
    asyncio.run(main())
