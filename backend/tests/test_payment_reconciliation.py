import pytest
import asyncio
from types import SimpleNamespace


@pytest.mark.asyncio
async def test_reconcile_pending_payments(monkeypatch):
    # prepare a fake pending payment
    fake_payment = SimpleNamespace(id="fakeid123", paystack_reference=None, payment_reference="PAY-TEST-123")

    async def fake_get_pending(tenant_id="default"):
        return [fake_payment]

    async def fake_verify_transaction(ref):
        return {"verified": True, "reference": "PS-FAKE-REF"}

    async def fake_confirm_payment(payment_id, reference):
        # simulate confirming payment
        return {"payment_id": payment_id, "status": "success", "receipt_number": "RCP-FAKE"}

    # monkeypatch repository and services
    from app.infrastructure.database.repositories.payment_repository import PaymentRepository
    from app.infrastructure.external_services.paystack_service import PaystackService
    from app.application.finance.process_payment import ProcessPaymentUseCase

    monkeypatch.setattr(PaymentRepository, "get_pending_payments", fake_get_pending)
    monkeypatch.setattr(PaystackService, "verify_transaction", fake_verify_transaction)
    monkeypatch.setattr(ProcessPaymentUseCase, "confirm_payment", fake_confirm_payment)

    from app.application.finance.reconciliation import reconcile_pending_payments

    result = await reconcile_pending_payments("default")
    assert result["checked"] == 1
    assert result["confirmed"] == 1
