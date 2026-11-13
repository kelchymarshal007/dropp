class BaseGateway:
    name: str = "base"

    def create_checkout(self, dropp_id: str, amount_minor: int, currency: str, email: str) -> str:
        """Returns a checkout URL or a mock token"""
        raise NotImplementedError

    def verify_webhook(self, payload: bytes, signature: str) -> dict:
        """Verifies the payment webhook"""
        raise NotImplementedError
