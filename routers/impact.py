"""代码变更影响分析路由"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.impact import ImpactAnalyzeRequest, ImpactResult
from app.services.impact_service import ImpactService

router = APIRouter(prefix="/api/impact", tags=["代码变更影响分析模块"])


@router.post("/analyze", response_model=ApiResponse[ImpactResult], summary="分析变更影响")
async def analyze_impact(
    data: ImpactAnalyzeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """分析指定文件变更的影响范围。"""
    service = ImpactService(db)
    result = await service.analyze(data, current_user.id)
    return ApiResponse(code=200, message="分析完成", data=result)


@router.get("", response_model=ApiResponse, summary="获取分析历史")
async def get_analysis_list(
    repo_id: int | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取影响分析历史记录。"""
    service = ImpactService(db)
    result = await service.get_list(repo_id=repo_id, page=page, page_size=page_size)
    return ApiResponse(code=200, message="success", data=result)


@router.get("/{analysis_id}", response_model=ApiResponse[ImpactResult], summary="获取分析详情")
async def get_analysis_detail(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取指定影响分析的完整结果，包含依赖图数据。"""
    service = ImpactService(db)
    result = await service.get_detail(analysis_id)
    return ApiResponse(code=200, message="success", data=result)
