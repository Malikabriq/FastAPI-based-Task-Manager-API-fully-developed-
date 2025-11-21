# app/routers/private/admin/admin.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.users import AdminUserCreate, UserResponse
from app.models.user import User
from app.models.user_role import UserRole
from app.models.role import Role
from app.utils import hash_password, get_current_active_user, require_permission, not_found

router = APIRouter(prefix="/admin/users", tags=["Admin Users"])


# -----------------------------------------------------
# ADMIN → CREATE USER
# -----------------------------------------------------
@router.post(
    "/",
    response_model=UserResponse,
    dependencies=[Depends(require_permission("user_create"))]
)
def create_user_admin(
    user: AdminUserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):

    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pwd = hash_password(user.password)

    new_user = User(
        name=user.name,
        email=user.email,
        password=hashed_pwd,
        role=user.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Assign role using UserRole
    role_obj = db.query(Role).filter(Role.role_name.ilike(user.role)).first()
    if role_obj:
        db.add(UserRole(user_id=new_user.id, role_id=role_obj.id))
        db.commit()

    return new_user


# -----------------------------------------------------
# ADMIN → VIEW ALL USERS
# -----------------------------------------------------
@router.get(
    "/",
    response_model=list[UserResponse],
    dependencies=[Depends(require_permission("user_view_all"))]
)
def get_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return db.query(User).all()


# -----------------------------------------------------
# ADMIN → UPDATE ANY USER
# -----------------------------------------------------
@router.put(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[Depends(require_permission("user_update"))]
)
def update_user(
    user_id: int,
    user: AdminUserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):

    existing = db.query(User).filter(User.id == user_id).first()
    if not existing:
        not_found("User not found")

    existing.name = user.name
    existing.email = user.email
    existing.password = hash_password(user.password)
    existing.role = user.role

    db.commit()
    db.refresh(existing)

    return existing


# -----------------------------------------------------
# ADMIN → DELETE ANY USER
# -----------------------------------------------------
@router.delete(
    "/{user_id}",
    dependencies=[Depends(require_permission("user_delete"))]
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        not_found("User not found")

    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}
