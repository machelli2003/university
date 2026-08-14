import pytest
import asyncio
from datetime import datetime

from app.application.finance.process_payment import ProcessPaymentUseCase


class FakeRepo:
    def __init__(self):
        self.created = None
        self.updated = None

    async def create(self, data):
        class P:
            def __init__(self, data):
                self.id = "fakeid"
                for k, v in data.items():
                    setattr(self, k, v)
        self.created = data
        return P(data)

    async def get_by_id(self, doc_id):
        # return object with attributes used by confirm_payment
        class P:
            def __init__(self):
                self.id = doc_id
                self.amount = 100.0
                self.payment_reference = "PAY-XYZ"
                self.student_id = "STU-1"
                self.tenant_id = "default"
        return P()

    async def update(self, doc_id, data):
        class P:
            def __init__(self):
                self.id = doc_id
                self.amount = data.get("amount", 100.0)
                self.payment_reference = data.get("payment_reference", "PAY-XYZ")
                self.payment_date = data.get("payment_date", datetime.utcnow())
                self.receipt_number = data.get("receipt_number")
                self.student_id = "STU-1"
                self.tenant_id = "default"
        self.updated = data
        return P()


@pytest.mark.asyncio
async def test_initiate_and_confirm_payment_flow():
    repo = FakeRepo()
    use_case = ProcessPaymentUseCase(repo)

    result = await use_case.initiate_payment("default", "STU-1", 50.0, "application", "card")
    assert result["status"] == "pending"
    assert "payment_reference" in result

    confirm = await use_case.confirm_payment(result["payment_id"], "PS-REF-123")
    assert confirm["status"] == "success"
    assert "receipt_number" in confirm
