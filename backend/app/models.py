from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Comment(BaseModel):
    id: Optional[int] = None
    content: str
    key_points: List[str] = []
    is_public: bool = True
    created_at: datetime = datetime.now()

class CommentResponse(BaseModel):
    content: str
    key_points: List[str]
    is_public: bool

class CommentCreate(BaseModel):
    content: str
