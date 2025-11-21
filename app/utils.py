# app/utils.py
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from passlib.context import CryptContext
import smtplib

from app.db.database import get_db
from app.models.user import User
from app.models.permissions import Permission
from app.models.user_role import UserRole
from app.models.role_permission import RolePermission


# ==========================================================
# JWT CONFIG
# ==========================================================
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


# ==========================================================
# PASSWORD HELPERS
# ==========================================================
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# ==========================================================
# TOKEN CREATION
# ==========================================================
def create_access_token(data: dict) -> str:
    """
    data = {"id": user_id, "email": user_email}
    """
    to_encode = {"id": data["id"], "email": data["email"]}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ==========================================================
# TOKEN → CURRENT USER
# ==========================================================
def get_current_user(token: str, db: Session):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("id")

        if not user_id:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise credentials_exception

    return user


def get_current_active_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    return get_current_user(token, db)


# ==========================================================
# PERMISSION SYSTEM
# ==========================================================
def get_user_permissions(user_id: int, db: Session):
    """
    Returns a set of permission names assigned to the user.
    """
    perms = (
        db.query(Permission.permission_name)
        .join(RolePermission, Permission.id == RolePermission.permission_id)
        .join(UserRole, RolePermission.role_id == UserRole.role_id)
        .filter(UserRole.user_id == user_id)
        .all()
    )
    return {p[0] for p in perms}


def check_permission(user: User, permission: str, db: Session):
    """
    Returns True if user has the specified permission.
    """
    user_perms = get_user_permissions(user.id, db)
    return permission in user_perms


def require_permission(permission: str):
    """
    Generic permission dependency.
    """
    def dependency(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
        if not check_permission(current_user, permission, db):
            raise HTTPException(
                status_code=403,
                detail=f"Permission '{permission}' required."
            )
        return True

    return dependency


# ==========================================================
# ADMIN-ONLY PROTECTION
# ==========================================================
def require_admin():
    """
    Allows ONLY Admin users.
    Admin must have permission: "admin_access"
    """
    def dependency(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
        if not check_permission(current_user, "admin_access", db):
            raise HTTPException(status_code=403, detail="Admin privilege required.")
        return True

    return dependency


# ==========================================================
# TASK-SPECIFIC PERMISSION DECORATOR
# ==========================================================
def require_task_permission(permission: str):
    """
    Decorator specifically for task routes.
    """
    def dependency(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
        if not check_permission(current_user, permission, db):
            raise HTTPException(
                status_code=403,
                detail=f"Task permission '{permission}' required."
            )
        return True

    return dependency


# ==========================================================
# EMAIL SENDER
# ==========================================================
def send_email(to, subject, body):
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login("abriq.revnix@gmail.com", "ndop pfsg kvjm zqqp")

    msg = f"Subject: {subject}\n\n{body}"
    server.sendmail("abriq.revnix@gmail.com", to, msg)
    server.quit()


# ==========================================================
# CENTRALIZED EXCEPTION HELPERS
# ==========================================================
def not_found(msg="Resource not found"):
    raise HTTPException(status_code=404, detail=msg)


def forbidden(msg="Forbidden"):
    raise HTTPException(status_code=403, detail=msg)
