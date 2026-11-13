import asyncio
import httpx
import sys
import uuid

sys.path.append('/app')
from app.models.post import Post
from app.core.database import AsyncSessionLocal

API_URL = "http://localhost:8000"

async def main():
    async with httpx.AsyncClient() as client:
        # 1. Login or Signup
        res = await client.post(f"{API_URL}/v1/auth/login/email", json={"email": "seller2@example.com", "password": "sellerpass"})
        if res.status_code != 200:
            res = await client.post(f"{API_URL}/v1/auth/signup/email", json={"email": "seller2@example.com", "password": "sellerpass", "is_seller": True})
        
        token = res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        user_id = res.json()["user_id"]

        # 2. Directly insert a mock active post into the DB (bypassing video upload for now)
        async with AsyncSessionLocal() as db:
            post = Post(
                seller_id=user_id,
                media_url="https://cdn.dropp.app/reels/test/index.m3u8",
                media_type="video",
                caption="This is a test Reel",
                status="active"
            )
            db.add(post)
            await db.commit()
            await db.refresh(post)
            post_id = str(post.id)
            print(f"Mock Post Created: {post_id}")

        # 3. Fetch Feed
        print("\n--- Fetching Feed ---")
        feed_res = await client.get(f"{API_URL}/v1/feed/")
        print(f"Feed: {feed_res.json()}")

        # 4. Like the Post
        print("\n--- Liking Post ---")
        like_res = await client.post(f"{API_URL}/v1/feed/{post_id}/like", headers=headers)
        print(f"Like Result: {like_res.json()}")

        # 5. Comment on the Post
        print("\n--- Commenting on Post ---")
        comment_res = await client.post(f"{API_URL}/v1/feed/{post_id}/comment", headers=headers, json={"body": "Nice item!"})
        print(f"Comment Result: {comment_res.json()}")

        # 6. Verify Feed Counters
        print("\n--- Verifying Updated Feed ---")
        feed_res2 = await client.get(f"{API_URL}/v1/feed/")
        print(f"Updated Feed: {feed_res2.json()}")

asyncio.run(main())
