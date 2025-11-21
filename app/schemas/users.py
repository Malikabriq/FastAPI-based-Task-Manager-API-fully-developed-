from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Literal
from app.schemas.tasks import Task  # for embedding tasks in user responses


# ---------------------------
# BASE USER (shared fields)
# ---------------------------
class UserBase(BaseModel):
    name: str = Field(..., description="Full name of the user", example="John Doe")
    email: EmailStr = Field(..., description="Email address of the user", example="john@example.com")


# ---------------------------
# NORMAL USER REGISTRATION (no role field)
# ---------------------------
class UserCreate(UserBase):
    password: str = Field(..., description="Password for the account", example="strongpassword123")
    # 🔥 Role removed — users cannot choose role


# ---------------------------
# ADMIN CREATES A USER (role allowed)
# ---------------------------
class AdminUserCreate(UserBase):
    password: str = Field(..., description="Password for the account")
    role: Literal["user", "admin"] = Field(..., description="Role assigned by admin")


# ---------------------------
# UPDATE USER (admin only)
# ---------------------------
class UserUpdate(BaseModel):
    name: Optional[str] = Field(None)
    email: Optional[EmailStr] = Field(None)
    password: Optional[str] = Field(None)
    role: Optional[Literal["user", "admin"]] = Field(None)  # admin may update role


# ---------------------------
# RESPONSE MODELS
# ---------------------------
class UserResponse(UserBase):
    id: int = Field(..., description="Unique ID of the user", example=1)
    role: str = Field(..., description="Role of the user", example="user")

    class Config:
        from_attributes = True  # Pydantic v2 ORM support


class UserWithTasks(UserResponse):
    tasks: List[Task] = Field(default_factory=list)
