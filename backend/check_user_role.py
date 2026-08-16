import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.config import get_settings
from app.infrastructure.models.user import User

async def check_user():
    settings = get_settings()
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB]
    await init_beanie(database=db, document_models=[User])
    
    user = await User.find_one({'email': 'machellialiyu@gmail.com'})
    if user:
        print(f'Email: {user.email}')
        print(f'Role: {user.role}')
        print(f'Role type: {type(user.role)}')
        print(f'Role value: {user.role.value if hasattr(user.role, "value") else str(user.role)}')
        print(f'Is Active: {user.is_active}')
        print(f'Is Verified: {user.is_verified}')
    else:
        print('User not found')
    
    client.close()

asyncio.run(check_user())
