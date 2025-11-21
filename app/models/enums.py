# app/models/enums.py
import enum

class PriorityEnum(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"

class StatusEnum(str, enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"

class RoleEnum(str, enum.Enum):
    admin = "admin"
    user = "user"
