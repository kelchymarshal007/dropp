from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Form, File, UploadFile
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, desc
from typing import Optional, List
from uuid import UUID, uuid4
import os
import shutil
from app.core.database import get_db
from app.models.post import Post
from app.models.post_social import PostLike, PostComment, CommentLike
from app.models.bookmark import Bookmark
from app.models.user import User
from app.models.follow import Follow
from app.core.security import verify_access_token
from app.websockets.chat_manager import chat_manager

router = APIRouter(prefix="/v1/feed", tags=["Reels Feed"])
optional_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/login/email", auto_error=False)

MEDIA_DIR = "/tmp/media_raw"
os.makedirs(MEDIA_DIR, exist_ok=True)


async def get_optional_user(token: Optional[str] = Depends(optional_oauth2_scheme), db: AsyncSession = Depends(get_db)):
    if not token:
        return None
    user_id = verify_access_token(token)
    if not user_id:
        return None
    try:
        user_uuid = UUID(str(user_id))
    except Exception:
        return None
    result = await db.execute(select(User).where(User.id == user_uuid))
    return result.scalar_one_or_none()


@router.websocket("/ws/{post_id}")
async def feed_websocket(websocket: WebSocket, post_id: str):
    await chat_manager.connect(websocket, f"feed_{post_id}")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        chat_manager.disconnect(websocket, f"feed_{post_id}")


@router.get("")
@router.get("/")
async def get_feed(db: AsyncSession = Depends(get_db), limit: int = 10, offset: int = 0, current_user: Optional[User] = Depends(get_optional_user)):
    result = await db.execute(select(Post).where(Post.status == "active").order_by(Post.created_at.desc()).limit(limit).offset(offset))
    posts = result.scalars().all()
    if not posts:
        return []
    seller_ids = [UUID(str(p.seller_id)) for p in posts if p.seller_id]
    users = {}
    if seller_ids:
        user_result = await db.execute(select(User).where(User.id.in_(seller_ids)))
        users = {str(u.id): u for u in user_result.scalars().all()}
    liked_post_ids = set()
    followed_seller_ids = set()
    if current_user:
        post_ids = [str(p.id) for p in posts]
        likes_result = await db.execute(select(PostLike.post_id).where(PostLike.user_id == str(current_user.id), PostLike.post_id.in_(post_ids)))
        liked_post_ids = {str(row) for row in likes_result.scalars().all()}
        follow_result = await db.execute(select(Follow.following_id).where(Follow.follower_id == str(current_user.id)))
        followed_seller_ids = {str(row) for row in follow_result.scalars().all()}
    bookmarked_post_ids = set()
    if current_user:
        bookmark_result = await db.execute(select(Bookmark.item_id).where(Bookmark.item_type == "post", Bookmark.user_id == str(current_user.id)))
        bookmarked_post_ids = {str(row) for row in bookmark_result.scalars().all()}
    feed = []
    for post in posts:
        seller = users.get(str(post.seller_id))
        handle = f"@{seller.email.split('@')[0]}" if seller and seller.email else "@user"
        feed.append({
            "id": str(post.id),
            "seller_id": str(post.seller_id),
            "seller_handle": handle,
            "media_urls": post.media_urls,
            "media_type": post.media_type,
            "caption": post.caption,
            "price_minor": post.price_minor,
            "currency": post.currency,
            "likes": post.like_count,
            "comments": post.comment_count,
            "drops": post.dropp_count,
            "shares": post.share_count,
            "is_liked": str(post.id) in liked_post_ids,
            "is_following": str(post.seller_id) in followed_seller_ids,
            "is_bookmarked": str(post.id) in bookmarked_post_ids,
            "created_at": post.created_at.isoformat() if post.created_at else None
        })
    return feed


