import asyncio
import sys
sys.path.append('/app')
from app.core.database import AsyncSessionLocal
from app.models.post import Post
from app.models.user import User
from sqlalchemy.future import select

async def main():
    async with AsyncSessionLocal() as db:
        # Get any existing user to act as the seller
        result = await db.execute(select(User).limit(1))
        user = result.scalar_one_or_none()
        if not user:
            print("No users found. Please sign up in the app first, then run this script.")
            return

        print(f"Seeding posts for seller: {user.email}")

        videos = [
            "https://www.w3schools.com/html/mov_bbb.mp4",
            "https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4",
            "https://www.w3schools.com/html/mov_bbb.mp4",
            "https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4",
            "https://www.w3schools.com/html/mov_bbb.mp4",
            "https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4",
            "https://www.w3schools.com/html/mov_bbb.mp4",
            "https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4",
            "https://www.w3schools.com/html/mov_bbb.mp4",
            "https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4"
        ]
        
        for i, url in enumerate(videos):
            post = Post(
                seller_id=str(user.id),
                media_url=url,
                media_type="video",
                caption=f"Test Product {i+1}. Check this out!",
                price_minor=10000 + (i * 5000),
                currency="USD",
                status="active",
                like_count=100 + i * 15,
                comment_count=20 + i * 3,
                dropp_count=5 + i,
                share_count=10 + i
            )
            db.add(post)
        await db.commit()
        print("Successfully seeded 10 posts into the feed!")

if __name__ == "__main__":
    asyncio.run(main())
