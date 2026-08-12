from typing import Tuple

class FinancialClearanceService:
    """Check financial clearance for students"""

    def __init__(self):
        pass

    async def check_clearance(
        self,
        student_id: str,
        fee_balance: float,
        pending_payments: int
    ) -> Tuple[bool, str]:
        if fee_balance > 0:
            return False, f"Outstanding balance: GHS {fee_balance:.2f}"

        if pending_payments > 0:
            return False, f"{pending_payments} pending payment(s)"

        return True, "Financially cleared"

    async def calculate_fee_balance(
        self,
        total_fees: float,
        payments_received: float,
        scholarships: float
    ) -> float:
        balance = total_fees - payments_received - scholarships
        return max(0, balance)
