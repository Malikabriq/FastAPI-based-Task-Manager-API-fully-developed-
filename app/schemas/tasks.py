from pydantic import BaseModel, Field, computed_field
from typing import Literal, Optional

class Task(BaseModel):
    id: int = Field(..., description="Unique ID of the task", example=1)
    title: str = Field(..., description="Title of the task", example="Write report")
    description: str = Field(..., description="Detailed description of the task", example="Finish the quarterly report")
    priority: Literal["low", "medium", "high"] = Field(..., description="Priority of the task")
    status: Literal["pending", "in_progress", "completed"] = Field(..., description="Current status of the task")
    estimated_hours: float = Field(..., gt=0, description="Estimated hours", example=5.0)
    hours_spent: float = Field(..., ge=0, description="Hours spent", example=2.0)

    @computed_field
    @property
    def progress(self) -> float:
        """Compute task completion percentage."""
        return round((self.hours_spent / self.estimated_hours) * 100, 2) if self.estimated_hours else 0.0

    @computed_field
    @property
    def verdict(self) -> str:
        """Return a human-readable verdict based on progress."""
        if self.progress >= 100:
            return "Task Completed"
        elif self.progress >= 70:
            return "Almost Done"
        elif self.progress >= 30:
            return "In Progress"
        else:
            return 
class TaskCreate(BaseModel):
    title: str = Field(..., description="Title of the task", example="Write report")
    description: str = Field(..., description="Detailed description of the task", example="Finish the quarterly report")
    priority: Literal["low", "medium", "high"] = Field(..., description="Priority of the task")
    status: Literal["pending", "in_progress", "completed"] = Field(..., description="Current status of the task")
    estimated_hours: float = Field(..., gt=0, description="Estimated hours", example=5.0)
    hours_spent: float = False
class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, description="Title of the task")
    description: Optional[str] = Field(None, description="Detailed description of the task")
    priority: Optional[Literal["low", "medium", "high"]] = Field(None, description="Priority of the task")
    status: Optional[Literal["pending", "in_progress", "completed"]] = Field(None, description="Current status of the task")
    estimated_hours: Optional[float] = Field(None, gt=0, description="Estimated hours")
    hours_spent: Optional[float] = Field(None, ge=0, description="Hours spent")
