"""Run payment reconciliation as a one-off script.

Usage:
    python scripts/reconcile_payments.py [tenant_id]

"""
import os
import sys

# Ensure backend directory is on Python path regardless of execution location
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import asyncio
from app.application.finance.reconciliation import reconcile_pending_payments


async def main():
    tenant = sys.argv[1] if len(sys.argv) > 1 else "default"
    result = await reconcile_pending_payments(tenant)
    print(f"Reconciliation result for tenant={tenant}: {result}")


if __name__ == "__main__":
    asyncio.run(main())
