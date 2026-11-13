import random
import string
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.dropp import Dropp
from app.schemas.dropp import DroppCreate

def generate_short_code(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

async def create_dropp(db: AsyncSession, data: DroppCreate, buyer_id: str):
    # Ensure currency is uppercase (e.g., NGN, not ngn)
    currency_upper = data.currency.upper()
    
    new_dropp = Dropp(
        code=generate_short_code(),
        buyer_id=buyer_id, # Injected securely from the JWT
        source_url=data.source_url,
        source_platform=data.source_platform.lower(),
        title=data.title,
        currency=currency_upper,
        offer_minor=data.offer_minor,
        image_url=data.image_url,
        status="sent"
    )
    
    db.add(new_dropp)
    await db.commit()
    await db.refresh(new_dropp)
    return new_dropp
