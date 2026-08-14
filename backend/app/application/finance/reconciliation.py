from app.infrastructure.database.repositories.payment_repository import PaymentRepository
from app.infrastructure.external_services.paystack_service import PaystackService
from app.application.finance.process_payment import ProcessPaymentUseCase
import asyncio


async def reconcile_pending_payments(tenant_id: str = "default") -> dict:
    payment_repo = PaymentRepository()
    paystack = PaystackService()
    use_case = ProcessPaymentUseCase(payment_repo)

    pending = await payment_repo.get_pending_payments(tenant_id)
    results = {
        "checked": len(pending),
        "confirmed": 0,
        "failed": 0,
    }

    for p in pending:
        try:
            # attempt verification by paystack reference if present, else by payment_reference
            ref = getattr(p, "paystack_reference", None) or getattr(p, "payment_reference", None)
            if not ref:
                results["failed"] += 1
                continue

            verification = await paystack.verify_transaction(ref)
            if verification.get("verified"):
                await use_case.confirm_payment(str(p.id), verification.get("reference") or ref)
                results["confirmed"] += 1
            else:
                results["failed"] += 1
        except Exception:
            results["failed"] += 1

    return results
