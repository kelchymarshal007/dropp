import asyncio
import websockets
import json

async def test_chat():
    # Use the token from your earlier login
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMWYzNjViYS1mNDVhLTQyMGUtODY0ZS00YjNhMmM4MGFhNjAiLCJleHAiOjE3OTUxOTg2OTJ9.CI_kBJzrt8YiS4zDSVEyKTY8F905ENuc6x8_4iIoL-Q"
    dropp_id = "test_dropp_123"
    uri = f"ws://localhost:8001/ws/chat/{dropp_id}?token={token}"
    
    async with websockets.connect(uri) as websocket:
        # 1. Receive the AI welcome message
        welcome = await websocket.recv()
        print(f"< Received Welcome: {welcome}")
        
        # 2. Send a message
        await websocket.send(json.dumps({"body": "Is the PS5 still available?"}))
        
        # 3. Receive the broadcasted message back
        response = await websocket.recv()
        print(f"< Received Broadcast: {response}")

asyncio.run(test_chat())
