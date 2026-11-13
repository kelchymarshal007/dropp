import asyncio
import httpx

API_URL = "http://localhost:8000"

async def main():
    async with httpx.AsyncClient() as client:
        # --- 1. Setup Users ---
        buyer_res = await client.post(f"{API_URL}/v1/auth/login/email", json={"email": "buyer@example.com", "password": "buyerpass"})
        if buyer_res.status_code != 200:
            buyer_res = await client.post(f"{API_URL}/v1/auth/signup/email", json={"email": "buyer@example.com", "password": "buyerpass", "is_seller": False})
        buyer_token = buyer_res.json()["access_token"]
        
        seller_res = await client.post(f"{API_URL}/v1/auth/login/email", json={"email": "seller2@example.com", "password": "sellerpass"})
        if seller_res.status_code != 200:
            seller_res = await client.post(f"{API_URL}/v1/auth/signup/email", json={"email": "seller2@example.com", "password": "sellerpass", "is_seller": True})
        seller_token = seller_res.json()["access_token"]

        buyer_h = {"Authorization": f"Bearer {buyer_token}"}
        seller_h = {"Authorization": f"Bearer {seller_token}"}

        # --- 2. Create Dropp ---
        dropp_res = await client.post(f"{API_URL}/v1/dropps/", headers=buyer_h, json={
            "source_url": "https://tiktok.com/test",
            "source_platform": "tiktok",
            "title": "Payment Test Item",
            "currency": "USD",
            "offer_minor": 150000
        })
        code = dropp_res.json()["code"]
        dropp_id = dropp_res.json()["id"]
        print(f"Created Dropp: {code}")

        # --- 3. Seller Accepts ---
        await client.post(f"{API_URL}/v1/dropps/{code}/seller-respond", headers=seller_h, json={
            "availability_type": "single", "action": "accept"
        })

        # --- 4. Both Sign ---
        await client.post(f"{API_URL}/v1/dropps/{code}/sign", headers=buyer_h, json={
            "final_minor": 140000, "dispatch_mode": "interstate"
        })
        sign_res = await client.post(f"{API_URL}/v1/dropps/{code}/sign", headers=seller_h, json={
            "final_minor": 140000, "dispatch_mode": "interstate"
        })
        
        checkout_token = sign_res.json()["checkout_token"]
        print(f"\n--- Deal Locked! ---")
        print(f"Checkout Token: {checkout_token}")

        # --- 5. Fetch Checkout Details ---
        print(f"\n--- Buyer Opens Checkout Portal ---")
        checkout_res = await client.get(f"{API_URL}/v1/payments/checkout/{checkout_token}")
        print(f"Checkout Details: {checkout_res.json()}")

        # --- 6. Simulate Payment Webhook ---
        print(f"\n--- BIKEM Webhook Fires ---")
        webhook_res = await client.post(f"{API_URL}/v1/payments/confirm-webhook", json={
            "dropp_id": dropp_id
        })
        print(f"Webhook Result: {webhook_res.json()}")

asyncio.run(main())
