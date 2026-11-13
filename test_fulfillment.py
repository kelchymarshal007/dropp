import asyncio
import httpx

API_URL = "http://localhost:8000"

async def create_funded_dropp(client, buyer_h, seller_h):
    dropp_res = await client.post(f"{API_URL}/v1/dropps/", headers=buyer_h, json={
        "source_url": "https://tiktok.com/test",
        "source_platform": "tiktok",
        "title": "Fulfillment Test Item",
        "currency": "USD",
        "offer_minor": 100000
    })
    dropp = dropp_res.json()
    code = dropp["code"]
    dropp_id = dropp["id"]

    await client.post(f"{API_URL}/v1/dropps/{code}/seller-respond", headers=seller_h, json={
        "availability_type": "single", "action": "accept"
    })
    await client.post(f"{API_URL}/v1/dropps/{code}/sign", headers=buyer_h, json={
        "final_minor": 95000, "dispatch_mode": "interstate"
    })
    await client.post(f"{API_URL}/v1/dropps/{code}/sign", headers=seller_h, json={
        "final_minor": 95000, "dispatch_mode": "interstate"
    })
    await client.post(f"{API_URL}/v1/payments/confirm-webhook", json={"dropp_id": dropp_id})
    
    return code, dropp_id

async def main():
    async with httpx.AsyncClient() as client:
        buyer_res = await client.post(f"{API_URL}/v1/auth/login/email", json={"email": "buyer@example.com", "password": "buyerpass"})
        if buyer_res.status_code != 200:
            buyer_res = await client.post(f"{API_URL}/v1/auth/signup/email", json={"email": "buyer@example.com", "password": "buyerpass", "is_seller": False})
        buyer_token = buyer_res.json()["access_token"]
        
        seller_res = await client.post(f"{API_URL}/v1/auth/login/email", json={"email": "seller2@example.com", "password": "sellerpass"})
        seller_token = seller_res.json()["access_token"]

        bh = {"Authorization": f"Bearer {buyer_token}"}
        sh = {"Authorization": f"Bearer {seller_token}"}

        # ==========================================
        # TEST 1: HAPPY PATH
        # ==========================================
        print("=== TEST 1: HAPPY PATH ===")
        code, _ = await create_funded_dropp(client, bh, sh)
        print(f"Dropp {code} is now FUNDED.")

        print("--- 1. Seller Ships ---")
        r = await client.post(f"{API_URL}/v1/dropps/{code}/ship", headers=sh, json={"carrier": "DHL", "tracking_no": "DHL123456"})
        print(f"Status: {r.json().get('status')}")

        print("--- 2. Item Delivered ---")
        # FIXED: Pass seller header (carrier webhook would call this in production)
        r = await client.post(f"{API_URL}/v1/dropps/{code}/delivered", headers=sh)
        print(f"Status: {r.json().get('status')} | Auto-release at: {r.json().get('auto_release_at')}")

        print("--- 3. Buyer Confirms Received ---")
        r = await client.post(f"{API_URL}/v1/dropps/{code}/confirm-received", headers=bh)
        print(f"Status: {r.json().get('status')}")
        print("HAPPY PATH COMPLETE.\n")

        # ==========================================
        # TEST 2: DISPUTE PATH
        # ==========================================
        print("=== TEST 2: DISPUTE PATH ===")
        code2, _ = await create_funded_dropp(client, bh, sh)
        print(f"Dropp {code2} is now FUNDED.")

        print("--- 1. Seller Ships ---")
        r = await client.post(f"{API_URL}/v1/dropps/{code2}/ship", headers=sh, json={"carrier": "GIG", "tracking_no": "GIG789"})
        print(f"Status: {r.json().get('status')}")

        print("--- 2. Item Delivered ---")
        r = await client.post(f"{API_URL}/v1/dropps/{code2}/delivered", headers=sh)
        print(f"Status: {r.json().get('status')}")

        print("--- 3. Buyer Opens Dispute ---")
        r = await client.post(f"{API_URL}/v1/dropps/{code2}/dispute", headers=bh, json={"reason": "Item is damaged"})
        print(f"Status: {r.json().get('status')}")

        print("--- 4. Admin Resolves (Releases to Seller) ---")
        r = await client.post(f"{API_URL}/v1/dropps/admin/{code2}/resolve", headers=bh, json={"decision": "release_seller"})
        print(f"Status: {r.json().get('status')}")
        print("DISPUTE PATH COMPLETE.")

asyncio.run(main())
