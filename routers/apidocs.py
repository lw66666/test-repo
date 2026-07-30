"""API文档生成路由"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.api_doc import ApiDocResult, DocGenRequest
from app.schemas.common import ApiResponse
from app.services.doc_gen_service import DocGenService

router = APIRouter(prefix="/api/docs", tags=["API文档生成模块"])


@router.post("/generate", response_model=ApiResponse[ApiDocResult], summary="生成API文档")
async def generate_doc(
    data: DocGenRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """从代码中提取接口定义，生成 API 文档。"""
    service = DocGenService(db)
    result = await service.generate(data, current_user.id)
    return ApiResponse(code=200, message="文档生成成功", data=result)


@router.get("", response_model=ApiResponse, summary="获取文档列表")
async def get_doc_list(
    repo_id: int | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取已生成的 API 文档列表。"""
    service = DocGenService(db)
    result = await service.get_list(repo_id=repo_id, page=page, page_size=page_size)
    return ApiResponse(code=200, message="success", data=result)


@router.get("/{doc_id}", response_model=ApiResponse[ApiDocResult], summary="获取文档详情")
async def get_doc_detail(
    doc_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取指定文档的完整内容。"""
    service = DocGenService(db)
    result = await service.get_detail(doc_id)
    return ApiResponse(code=200, message="success", data=result)


@router.delete("/{doc_id}", response_model=ApiResponse, summary="删除文档")
async def delete_doc(
    doc_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除指定的 API 文档。"""
    service = DocGenService(db)
    await service.delete(doc_id)
    return ApiResponse(code=200, message="文档已删除", data=None)
