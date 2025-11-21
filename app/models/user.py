from sqlalchemy import Column, String, Integer, Enum, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.db.database import Base
from app.models.enums import RoleEnum

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="user")  # role: user/admin
    reset_code = Column(String, nullable=True)
    reset_expires_at = Column(DateTime, nullable=True)
    reset_verified = Column(Boolean, default=False)  # <-- NEW COLUMN

    tasks = relationship(
        "Task",
        back_populates="owner",
        cascade="all, delete-orphan"
    )

    user_roles = relationship(
        "UserRole",
        back_populates="user",
        cascade="all, delete-orphan"
    )
