from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from app.core.database import get_db
from app.models.post import Post
from app.models.post_social import PostLike, PostComment
from app.models.user import User
from app.api.deps import get_current_user

router = APIRouter(prefix="/v1/feed", tags=["Reels Feed"])

@router.get("/")
async def get_feed(db: AsyncSession = Depends(get_db), limit: int = 10, offset: int = 0):
    result = await db.execute(
        select(Post)
        .where(Post.status == "active")
        .order_by(Post.created_at.desc())
        .limit(limit).offset(offset)
    )
    posts = result.scalars().all()
    
    return [{
        "id": str(p.id),
        "seller_id": str(p.seller_id),
        "media_url": p.media_url,
        "caption": p.caption,
        "price_minor": p.price_minor,
        "currency": p.currency,
        "likes": p.like_count,
        "comments": p.comment_count,
        "drops": p.dropp_count,
        "shares": p.share_count
    } for p in posts]

@router.post("/{post_id}/like")
async def toggle_like(post_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(PostLike).where(PostLike.post_id == post_id, PostLike.user_id == str(current_user.id)))
    existing_like = result.scalar_one_or_none()
    
    if existing_like:
        await db.delete(existing_like)
        await db.execute(update(Post).where(Post.id == post_id).values(like_count=Post.like_count - 1))
        await db.commit()
        return {"status": "unliked"}
    else:
        new_like = PostLike(post_id=post_id, user_id=str(current_user.id))
        db.add(new_like)
        await db.execute(update(Post).where(Post.id == post_id).values(like_count=Post.like_count + 1))
        await db.commit()
        return {"status": "liked"}

@router.post("/{post_id}/comment")
async def add_comment(post_id: str, payload: dict, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    body = payload.get("body")
    parent_id = payload.get("parent_id")
    
    if not body:
        raise HTTPException(status_code=400, detail="Comment body required")
        
    new_comment = PostComment(
        post_id=post_id,
        user_id=str(current_user.id),
        parent_id=parent_id,
        body=body
    )
    db.add(new_comment)
    await db.execute(update(Post).where(Post.id == post_id).values(comment_count=Post.comment_count + 1))
    await db.commit()
    
    return {"status": "ok", "comment_id": str(new_comment.id)}
