from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = Field(
        default_factory=lambda: {
            "dietary": [],
            "mobility": "normal",
            "interests": ["sightseeing", "nature"],
            "travel_pace": "moderate"
        }
    )

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserPreferencesUpdate(BaseModel):
    dietary: Optional[List[str]] = None
    mobility: Optional[str] = None
    interests: Optional[List[str]] = None
    travel_pace: Optional[str] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class TokenPayload(BaseModel):
    sub: Optional[str] = None
