import asyncio
import websockets
import json
import httpx

API_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000"

async def main():
    async with httpx.AsyncClient() as client:
        print("--- 1. Logging in as Buyer ---")
        buyer_login = await client.post(f"{API_URL}/v1/auth/login/email", json={"email": "seller@example.com", "password": "securepass"})
        if buyer_login.status_code != 200:
            print(f"LOGIN FAILED: {buyer_login.status_code} - {buyer_login.text}")
            return
            
        buyer_token = buyer_login.json()["access_token"]
        
        print("--- 2. Creating a Dropp ---")
        dropp_res = await client.post(
            f"{API_URL}/v1/dropps/",
            headers={"Authorization": f"Bearer {buyer_token}"},
            json={
                "source_url": "https://tiktok.com/test",
                "source_platform": "tiktok",
                "title": "Test iPhone",
                "currency": "USD",
                "offer_minor": 50000
            }
        )
        
        # Print the raw response if it's not 200
        if dropp_res.status_code != 200:
            print(f"CREATE DROPP FAILED: {dropp_res.status_code}")
            print(f"Response: {dropp_res.text}")
            return
            
        dropp = dropp_res.json()
        dropp_id = dropp["id"]
        dropp_code = dropp["code"]
        print(f"Created Dropp: {dropp_code} (ID: {dropp_id})")

        print("\n--- 3. Seller Connecting to WebSocket ---")
        uri = f"{WS_URL}/ws/chat/{dropp_id}?token={buyer_token}"
        
        async with websockets.connect(uri) as websocket:
            response = await websocket.recv()
            print(f"< Received from AI: {response}")
            
            print("\n--- 4. Seller Accepts Item via REST API ---")
            accept_res = await client.post(
                f"{API_URL}/v1/dropps/{dropp_code}/seller-respond",
                headers={"Authorization": f"Bearer {buyer_token}"},
                json={"availability_type": "single", "action": "accept"}
            )
            
            if accept_res.status_code != 200:
                print(f"SELLER RESPOND FAILED: {accept_res.status_code}")
                print(f"Response: {accept_res.text}")
                return
                
            print(f"REST Response: {accept_res.status_code}")

            print("\n--- 5. Waiting for AI Broadcast to Chat ---")
            response = await websocket.recv()
            print(f"< Received from AI: {response}")

asyncio.run(main())
