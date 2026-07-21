"""用户管理路由 — CRUD（需要admin权限）"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_role
from app.models.user import UserRole
from app.repositories.user_repo import UserRepository
from app.schemas.auth import UserCreate, UserInfo, UserListQuery, UserUpdate
from app.schemas.common import ApiResponse, PaginatedData
from app.models.user import User

router = APIRouter(prefix="/api/users", tags=["用户管理模块"])


@router.get("", response_model=ApiResponse[PaginatedData[UserInfo]], summary="获取用户列表")
async def get_users(
    page: int = 1,
    page_size: int = 20,
    role: UserRole | None = None,
    keyword: str | None = None,
    is_active: bool | None = None,
    _current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """分页查询系统用户列表（需要admin权限）。"""
    repo = UserRepository(db)
    users, total = await repo.get_list(
        page=page,
        page_size=page_size,
        role=role,
        keyword=keyword,
        is_active=is_active,
    )
    pages = (total + page_size - 1) // page_size
    items = [UserInfo.model_validate(u) for u in users]
    return ApiResponse(
        code=200,
        message="success",
        data=PaginatedData(items=items, total=total, page=page, page_size=page_size, pages=pages),
    )





@router.put("/{user_id}", response_model=ApiResponse[UserInfo], summary="更新用户信息")
async def update_user(
    user_id: int,
    data: UserUpdate,
    _current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """更新指定用户的信息（需要admin权限）。"""
    repo = UserRepository(db)
    user = await repo.update(user_id, data)
    return ApiResponse(code=200, message="用户信息更新成功", data=UserInfo.model_validate(user))


@router.delete("/{user_id}", response_model=ApiResponse, summary="删除用户")
async def delete_user(
    user_id: int,
    _current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """删除指定用户（软删除，需要admin权限）。"""
    repo = UserRepository(db)
    await repo.soft_delete(user_id)
    return ApiResponse(code=200, message="用户已删除", data=None)
