"""单元测试生成路由"""

import asyncio

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.test_gen import TestGenRequest, TestGenResult
from app.services.test_gen_service import TestGenService

router = APIRouter(prefix="/api/tests", tags=["测试生成模块"])


@router.post("/generate", response_model=ApiResponse, summary="生成单元测试")
async def generate_test(
    data: TestGenRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """为指定函数生成 pytest 单元测试用例。异步执行。"""
    service = TestGenService(db)

    # 先创建记录，获取 ID
    record = await service.create_pending_record(data, current_user.id)

    # 异步执行生成任务
    async def run_generate():
        from app.core.database import AsyncSessionLocal
        async with AsyncSessionLocal() as new_db:
            gen_service = TestGenService(new_db)
            try:
                await gen_service.execute_generate(record.id, data)
            except Exception as e:
                print(f"[TestGen] 生成失败: {e}")
                await gen_service.mark_failed(record.id, str(e))

    asyncio.create_task(run_generate())

    return ApiResponse(
        code=200,
        message="测试生成任务已提交",
        data={"id": record.id, "status": "generating"},
    )


@router.get("", response_model=ApiResponse, summary="获取测试生成历史")
async def get_test_history(
    repo_id: int | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取测试生成记录列表。"""
    service = TestGenService(db)
    result = await service.get_history(repo_id=repo_id, page=page, page_size=page_size)
    return ApiResponse(code=200, message="success", data=result)


@router.get("/{test_id}", response_model=ApiResponse[TestGenResult], summary="获取测试生成详情")
async def get_test_detail(
    test_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取指定测试生成记录的完整内容。"""
    service = TestGenService(db)
    result = await service.get_detail(test_id)
    return ApiResponse(code=200, message="success", data=result)


