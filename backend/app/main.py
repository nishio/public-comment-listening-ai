from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import logging
import traceback

logging.basicConfig(level=logging.INFO)
from .models import Comment, CommentResponse, CommentCreate
from .llm import extract_key_points

app = FastAPI()

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# インメモリデータストア
comments: List[Comment] = []

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.post("/extract")
async def extract_key_points_endpoint(comment: CommentCreate) -> List[str]:
    try:
        key_points = await extract_key_points(comment.content)
        return key_points
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/comments", response_model=CommentResponse)
async def create_comment(comment: CommentCreate):
    logging.info(f"Received comment: {comment.content[:50]}...")
    
    if not comment.content:
        raise HTTPException(status_code=400, detail="コメント内容は必須です")
    
    try:
        # LLMで要点を抽出
        logging.info("Extracting key points...")
        key_points = await extract_key_points(comment.content)
        logging.info(f"Extracted key points: {key_points}")
        
        # コメントを保存
        new_comment = Comment(
            id=len(comments),
            content=comment.content,
            key_points=key_points,
            is_public=True
        )
        comments.append(new_comment)
        
        return CommentResponse(
            content=new_comment.content,
            key_points=new_comment.key_points,
            is_public=new_comment.is_public
        )
    except Exception as e:
        error_detail = f"Error processing comment: {str(e)}\n{traceback.format_exc()}"
        logging.error(error_detail)
        raise HTTPException(
            status_code=500,
            detail="コメントの処理中にエラーが発生しました。詳細: " + str(e)
        )

@app.get("/api/comments", response_model=List[CommentResponse])
async def list_comments(show_private: bool = False):
    if show_private:
        return [CommentResponse(**comment.dict()) for comment in comments]
    return [CommentResponse(**comment.dict()) for comment in comments if comment.is_public]

@app.patch("/api/comments/{comment_id}/visibility")
async def update_comment_visibility(comment_id: int, is_public: bool):
    if comment_id >= len(comments):
        raise HTTPException(status_code=404, detail="コメントが見つかりません")
    
    comments[comment_id].is_public = is_public
    return {"status": "ok"}
