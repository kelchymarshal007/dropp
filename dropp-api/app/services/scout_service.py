from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.scout import WantedRequest
from app.models.user import User
from app.scout.mock_provider import MockSearchProvider
from app.scout.scoring import score_match, extract_price

def get_search_provider():
    # Factory: Swap for RealSearchProvider when API keys are ready
    return MockSearchProvider()

async def create_wanted_request(db: AsyncSession, buyer_id: str, data):
    # 1. Check Pro Tier
    user_result = await db.execute(select(User).where(User.id == buyer_id))
    user = user_result.scalar_one_or_none()

    if not user or user.tier != "pro_buyer":
        raise ValueError("Dropp Scout is a Pro feature. Upgrade to Pro Buyer.")

    # 2. Create Request
    new_request = WantedRequest(
        buyer_id=buyer_id,
        item_description=data.item_description,
        target_price_minor=data.target_price_minor,
        currency=data.currency.upper(),
        location=data.location,
        status="searching"
    )
    db.add(new_request)
    await db.commit()
    await db.refresh(new_request)
    return new_request

async def find_matches(db: AsyncSession, request_id: str) -> List[dict]:
    result = await db.execute(select(WantedRequest).where(WantedRequest.id == request_id))
    wanted = result.scalar_one_or_none()
    if not wanted:
        raise ValueError("Wanted request not found")

    keywords = [k.strip().lower() for k in wanted.item_description.split() if len(k) > 2]

    # 1. Search External platforms
    provider = get_search_provider()
    raw_results = provider.search(
        query=wanted.item_description,
        location=wanted.location,
        max_results=20
    )

    # 2. Score results
    scored = []
    for r in raw_results:
        score = score_match(r, wanted.target_price_minor, keywords)
        scored.append({
            "post_id": r["url"], # Using URL as ID for external results
            "seller_id": r["seller_handle"],
            "caption": r.get("title"),
            "media_url": r.get("image_url"),
            "price_minor": extract_price(r.get("price_display", "")),
            "currency": wanted.currency,
            "match_score": score
        })

    # 3. Sort and return Top 5
    scored.sort(key=lambda x: x["match_score"], reverse=True)
    return scored[:5]

async def fulfill_request(db: AsyncSession, request_id: str, buyer_id: str):
    result = await db.execute(
        select(WantedRequest).where(
            WantedRequest.id == request_id,
            WantedRequest.buyer_id == buyer_id
        )
    )
    wanted = result.scalar_one_or_none()
    if not wanted:
        raise ValueError("Wanted request not found or not owned by you")

    wanted.status = "fulfilled"
    await db.commit()
    await db.refresh(wanted)
    return wanted
