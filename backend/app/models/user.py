"""User model with UUID v7 primary key."""
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import String
from datetime import datetime
from typing import Optional
from uuid import UUID
from app.utils.uuid_utils import generate_uuid7


class User(SQLModel, table=True):
    """User account model.
    
    Attributes:
        id: UUID v7 primary key (time-ordered)
        email: Unique email address
        password_hash: Hashed password
        plan: Subscription plan (FREE, PRO, ENTERPRISE)
        minutes_used: Total minutes of video generated
        created_at: Account creation timestamp
        updated_at: Last update timestamp
    """
    __tablename__ = "user"
    
    id: UUID = Field(
        default_factory=generate_uuid7,
        primary_key=True,
        nullable=False
    )
    email: str = Field(
        sa_column=Column(String, unique=True, index=True, nullable=False)
    )
    password_hash: str = Field(nullable=False)
    plan: str = Field(default="FREE", nullable=False)  # Will be PostgreSQL ENUM
    minutes_used: int = Field(default=0, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
