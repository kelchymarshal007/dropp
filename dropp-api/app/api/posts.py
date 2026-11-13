import os
import shutil
import uuid
from fastapi import APIRouter, UploadFile, File, Form, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.user import User
from app.models.post import Post
from app.api.deps import get_current_user

router = APIRouter(prefix="/v1/posts", tags=["Reels"])

TEMP_MEDIA_DIR = "/tmp/media_raw"
os.makedirs(TEMP_MEDIA_DIR, exist_ok=True)

@router.post("/upload")
async def upload_reel(
    file: UploadFile = File(...),
    caption: str = Form(None),
    price_minor: int = Form(None),
    currency: str = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    file_id = str(uuid.uuid4())
    file_extension = file.filename.split(".")[-1]
    temp_path = os.path.join(TEMP_MEDIA_DIR, f"{file_id}.{file_extension}")
    
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    new_post = Post(
        seller_id=str(current_user.id),
        media_type="video" if file_extension in ["mp4", "mov"] else "image",
        caption=caption,
        price_minor=price_minor,
        currency=currency.upper() if currency else None,
        status="active"
    )
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)

    return {
        "status": "accepted", 
        "post_id": str(new_post.id), 
        "message": "Reel uploaded."
    }
