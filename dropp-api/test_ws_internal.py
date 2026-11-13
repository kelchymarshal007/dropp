import asyncio
import websockets
import json

async def test_chat():
    # Using the fresh token
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMWYzNjViYS1mNDVhLTQyMGUtODY0ZS00YjNhMmM4MGFhNjAiLCJleHAiOjE3OTUxOTk4MzV9.s1DtMoScHlMEzo5LfEECsTMhoxeq7slfAmcx8b7F78A"
    dropp_id = "test_dropp_123"
    uri = f"ws://localhost:8000/ws/chat/{dropp_id}?token={token}"
    
    async with websockets.connect(uri) as websocket:
        welcome = await websocket.recv()
        print(f"< Received Welcome: {welcome}")
        
        await websocket.send(json.dumps({"body": "Is the PS5 still available?"}))
        
        response = await websocket.recv()
        print(f"< Received Broadcast: {response}")

asyncio.run(test_chat())
