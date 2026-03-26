from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from contextlib import asynccontextmanager
import shutil, os, tempfile, logging
import base64
from app.schemas import PostResponse, UserRead, UserCreate, UserUpdate
from app.db import Post, Like, Comment, create_db_and_tables, get_async_session, User
from app.images import imagekit
from app.users import auth_backend, current_active_user, fastapi_users




# ------------------ LOGGING ------------------
logging.basicConfig(level=logging.INFO)


# ------------------ LIFESPAN ------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield


app = FastAPI(title="Social Media API 🚀", lifespan=lifespan)


# ------------------ AUTH ------------------
app.include_router(fastapi_users.get_auth_router(auth_backend), prefix='/auth/jwt')
app.include_router(fastapi_users.get_register_router(UserRead, UserCreate), prefix="/auth")
app.include_router(fastapi_users.get_users_router(UserRead, UserUpdate), prefix="/users")


# ------------------ UPLOAD ------------------
@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    caption: str = Form(""),
    user=Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    try:
        # ✅ read file
        file_bytes = await file.read()

        # ✅ convert to base64
        encoded_file = base64.b64encode(file_bytes).decode()

        # ✅ upload to ImageKit
        upload = imagekit.upload_file(
            file=encoded_file,
            file_name=file.filename,
            options={
                "use_unique_file_name": True
            }
        )

        # ✅ get URL
        image_url = upload.response_metadata.raw["url"]

        # ✅ save to DB
        new_post = Post(
            user_id=str(user.id),
            caption=caption,
            url=image_url,
            file_type="image"
        )

        session.add(new_post)
        await session.commit()
        await session.refresh(new_post)

        return {"message": "Uploaded", "url": image_url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# ------------------ FEED (OPTIMIZED + PAGINATION) ------------------
from sqlalchemy import select

@app.get("/feed")
async def get_feed(
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(
        select(Post).order_by(Post.created_at.desc())
    )

    posts = result.scalars().all()

    data = []

    for post in posts:
        # ✅ GET LIKES
        likes_result = await session.execute(
            select(Like).where(Like.post_id == post.id)
        )
        likes = likes_result.scalars().all()

        # ✅ GET COMMENTS
        comments_result = await session.execute(
            select(Comment).where(Comment.post_id == post.id)
        )
        comments = comments_result.scalars().all()

        data.append({
            "id": post.id,
            "email": "user",
            "url": post.url,
            "caption": post.caption,
            "file_type": post.file_type,
            "likes": len(likes),  # 🔥 REAL COUNT
            "comments": [
                {"content": c.content} for c in comments
            ],
            "is_owner": str(post.user_id) == str(user.id)
        })

    return {"posts": data}

# ------------------ DELETE ------------------
@app.delete("/posts/{post_id}")
async def delete_post(
    post_id: str,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    result = await session.execute(select(Post).where(Post.id == post_id))
    post = result.scalars().first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.user_id != str(user.id):
        raise HTTPException(status_code=403, detail="Not allowed")

    await session.delete(post)
    await session.commit()

    return {"message": "Deleted successfully"}


# ------------------ LIKE ------------------
@app.post("/posts/{post_id}/like")
async def like_post(
    post_id: str,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    # 🔥 CHECK IF ALREADY LIKED
    result = await session.execute(
        select(Like).where(
            Like.post_id == post_id,
            Like.user_id == str(user.id)
        )
    )
    existing = result.scalars().first()

    if existing:
        return {"message": "Already liked"}

    like = Like(user_id=str(user.id), post_id=post_id)

    session.add(like)
    await session.commit()

    return {"message": "Liked"}


# ------------------ COMMENT ------------------

@app.post("/posts/{post_id}/comment")
async def add_comment(
    post_id: str,
    content: str = Form(...),
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    comment = Comment(
        user_id=str(user.id),
        post_id=post_id,
        content=content
    )

    session.add(comment)
    await session.commit()

    return {"message": "Comment added"} 