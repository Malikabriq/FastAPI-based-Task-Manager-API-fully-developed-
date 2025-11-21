from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.crud import tasks as task_crud
from app.schemas.tasks import Task as TaskSchema, TaskCreate, TaskUpdate
from app.models.user import User
from app.utils import get_current_active_user, require_permission, not_found, forbidden

router = APIRouter(prefix="/tasks", tags=["Tasks"])


# -----------------------------------------------------
# READ TASKS
# - Admin with task_view_any sees all tasks
# - Normal user sees only own tasks
# -----------------------------------------------------
@router.get("/", response_model=List[TaskSchema])
def read_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Admin global view permission
    user_permissions = task_crud.get_user_permissions(current_user.id, db)
    if "task_view_any" in user_permissions:
        return task_crud.get_all_tasks(db)

    # Normal user: only own tasks
    return task_crud.get_tasks_by_user(db, current_user.id)


# -----------------------------------------------------
# CREATE TASK
# - Admin with task_create_any may create for any user
# - Normal user can create own tasks (task_create_own)
# -----------------------------------------------------
@router.post("/", response_model=TaskSchema)
def create_task(
    payload: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    user_permissions = task_crud.get_user_permissions(current_user.id, db)

    if "task_create_any" in user_permissions and payload.owner_id:
        owner_id = payload.owner_id
    else:
        owner_id = current_user.id

    new_task = task_crud.create_task(db, payload, owner_id)
    return new_task


# -----------------------------------------------------
# UPDATE TASK
# - Admin with task_update_any can update any
# - Normal user can update own only
# -----------------------------------------------------
@router.put("/{task_id}", response_model=TaskSchema)
def update_task(
    task_id: int,
    updates: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    user_permissions = task_crud.get_user_permissions(current_user.id, db)
    task = task_crud.get_task_by_id(db, task_id)

    if not task:
        not_found("Task not found")

    if "task_update_any" in user_permissions:
        updated = task_crud.update_task_admin(db, task_id, updates)
        return updated

    # Must be owner
    if task.owner_id != current_user.id:
        forbidden("You cannot update this task")

    updated = task_crud.update_task_for_user(db, task_id, current_user.id, updates)
    if not updated:
        not_found("Task not found")
    return updated


# -----------------------------------------------------
# DELETE TASK
# - Admin with task_delete_any can delete any
# - Normal user can delete own only
# -----------------------------------------------------
@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    user_permissions = task_crud.get_user_permissions(current_user.id, db)
    task = task_crud.get_task_by_id(db, task_id)

    if not task:
        not_found("Task not found")

    if "task_delete_any" in user_permissions:
        ok = task_crud.delete_task_admin(db, task_id)
        return {"message": "Task deleted"} if ok else not_found("Task not found")

    # Must be owner
    if task.owner_id != current_user.id:
        forbidden("You cannot delete this task")

    ok = task_crud.delete_task_for_user(db, task_id, current_user.id)
    return {"message": "Task deleted"} if ok else not_found("Task not found")
