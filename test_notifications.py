import asyncio
import httpx
import sys

sys.path.append('/app')
from app.core.database import AsyncSessionLocal
from app.services.notification_service import send_notification

API_URL = "http://localhost:8000"

async def main():
    async with httpx.AsyncClient() as client:
        # 1. Try signup
        print("--- Signing Up ---")
        res = await client.post(f"{API_URL}/v1/auth/signup/email", json={
            "email": "notif_user@example.com", "password": "pass123", "is_seller": False
        })
        print(f"Signup Response: {res.status_code} - {res.text}")

        if res.status_code != 200:
            print("--- Trying Login ---")
            res = await client.post(f"{API_URL}/v1/auth/login/email", json={
                "email": "notif_user@example.com", "password": "pass123"
            })
            print(f"Login Response: {res.status_code} - {res.text}")

        if res.status_code != 200:
            print("FATAL: Cannot authenticate user.")
            return

        token = res.json()["access_token"]
        user_id = res.json()["user_id"]
        headers = {"Authorization": f"Bearer {token}"}
        print(f"Authenticated as user: {user_id}")

        # 2. Trigger notification
        print("\n--- Triggering Notification ---")
        async with AsyncSessionLocal() as db:
            await send_notification(
                db=db,
                user_id=user_id,
                notif_type="escrow_update",
                title="Item Shipped!",
                body="Your PS5 has been shipped via DHL.",
                channels=["in_app", "email", "sms"]
            )
        print("Notification dispatched to DB + Queues")

        # 3. Fetch via API
        print("\n--- Fetching Notifications ---")
        r = await client.get(f"{API_URL}/v1/notifications/", headers=headers)
        print(f"Status: {r.status_code}")
        print(f"Notifications: {r.json()}")

asyncio.run(main())