@router.post("/{post_id}/like")
async def toggle_like(post_id: str, db: AsyncSession = Depends(get_db), current_user: Optional[User] = Depends(get_optional_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    result = await db.execute(select(PostLike).where(PostLike.post_id == post_id, PostLike.user_id == str(current_user.id)))
    existing_like = result.scalar_one_or_none()
    is_liked = False
    if existing_like:
        await db.delete(existing_like)
        await db.execute(update(Post).where(Post.id == post_id).values(like_count=Post.like_count - 1))
    else:
        db.add(PostLike(post_id=post_id, user_id=str(current_user.id)))
        await db.execute(update(Post).where(Post.id == post_id).values(like_count=Post.like_count + 1))
        is_liked = True
    await db.commit()
    new_count = (await db.execute(select(Post.like_count).where(Post.id == post_id))).scalar()
    await chat_manager.publish_to_redis(f"feed_{post_id}", {"type": "like_update", "post_id": post_id, "likes": new_count})
    return {"status": "liked" if is_liked else "unliked", "likes": new_count}


@router.get("/{post_id}/comments")
async def get_comments(post_id: str, db: AsyncSession = Depends(get_db), current_user: Optional[User] = Depends(get_optional_user)):
    result = await db.execute(select(PostComment).where(PostComment.post_id == post_id).order_by(desc(PostComment.created_at)))
    comments = result.scalars().all()
    user_ids = list(set([UUID(str(c.user_id)) for c in comments if c.user_id]))
    users = {}
    if user_ids:
        u_res = await db.execute(select(User).where(User.id.in_(user_ids)))
        users = {str(u.id): u for u in u_res.scalars().all()}
    liked_comments = set()
    if current_user and comments:
        c_ids = [str(c.id) for c in comments]
        cl_res = await db.execute(select(CommentLike.comment_id).where(CommentLike.user_id == str(current_user.id), CommentLike.comment_id.in_(c_ids)))
        liked_comments = {str(row) for row in cl_res.scalars().all()}
    return [{
        "id": str(c.id),
        "user_id": str(c.user_id),
        "handle": f"@{users[str(c.user_id)].email.split('@')[0]}" if str(c.user_id) in users else "@user",
        "body": c.body,
        "parent_id": c.parent_id,
        "like_count": c.like_count,
        "media_urls": c.media_urls or [],
        "is_liked": str(c.id) in liked_comments,
        "created_at": c.created_at.isoformat()
    } for c in comments]


@router.post("/{post_id}/comment")
async def add_comment(
    post_id: str,
    body: str = Form(...),
    parent_id: Optional[str] = Form(None),
    files: List[UploadFile] = File(default=[]),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    media_urls = []
    for file in files:
        if not file.filename:
            continue
        ext = file.filename.split(".")[-1].lower() if "." in file.filename else "bin"
        file_id = str(uuid4())
        temp_path = os.path.join(MEDIA_DIR, f"{file_id}.{ext}")
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        media_urls.append(f"/media/{file_id}.{ext}")

    db.add(PostComment(
        post_id=post_id,
        user_id=str(current_user.id),
        body=body,
        parent_id=parent_id if parent_id else None,
        media_urls=media_urls
    ))
    await db.execute(update(Post).where(Post.id == post_id).values(comment_count=Post.comment_count + 1))
    await db.commit()

    new_count = (await db.execute(select(Post.comment_count).where(Post.id == post_id))).scalar()
    await chat_manager.publish_to_redis(f"feed_{post_id}", {"type": "comment_update", "post_id": post_id, "comments": new_count})
    return {"status": "ok", "comments": new_count}


@router.post("/comments/{comment_id}/like")
async def toggle_comment_like(comment_id: str, db: AsyncSession = Depends(get_db), current_user: Optional[User] = Depends(get_optional_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    result = await db.execute(select(CommentLike).where(CommentLike.comment_id == comment_id, CommentLike.user_id == str(current_user.id)))
    existing = result.scalar_one_or_none()
    is_liked = False
    if existing:
        await db.delete(existing)
        await db.execute(update(PostComment).where(PostComment.id == comment_id).values(like_count=PostComment.like_count - 1))
    else:
        db.add(CommentLike(comment_id=comment_id, user_id=str(current_user.id)))
        await db.execute(update(PostComment).where(PostComment.id == comment_id).values(like_count=PostComment.like_count + 1))
        is_liked = True
    await db.commit()
    new_count = (await db.execute(select(PostComment.like_count).where(PostComment.id == comment_id))).scalar()
    return {"status": "liked" if is_liked else "unliked", "likes": new_count}


@router.post("/{post_id}/bookmark")
async def toggle_bookmark(post_id: str, payload: dict, db: AsyncSession = Depends(get_db), current_user: Optional[User] = Depends(get_optional_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    item_type = payload.get("item_type", "post")
    item_id = payload.get("item_id", post_id)
    
    result = await db.execute(select(Bookmark).where(Bookmark.item_id == item_id, Bookmark.item_type == item_type, Bookmark.user_id == str(current_user.id)))
    existing = result.scalar_one_or_none()
    is_bookmarked = False
    if existing:
        await db.delete(existing)
    else:
        db.add(Bookmark(item_id=item_id, item_type=item_type, user_id=str(current_user.id)))
        is_bookmarked = True
    await db.commit()
    return {"status": "bookmarked" if is_bookmarked else "unbookmarked", "is_bookmarked": is_bookmarked}

@router.get("/bookmarks")
async def get_bookmarks(db: AsyncSession = Depends(get_db), current_user: Optional[User] = Depends(get_optional_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    result = await db.execute(select(Bookmark).where(Bookmark.user_id == str(current_user.id)).order_by(Bookmark.created_at.desc()))
    bookmarks = result.scalars().all()
    
    post_ids = [b.item_id for b in bookmarks if b.item_type == 'post']
    comment_ids = [b.item_id for b in bookmarks if b.item_type == 'comment']
    
    saved_posts = []
    if post_ids:
        posts_result = await db.execute(select(Post).where(Post.id.in_(post_ids)))
        posts_map = {str(p.id): p for p in posts_result.scalars().all()}
        for b in bookmarks:
            if b.item_type == 'post' and b.item_id in posts_map:
                p = posts_map[b.item_id]
                saved_posts.append({"type": "post", "id": str(p.id), "media_urls": p.media_urls, "media_type": p.media_type, "caption": p.caption})
                
    saved_comments = []
    if comment_ids:
        c_result = await db.execute(select(PostComment).where(PostComment.id.in_(comment_ids)))
        comments_map = {str(c.id): c for c in c_result.scalars().all()}
        for b in bookmarks:
            if b.item_type == 'comment' and b.item_id in comments_map:
                c = comments_map[b.item_id]
                saved_comments.append({"type": "comment", "id": str(c.id), "post_id": str(c.post_id), "body": c.body, "created_at": c.created_at.isoformat()})

    return {"posts": saved_posts, "comments": saved_comments}
