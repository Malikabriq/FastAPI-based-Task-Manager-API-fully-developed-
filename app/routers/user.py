# app/routers/user.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.database import get_db
from app.schemas.users import UserCreate, UserResponse
from app.models.user import User
from app.models.user_role import UserRole
from app.models.role import Role
from app.utils import hash_password, verify_password, create_access_token, not_found

router = APIRouter(prefix="/users", tags=["Users"])


# -----------------------------------------------------
# PUBLIC REGISTER (Normal user)
# -----------------------------------------------------
@router.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pwd = hash_password(user.password)

    new_user = User(
        name=user.name,
        email=user.email,
        password=hashed_pwd,
        role="user"    # <-- FIXED
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Assign default User role
    role_user = db.query(Role).filter(Role.role_name == "user").first()
    if role_user:
        db.add(UserRole(user_id=new_user.id, role_id=role_user.id))
        db.commit()

    return new_user



# -----------------------------------------------------
# LOGIN (email + password)
# -----------------------------------------------------
class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    # Check user exists
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    if not verify_password(data.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    # Generate token
    token = create_access_token({"id": user.id, "email": user.email})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
        }
    }
