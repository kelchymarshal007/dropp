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
        # 1. Create a normal user and try to access admin (should 403)
        print("--- 1. Normal user tries admin (should 403) ---")
        res = await client.post(f"{API_URL}/v1/auth/signup/email", json={
            "email": "normal_user@example.com", "password": "pass12345", "is_seller": False
        })
        if res.status_code != 200:
            res = await client.post(f"{API_URL}/v1/auth/login/email", json={
                "email": "normal_user@example.com", "password": "pass12345"
            })
        user_token = res.json()["access_token"]
        user_id = res.json()["user_id"]
        user_h = {"Authorization": f"Bearer {user_token}"}

        r = await client.get(f"{API_URL}/v1/admin/metrics", headers=user_h)
        print(f"Status: {r.status_code} - {r.json()}")

        # 2. Promote to admin
        print("\n--- 2. Promoting user to admin ---")
        async with AsyncSessionLocal() as db:
            await db.execute(update(User).where(User.id == user_id).values(role="admin"))
            await db.commit()
        print("Promoted to admin")

        # Re-login
        res = await client.post(f"{API_URL}/v1/auth/login/email", json={
            "email": "normal_user@example.com", "password": "pass12345"
        })
        admin_token = res.json()["access_token"]
        admin_h = {"Authorization": f"Bearer {admin_token}"}

        # 3. Access admin metrics
        print("\n--- 3. Admin fetches metrics ---")
        r = await client.get(f"{API_URL}/v1/admin/metrics", headers=admin_h)
        print(f"Status: {r.status_code}")
        print(f"Metrics: {r.json()}")

        # 4. List disputes
        print("\n--- 4. Admin lists disputes ---")
        r = await client.get(f"{API_URL}/v1/admin/disputes", headers=admin_h)
        print(f"Status: {r.status_code}")
        print(f"Disputes: {r.json()}")

        # 5. List users
        print("\n--- 5. Admin lists users ---")
        r = await client.get(f"{API_URL}/v1/admin/users?limit=5", headers=admin_h)
        print(f"Status: {r.status_code}")
        print(f"Users returned: {len(r.json())}")

        # 6. Suspend a user
        print("\n--- 6. Admin suspends a victim ---")
        v = await client.post(f"{API_URL}/v1/auth/signup/email", json={
            "email": "victim@example.com", "password": "pass12345", "is_seller": False
        })
        if v.status_code != 200:
            v = await client.post(f"{API_URL}/v1/auth/login/email", json={
                "email": "victim@example.com", "password": "pass12345"
            })
        victim_id = v.json()["user_id"]

        r = await client.post(
            f"{API_URL}/v1/admin/users/{victim_id}/suspend",
            headers=admin_h,
            json={"reason": "Test suspension"}
        )
        print(f"Status: {r.status_code} - {r.json()}")

        # 7. Reactivate
        print("\n--- 7. Admin reactivates ---")
        r = await client.post(f"{API_URL}/v1/admin/users/{victim_id}/reactivate", headers=admin_h)
        print(f"Status: {r.status_code} - {r.json()}")

asyncio.run(main())
