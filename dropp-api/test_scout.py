import asyncio
import httpx
import sys

sys.path.append('/app')
from app.core.database import AsyncSessionLocal
from app.models.user import User
from sqlalchemy.future import select
from sqlalchemy import update

API_URL = "http://localhost:8000"

async def main():
    async with httpx.AsyncClient() as client:
        # 1. Sign up buyer
        print("--- 1. Signing up buyer (Free tier) ---")
        res = await client.post(f"{API_URL}/v1/auth/signup/email", json={
            "email": "scout_test2@example.com", "password": "testpass123", "is_seller": False
        })
        if res.status_code != 200:
            res = await client.post(f"{API_URL}/v1/auth/login/email", json={
                "email": "scout_test2@example.com", "password": "testpass123"
            })
        token = res.json()["access_token"]
        buyer_id = res.json()["user_id"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Try to create Wanted Request (should FAIL - Free tier)
        print("\n--- 2. Free user tries Scout (should be 403) ---")
        r = await client.post(f"{API_URL}/v1/scout/requests", headers=headers, json={
            "item_description": "Nike Air Jordan 1 Size 10",
            "target_price_minor": 30000,
            "currency": "USD",
            "location": "Lagos"
        })
        print(f"Status: {r.status_code} - {r.json()}")

        # 3. Upgrade to Pro
        print("\n--- 3. Upgrading to Pro Buyer ---")
        async with AsyncSessionLocal() as db:
            await db.execute(update(User).where(User.id == buyer_id).values(tier="pro_buyer"))
            await db.commit()
        print("Upgraded successfully")

        # 4. Create Wanted Request (should SUCCEED)
        print("\n--- 4. Pro user creates Wanted Request ---")
        r = await client.post(f"{API_URL}/v1/scout/requests", headers=headers, json={
            "item_description": "Nike Air Jordan 1 Size 10",
            "target_price_minor": 30000,
            "currency": "USD",
            "location": "Lagos"
        })
        print(f"Status: {r.status_code}")
        request_data = r.json()
        request_id = request_data["id"]
        print(f"Request ID: {request_id}")

        # 5. Find external matches
        print("\n--- 5. Scout engine searches external platforms ---")
        r = await client.get(f"{API_URL}/v1/scout/requests/{request_id}/matches", headers=headers)
        print(f"Status: {r.status_code}")
        matches = r.json()
        print(f"Top matches: {len(matches)}")
        for m in matches:
            price = m['price_minor']/100 if m['price_minor'] else 'N/A'
            print(f"  Score {m['match_score']} | {m['seller_id']} | {m['caption']} | {price} {m['currency']}")

asyncio.run(main())
