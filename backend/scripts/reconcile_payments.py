"""Run payment reconciliation as a one-off script.

Usage:
    python scripts/reconcile_payments.py [tenant_id]

"""
import asyncio
import sys
from app.application.finance.reconciliation import reconcile_pending_payments


async def main():
    tenant = sys.argv[1] if len(sys.argv) > 1 else "default"
    result = await reconcile_pending_payments(tenant)
    print(f"Reconciliation result for tenant={tenant}: {result}")


if __name__ == "__main__":
    asyncio.run(main())
