"""用户 ORM 模型"""

import enum
from datetime import datetime

from sqlalchemy import Boolean, Enum, Integer, String, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
# 这是一个测试修改

class UserRole(str, enum.Enum):
    """用户角色枚举"""
    # 系统管理员
    ADMIN = "admin"
    # 技术负责人
    TECH_LEAD = "tech_lead"
    # 开发人员
    DEVELOPER = "developer"
    # 运维人员
    DEVOPS = "devops"
    # 只读用户
    VIEWER = "viewer"


class User(Base):
    """系统用户表"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role", create_type=False, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        default=UserRole.DEVELOPER,
    )
    github_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_login_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
