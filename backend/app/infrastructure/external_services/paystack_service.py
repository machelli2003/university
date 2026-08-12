import httpx
from typing import Optional, Dict
from app.config import get_settings

settings = get_settings()

class PaystackService:
    """Paystack payment gateway integration (Test Mode)"""

    BASE_URL = "https://api.paystack.co"

    def __init__(self):
        self.secret_key = settings.PAYSTACK_SECRET_KEY
        self.public_key = settings.PAYSTACK_PUBLIC_KEY
        self.headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json",
        }

    async def initialize_transaction(
        self,
        email: str,
        amount: float,
        reference: str,
        callback_url: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> Dict:
        payload = {
            "email": email,
            "amount": int(amount * 100),
            "reference": reference,
            "currency": "GHS",
        }

        if callback_url:
            payload["callback_url"] = callback_url

        if metadata:
            payload["metadata"] = metadata

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.BASE_URL}/transaction/initialize",
                    json=payload,
                    headers=self.headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                return {
                    "status": False,
                    "message": f"Paystack error: {e.response.text}",
                }
            except Exception as e:
                return {
                    "status": False,
                    "message": f"Connection error: {str(e)}",
                }

    async def verify_transaction(self, reference: str) -> Dict:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.BASE_URL}/transaction/verify/{reference}",
                    headers=self.headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                data = response.json()

                if data.get("status") and data.get("data", {}).get("status") == "success":
                    return {
                        "verified": True,
                        "amount": data["data"]["amount"] / 100,
                        "reference": data["data"]["reference"],
                        "paid_at": data["data"].get("paid_at"),
                        "channel": data["data"].get("channel"),
                        "customer_email": data["data"]["customer"]["email"],
                    }
                else:
                    return {
                        "verified": False,
                        "message": data.get("message", "Transaction not successful"),
                    }
            except httpx.HTTPStatusError as e:
                return {"verified": False, "message": f"Verification error: {e.response.text}"}
            except Exception as e:
                return {"verified": False, "message": f"Connection error: {str(e)}"}

    async def initialize_mobile_money(
        self,
        email: str,
        amount: float,
        phone: str,
        provider: str,
        reference: str,
    ) -> Dict:
        payload = {
            "email": email,
            "amount": int(amount * 100),
            "currency": "GHS",
            "mobile_money": {
                "phone": phone,
                "provider": provider,
            },
            "reference": reference,
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.BASE_URL}/charge",
                    json=payload,
                    headers=self.headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                return {"status": False, "message": str(e)}

    def verify_webhook_signature(self, payload_body: bytes, signature: str) -> bool:
        import hmac
        import hashlib

        computed_signature = hmac.new(
            self.secret_key.encode("utf-8"),
            payload_body,
            hashlib.sha512
        ).hexdigest()

        return hmac.compare_digest(computed_signature, signature)
