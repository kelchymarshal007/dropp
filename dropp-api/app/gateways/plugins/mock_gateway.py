import random
import string
from app.gateways.base_gateway import BaseGateway

class MockGateway(BaseGateway):
    name = "mock_bikem"

    def create_checkout(self, dropp_id: str, amount_minor: int, currency: str, email: str) -> str:
        # In production, this would call the BIKEM API and return a real URL.
        # For now, we return a mock checkout token to simulate the redirect.
        mock_token = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
        print(f"[{self.name}] Created checkout for {dropp_id} at {amount_minor / 100} {currency}. Token: {mock_token}")
        return mock_token

    def verify_webhook(self, payload: bytes, signature: str) -> dict:
        # In production, verify HMAC signature. For mock, we trust it.
        import json
        return json.loads(payload)
