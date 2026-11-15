from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from uuid import UUID
from app.core.database import get_db
from app.models.user import User
from app.models.follow import Follow
from app.models.post import Post
from app.api.deps import get_current_user

router = APIRouter(prefix="/v1/users", tags=["Users"])

@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": str(current_user.id), "email": current_user.email,
        "handle": f"@{current_user.email.split('@')[0]}" if current_user.email else "@dropp_user",
        "is_seller": current_user.is_seller, "tier": current_user.tier,
        "followers": current_user.follower_count, "following": current_user.following_count,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None
    }

@router.get("/profile/{handle}")
async def get_public_profile(handle: str, db: AsyncSession = Depends(get_db)):
    clean_handle = handle.replace('@', '')
    # Match any email that starts with the handle, regardless of the domain
    result = await db.execute(
        select(User).where(User.email.ilike(f"{clean_handle}@%")).limit(1)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    posts_result = await db.execute(
        select(Post).where(Post.seller_id == str(user.id), Post.status == "active").order_by(Post.created_at.desc())
    )
    posts = posts_result.scalars().all()
    
    return {
        "id": str(user.id),
        "handle": f"@{user.email.split('@')[0]}",
        "followers": user.follower_count,
        "following": user.following_count,
        "posts": [{
            "id": str(p.id), "media_urls": p.media_urls, "media_type": p.media_type, 
            "likes": p.like_count, "caption": p.caption, "price_minor": p.price_minor
        } for p in posts]
    }

@router.get("/{user_id}/followers")
async def get_followers(user_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Follow).where(Follow.following_id == user_id))
    follows = result.scalars().all()
    follower_ids = [f.follower_id for f in follows]
    if not follower_ids: return []
    
    users_res = await db.execute(select(User).where(User.id.in_(follower_ids)))
    users = users_res.scalars().all()
    return [{"id": str(u.id), "handle": f"@{u.email.split('@')[0]}" if u.email else "@user"} for u in users]

@router.get("/{user_id}/following")
async def get_following(user_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Follow).where(Follow.follower_id == user_id))
    follows = result.scalars().all()
    following_ids = [f.following_id for f in follows]
    if not following_ids: return []
    
    users_res = await db.execute(select(User).where(User.id.in_(following_ids)))
    users = users_res.scalars().all()
    return [{"id": str(u.id), "handle": f"@{u.email.split('@')[0]}" if u.email else "@user"} for u in users]

@router.post("/{user_id}/follow")
async def toggle_follow(user_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    if str(current_user.id) == user_id:
        raise HTTPException(status_code=400, detail="You cannot follow yourself")
    
    result = await db.execute(select(Follow).where(Follow.follower_id == str(current_user.id), Follow.following_id == user_id))
    existing = result.scalar_one_or_none()
    
    is_following = False
    if existing:
        await db.delete(existing)
        await db.execute(update(User).where(User.id == str(current_user.id)).values(following_count=User.following_count - 1))
        await db.execute(update(User).where(User.id == user_id).values(follower_count=User.follower_count - 1))
    else:
        db.add(Follow(follower_id=str(current_user.id), following_id=user_id))
        await db.execute(update(User).where(User.id == str(current_user.id)).values(following_count=User.following_count + 1))
        await db.execute(update(User).where(User.id == user_id).values(follower_count=User.follower_count + 1))
        is_following = True
        
    await db.commit()
    return {"status": "following" if is_following else "unfollowed", "is_following": is_following}
