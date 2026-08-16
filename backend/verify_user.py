import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.config import get_settings
from app.infrastructure.models.user import User
from datetime import datetime

async def verify_user():
    settings = get_settings()
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB]
    await init_beanie(database=db, document_models=[User])
    
    user = await User.find_one({'email': 'machellialiyu@gmail.com'})
    if user:
        print(f'Before: Is Verified: {user.is_verified}')
        user.is_verified = True
        user.email_verified_at = datetime.utcnow()
        await user.save()
        print(f'After: Is Verified: {user.is_verified}')
        print('User verified successfully!')
    else:
        print('User not found')
    
    client.close()

asyncio.run(verify_user())
