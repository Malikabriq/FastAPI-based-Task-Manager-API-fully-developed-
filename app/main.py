# app/main.py
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from sqlalchemy import inspect
from sqlalchemy.exc import OperationalError

from app.db.database import Base, engine
from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole
from app.models.permissions import Permission
from app.models.role_permission import RolePermission
from app.utils import hash_password

from app.routers.user import router as user_router
from app.routers.tasks import router as tasks_router
from app.routers.private.admin.admin import router as admin_router
from app.routers.auth import router as auth_router

from app.middleware import RateLimitMiddleware


# ----------------- LIFESPAN -----------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables
    Base.metadata.create_all(bind=engine)

    session = Session(bind=engine)
    inspector = inspect(engine)

    # Add "estimated_hours" column if missing
    columns = [col["name"] for col in inspector.get_columns("tasks")]
    if "estimated_hours" not in columns:
        try:
            with engine.connect() as conn:
                conn.execute("ALTER TABLE tasks ADD COLUMN estimated_hours FLOAT")
        except OperationalError:
            pass

    # Create default roles if not exist
    role_admin = session.query(Role).filter_by(role_name="Admin").first()
    role_user = session.query(Role).filter_by(role_name="User").first()

    if not role_admin:
        role_admin = Role(role_name="Admin", person_name="System")
        session.add(role_admin)
    if not role_user:
        role_user = Role(role_name="User", person_name="Default")
        session.add(role_user)
    session.commit()

    # Permissions
    permission_list = [
        ("task_create_any", "Admin create any task"),
        ("task_view_any", "Admin view all tasks"),
        ("task_update_any", "Admin update any task"),
        ("task_delete_any", "Admin delete any task"),
        ("task_create_own", "User create own task"),
        ("task_view_own", "User view own tasks"),
        ("task_update_own", "User update own tasks"),
        ("task_delete_own", "User delete own tasks"),
        ("user_create", "Admin can create users"),
        ("user_view_all", "Admin can see all users"),
        ("user_update", "Admin can update any user"),
        ("user_delete", "Admin can delete any user"),
    ]

    existing_names = {p.permission_name for p in session.query(Permission).all()}
    for name, desc in permission_list:
        if name not in existing_names:
            session.add(Permission(permission_name=name, description=desc))
    session.commit()

    # Assign permissions to roles
    all_permissions = {p.permission_name: p for p in session.query(Permission).all()}

    admin_perms = [
        "task_create_any", "task_view_any", "task_update_any", "task_delete_any",
        "user_create", "user_view_all", "user_update", "user_delete"
    ]
    for perm_name in admin_perms:
        perm = all_permissions.get(perm_name)
        if perm and not session.query(RolePermission).filter_by(role_id=role_admin.id, permission_id=perm.id).first():
            session.add(RolePermission(role_id=role_admin.id, permission_id=perm.id))

    user_perms = ["task_create_own", "task_view_own", "task_update_own", "task_delete_own"]
    for perm_name in user_perms:
        perm = all_permissions.get(perm_name)
        if perm and not session.query(RolePermission).filter_by(role_id=role_user.id, permission_id=perm.id).first():
            session.add(RolePermission(role_id=role_user.id, permission_id=perm.id))

    session.commit()

    # Create default admin user
    admin_user = session.query(User).filter_by(email="admin@example.com").first()
    if not admin_user:
        admin_user = User(
            name="Admin",
            email="admin@example.com",
            password=hash_password("admin123"),
            role="admin",
        )
        session.add(admin_user)
        session.commit()
        session.refresh(admin_user)

        if not session.query(UserRole).filter_by(user_id=admin_user.id, role_id=role_admin.id).first():
            session.add(UserRole(user_id=admin_user.id, role_id=role_admin.id))
            session.commit()

    session.close()
    yield


# ----------------- APP INIT -----------------
app = FastAPI(
    title="Task Manager API",
    version="1.0.0",
    description="RBAC-Based Task Manager",
    lifespan=lifespan
)

# ----------------- MIDDLEWARE -----------------
app.add_middleware(RateLimitMiddleware, max_requests=10, window=60)

# ----------------- ROUTERS -----------------
app.include_router(user_router, prefix="/users", tags=["Users"])
app.include_router(tasks_router, prefix="/tasks", tags=["Tasks"])
app.include_router(admin_router)  # ✅ No extra prefix
app.include_router(auth_router, prefix="/auth", tags=["Auth"])

# ----------------- ROOT -----------------
@app.get("/")
def root():
    return {"message": "Task Manager API is running!"}


# ----------------- CUSTOM OPENAPI -----------------
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(title=app.title, version=app.version, routes=app.routes)

    schema["components"]["securitySchemes"] = {
        "BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    }

    for path in schema["paths"].values():
        for method in path.values():
            if "login" not in method.get("operationId", "").lower():
                method["security"] = [{"BearerAuth": []}]

    app.openapi_schema = schema
    return schema


app.openapi = custom_openapi
