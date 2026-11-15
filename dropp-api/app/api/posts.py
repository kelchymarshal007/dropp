import os
import shutil
import uuid
from typing import List
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.models.user import User
from app.models.post import Post
from app.api.deps import get_current_user

router = APIRouter(prefix="/v1/posts", tags=["Reels"])
TEMP_MEDIA_DIR = "/tmp/media_raw"
os.makedirs(TEMP_MEDIA_DIR, exist_ok=True)

@router.get("/my-reels")
async def get_my_reels(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Post).where(Post.seller_id == str(current_user.id)).order_by(Post.created_at.desc()))
    posts = result.scalars().all()
    return [{
        "id": str(p.id), "media_urls": p.media_urls, "media_type": p.media_type,
        "caption": p.caption, "price_minor": p.price_minor, "currency": p.currency,
        "likes": p.like_count, "comments": p.comment_count
    } for p in posts]

@router.post("/upload")
async def upload_post(
    files: List[UploadFile] = File(...),
    caption: str = Form(None),
    price_minor: int = Form(None),
    currency: str = Form(None),
    category: str = Form(None),
    subcategory: str = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    media_urls = []
    media_type = "video"

    for file in files:
        file_id = str(uuid.uuid4())
        ext = file.filename.split(".")[-1].lower()
        temp_path = os.path.join(TEMP_MEDIA_DIR, f"{file_id}.{ext}")
        
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # In Production: Upload to S3 here and append S3 URL. 
        # For local dev, we serve from localhost.
        media_urls.append(f"/media/{file_id}.{ext}")
        
        if ext in ["jpg", "jpeg", "png", "webp"]:
            media_type = "carousel"

    new_post = Post(
        seller_id=str(current_user.id),
        media_urls=media_urls,
        media_type=media_type,
        caption=caption,
        price_minor=price_minor,
        currency=currency.upper() if currency else None,
        category=category,
        subcategory=subcategory,
        status="active"
    )
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)

    return {"status": "accepted", "post_id": str(new_post.id)}
