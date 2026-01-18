from fastapi import FastAPI, HTTPException, File, UploadFile, Depends, Form
from app.schemas import NewPost, NewPostResponse, UserRead, UserCreate, UserUpdate
from app.db import Post,create_db_and_tables, get_async_session, User
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select
from app.images import imagekit 
#from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions

import shutil
import os
import uuid
import tempfile

from app.users import current_active_user,auth_backend,fastapi_users


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create database and tables
    await create_db_and_tables()
    yield
    # Shutdown: any cleanup can be done here if necessary


app = FastAPI(lifespan=lifespan)


app.include_router(fastapi_users.get_auth_router(auth_backend),prefix="/auth/jwt", tags=["auth"])
app.include_router(fastapi_users.get_register_router(UserRead,UserCreate),prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_reset_password_router(),prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_verify_router(UserRead),prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_users_router(UserRead,UserUpdate),prefix="/users", tags=["users"])

#upload-posts

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    caption: str = Form(...),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user)
):
    
    temp_file_path = None

    try:
        with tempfile.NamedTemporaryFile(delete=False,suffix=os.path.splitext(file.filename)[1]) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name

        upload_result = imagekit.files.upload(
            file=open(temp_file_path, 'rb'),
            file_name=file.filename,
            folder="/imagefeed-uploads",
            tags=["backend-upload"],
            
            
        )

        if upload_result.url is not None:
              new_post = Post(
                    caption=caption, 
                    user_id=user.id,
                    url= upload_result.url, 
                    file_type="video" if file.content_type.startswith("video/") else "image", 
                    file_name=upload_result.name,)
              
              session.add(new_post)
              await session.commit()
              await session.refresh(new_post)      
              return new_post
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
            file.file.close()
    
            

   


#feed

@app.get("/feed")
async def feed(session: AsyncSession = Depends(get_async_session), user: User = Depends(current_active_user)):
    
    result = await session.execute(
        select(Post).order_by(Post.created_at.desc())
    )
    posts = [row[0] for row in result.all()]


    result = await session.execute(select(User))
    users = [row[0] for row in result.all()]

    user_dict = {u.id: u.email for u in users}

    posts_data = []

    for post in posts:
        posts_data.append({
            "id": str(post.id),
            "caption": post.caption,
            "url": post.url,
            "file_type": post.file_type,
            "file_name": post.file_name,
            "created_at": post.created_at.isoformat(),
            "user_id": str(post.user_id),
            "is_owner": post.user_id == user.id,
            "email": user_dict.get(post.user_id, "unknown")
            
        })

    return {"posts": posts_data}    




   
#delete-posts
@app.delete("/posts/{post_id}")
async def delete_post(post_id: str, session: AsyncSession = Depends(get_async_session), user: User = Depends(current_active_user)):
    
    try:
        post_id = uuid.UUID(post_id)
        result = await session.execute(select(Post).where(Post.id == post_id))
        post = result.scalars().first() 
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        if post.user_id != user.id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this post")

        await session.delete(post)
        await session.commit()
        return {"success": True, "message": "Post deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting post: {str(e)}")

  
    




'''
text_posts = {1:{"title":"First Title","content":"First Content"},
       2:{"title":"Second Title","content":"Second Content"},
       3:{"title":"Third Title","content":"Third Content"}}





@app.get('/hello')
def hello():
    return {'message':"hello world"}


@app.get("/posts")
def get_posts(limit: int = None):

    if limit:

        return list(text_posts.values())[:limit]

    return text_posts

@app.get('/posts/{id}')
def get_post(id: int):

    if id not in text_posts:
        raise HTTPException(status_code=404, detail="Post not found")
   
    posts = text_posts.get(id)

    return posts

@app.post('/posts')
def create_posts(post: NewPost)-> NewPostResponse:
    
    new_post = {"title": post.title, "content": post.content}
    text_posts[max(text_posts.keys()) + 1] = new_post
    
    return new_post


'''
