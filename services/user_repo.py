"""用户数据访问层"""

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationException, ConflictException, NotFoundException
from app.core.security import get_password_hash, verify_password
from app.models.user import User, UserRole
from app.schemas.auth import PasswordChange, ProfileUpdate, UserCreate, UserUpdate


class UserRepository:
    """用户 Repository"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int) -> User:
        """按ID查询用户"""
        result = await self.db.execute(
            select(User).where(User.id == user_id, User.deleted_at.is_(None))
        )
        user = result.scalar_one_or_none()
        if not user:
            raise NotFoundException("用户", user_id)
        return user

    async def get_by_username(self, username: str) -> User | None:
        """按用户名查询"""
        result = await self.db.execute(
            select(User).where(User.username == username, User.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """按邮箱查询"""
        result = await self.db.execute(
            select(User).where(User.email == email, User.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_by_username_or_email(self, username: str) -> User | None:
        """按用户名或邮箱查询"""
        result = await self.db.execute(
            select(User).where(
                (User.username == username) | (User.email == username),
                User.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_list(
        self,
        page: int = 1,
        page_size: int = 20,
        role: UserRole | None = None,
        keyword: str | None = None,
        is_active: bool | None = None,
    ) -> tuple[list[User], int]:
        """分页查询用户列表"""
        query = select(User).where(User.deleted_at.is_(None))

        # 角色过滤
        if role is not None:
            query = query.where(User.role == role)

        # 关键词搜索
        if keyword:
            pattern = f"%{keyword}%"
            query = query.where(
                (User.username.ilike(pattern)) | (User.email.ilike(pattern))
            )

        # 启用状态过滤
        if is_active is not None:
            query = query.where(User.is_active == is_active)

        # 总数
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar() or 0

        # 分页
        query = query.order_by(User.id).offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        users = list(result.scalars().all())

        return users, total

    async def create(self, data: UserCreate) -> User:
        """创建用户"""
        # 检查用户名唯一
        existing = await self.get_by_username(data.username)
        if existing:
            raise ConflictException("用户名已存在")

        # 检查邮箱唯一
        existing = await self.get_by_email(data.email)
        if existing:
            raise ConflictException("邮箱已被注册")

        user = User(
            username=data.username,
            email=data.email,
            password_hash=get_password_hash(data.password),
            role=data.role,
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def update(self, user_id: int, data: UserUpdate) -> User:
        """更新用户"""
        user = await self.get_by_id(user_id)

        # 检查邮箱唯一
        if data.email and data.email != user.email:
            existing = await self.get_by_email(data.email)
            if existing:
                raise ConflictException("邮箱已被注册")
            user.email = data.email

        if data.role is not None:
            user.role = data.role
        if data.is_active is not None:
            user.is_active = data.is_active

        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def soft_delete(self, user_id: int) -> None:
        """软删除用户"""
        user = await self.get_by_id(user_id)
        user.deleted_at = datetime.now(timezone.utc)
        user.is_active = False
        await self.db.flush()

    async def update_last_login(self, user_id: int) -> None:
        """更新最后登录时间"""
        user = await self.get_by_id(user_id)
        user.last_login_at = datetime.now(timezone.utc)
        await self.db.flush()

    async def update_profile(self, user_id: int, data: ProfileUpdate) -> User:
        """更新个人资料"""
        user = await self.get_by_id(user_id)

        if data.email is not None and data.email != user.email:
            existing = await self.get_by_email(data.email)
            if existing:
                raise ConflictException("邮箱已被注册")
            user.email = data.email

        if data.github_id is not None:
            user.github_id = data.github_id
        if data.avatar_url is not None:
            user.avatar_url = data.avatar_url

        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def change_password(self, user_id: int, data: PasswordChange) -> None:
        """修改密码"""
        user = await self.get_by_id(user_id)

        if not verify_password(data.old_password, user.password_hash):
            raise AuthenticationException("当前密码错误")

        user.password_hash = get_password_hash(data.new_password)
        await self.db.flush()
