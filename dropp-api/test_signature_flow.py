import asyncio
import httpx

API_URL = "http://localhost:8000"

async def main():
    async with httpx.AsyncClient() as client:
        # --- Create/Lookup Buyer and Seller ---
        print("--- 1. Creating Users ---")
        
        # Buyer
        buyer_res = await client.post(f"{API_URL}/v1/auth/signup/email", json={
            "email": "buyer@example.com", "password": "buyerpass", "is_seller": False
        })
        if buyer_res.status_code != 200:
            buyer_res = await client.post(f"{API_URL}/v1/auth/login/email", json={
                "email": "buyer@example.com", "password": "buyerpass"
            })
        buyer_token = buyer_res.json()["access_token"]
        print(f"Buyer logged in.")

        # Seller
        seller_res = await client.post(f"{API_URL}/v1/auth/signup/email", json={
            "email": "seller2@example.com", "password": "sellerpass", "is_seller": True
        })
        if seller_res.status_code != 200:
            seller_res = await client.post(f"{API_URL}/v1/auth/login/email", json={
                "email": "seller2@example.com", "password": "sellerpass"
            })
        seller_token = seller_res.json()["access_token"]
        print(f"Seller logged in.")

        buyer_headers = {"Authorization": f"Bearer {buyer_token}"}
        seller_headers = {"Authorization": f"Bearer {seller_token}"}

        # --- Buyer Creates Dropp ---
        print("\n--- 2. Buyer Creates Dropp ---")
        dropp_res = await client.post(f"{API_URL}/v1/dropps/", headers=buyer_headers, json={
            "source_url": "https://tiktok.com/test",
            "source_platform": "tiktok",
            "title": "Signature Test Item",
            "currency": "USD",
            "offer_minor": 100000
        })
        dropp = dropp_res.json()
        code = dropp["code"]
        print(f"Created Dropp: {code}")

        # --- Seller Responds ---
        print("\n--- 3. Seller Accepts Item ---")
        await client.post(f"{API_URL}/v1/dropps/{code}/seller-respond", headers=seller_headers, json={
            "availability_type": "single", "action": "accept"
        })
        print("State: negotiating")

        # --- Buyer Signs ---
        print("\n--- 4. Buyer Signs ---")
        res1 = await client.post(f"{API_URL}/v1/dropps/{code}/sign", headers=buyer_headers, json={
            "final_minor": 90000, "dispatch_mode": "interstate"
        })
        data1 = res1.json()
        print(f"Buyer Signature Set: {data1.get('buyer_signature') is not None}")
        print(f"Seller Signature Set: {data1.get('seller_signature') is not None}")
        print(f"Status: {data1.get('status')}")

        # --- Seller Signs ---
        print("\n--- 5. Seller Signs ---")
        res2 = await client.post(f"{API_URL}/v1/dropps/{code}/sign", headers=seller_headers, json={
            "final_minor": 90000, "dispatch_mode": "interstate"
        })
        data2 = res2.json()
        print(f"Buyer Signature Set: {data2.get('buyer_signature') is not None}")
        print(f"Seller Signature Set: {data2.get('seller_signature') is not None}")
        print(f"Status: {data2.get('status')}")
        print(f"Checkout Token: {data2.get('checkout_token')}")

asyncio.run(main())
