import hmac
import hashlib
from app.infrastructure.external_services.paystack_service import PaystackService


def test_verify_webhook_signature():
    svc = PaystackService()
    payload = b'{"data": {"foo": "bar"}}'
    # compute signature using service secret
    secret = svc.secret_key or "test_secret"
    sig = hmac.new(secret.encode("utf-8"), payload, hashlib.sha512).hexdigest()
    assert svc.verify_webhook_signature(payload, sig)
