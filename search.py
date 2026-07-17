"""代码语义搜索路由"""

import asyncio

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.search import IndexRequest, IndexStatusResponse, SearchQuery, SearchResponse
from app.services.indexing_service import IndexingService
from app.services.search_service import SearchService

router = APIRouter(prefix="/api/search", tags=["代码搜索模块"])


@router.post("/code", response_model=ApiResponse[SearchResponse], summary="语义搜索代码")
async def search_code(
    data: SearchQuery,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """使用自然语言搜索代码片段。"""
    service = SearchService(db)
    result = await service.search(data)
    return ApiResponse(code=200, message="success", data=result)


@router.post("/index", response_model=ApiResponse, summary="触发仓库索引")
async def trigger_index(
    data: IndexRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """触发对指定仓库的代码索引（向量化）。异步执行。"""
    service = IndexingService(db)

    # 异步执行索引任务
    async def run_index():
        from app.core.database import AsyncSessionLocal
        async with AsyncSessionLocal() as new_db:
            index_service = IndexingService(new_db)
            try:
                result = await index_service.index_repository(data.repo_id, data.force_full)
                print(f"[Indexing] 任务完成: {result}")
            except Exception as e:
                print(f"[Indexing] 任务失败: {e}")

    asyncio.create_task(run_index())

    return ApiResponse(
        code=200,
        message="索引任务已提交",
        data={
            "repo_id": data.repo_id,
            "mode": "full" if data.force_full else "incremental",
        },
    )


@router.get("/index/{repo_id}", response_model=ApiResponse[IndexStatusResponse], summary="获取索引状态")
async def get_index_status(
    repo_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """查询仓库的代码索引状态。"""
    service = SearchService(db)
    result = await service.get_index_status(repo_id)
    return ApiResponse(code=200, message="success", data=result)
