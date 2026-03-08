from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# Define that each user will have an email, optional name and age
class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    age: Optional[int] = None

# Used in auth, when creating a user it will need a password
class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    profile_image_url: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Classic Token object token, used to return as JSON with acces_token and the token_type(usually bearer)
class Token(BaseModel):
    access_token: str
    token_type: str

# Used when creating a token
class TokenData(BaseModel):
    email: Optional[str] = None

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    id: int
    message: str
    response: str
    timestamp: datetime
    
    class Config:
        from_attributes = True
