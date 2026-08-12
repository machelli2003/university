import pytest
from app.domain.admissions.waec_service import WAECService

@pytest.mark.asyncio
async def test_waec_service_manual_stub():
    service = WAECService()
    service.api_enabled = False
    verified, details, message = await service.verify_results("1234567890", 2024, "WASSCE")
    assert verified is False
    assert details is None
    assert "Manual verification required" in message

@pytest.mark.asyncio
async def test_waec_service_invalid_credentials():
    service = WAECService()
    valid, message = await service.validate_exam_credentials("1234567890", 2024, "INVALID")
    assert valid is False
    assert "Exam type must be one of" in message
