import asyncio
import sys
sys.path.append('/app')
from app.core.database import AsyncSessionLocal
from app.models.post import Post
from app.models.post_social import PostLike
from sqlalchemy import update, delete

async def main():
    async with AsyncSessionLocal() as db:
        # 1. Delete all existing likes
        await db.execute(delete(PostLike))
        
        # 2. Reset all like and comment counts to 0
        await db.execute(update(Post).values(like_count=0, comment_count=0))
        
        await db.commit()
        print("Successfully reset all likes and comments to 0 in the database.")

if __name__ == "__main__":
    asyncio.run(main())
