"""PR审查路由"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.review import ReviewStatus
from app.schemas.common import ApiResponse, PaginatedData
from app.schemas.review import (
    IssueUpdate,
    ReviewIssue,
    ReviewListItem,
    ReviewResult,
    ReviewTrigger,
)
from app.services.review_service import ReviewService

router = APIRouter(prefix="/api/reviews", tags=["PR智能审查模块"])


@router.post("/trigger", response_model=ApiResponse, summary="手动触发审查")
async def trigger_review(
    data: ReviewTrigger,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """手动触发对指定PR的AI审查。"""
    service = ReviewService(db)
    result = await service.trigger_review(data.repo_id, data.pr_number, data.agents)
    return ApiResponse(code=200, message="审查已触发", data=result)


@router.get("/stats", response_model=ApiResponse, summary="审查统计")
async def get_review_stats(
    repo_id: int | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取审查统计数据。"""
    service = ReviewService(db)
    result = await service.get_stats(repo_id=repo_id, start_date=start_date, end_date=end_date)
    return ApiResponse(code=200, message="success", data=result)


@router.get("", response_model=ApiResponse[PaginatedData[ReviewListItem]], summary="获取审查记录列表")
async def get_review_list(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    repo_id: int | None = None,
    status: ReviewStatus | None = None,
    author: str | None = None,
    min_score: int | None = None,
    max_score: int | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """分页查询审查记录列表。"""
    service = ReviewService(db)
    data = await service.get_review_list(
        page=page, page_size=page_size,
        repo_id=repo_id, status=status, author=author,
        min_score=min_score, max_score=max_score,
    )
    return ApiResponse(code=200, message="success", data=data)


@router.get("/{pr_id}", response_model=ApiResponse[ReviewResult], summary="获取审查结果")
async def get_review_result(
    pr_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取指定PR的审查结果。"""
    service = ReviewService(db)
    result = await service.get_review_result(pr_id)
    return ApiResponse(code=200, message="success", data=result)


@router.patch("/issues/{issue_id}", response_model=ApiResponse[ReviewIssue], summary="更新审查问题状态")
async def update_issue(
    issue_id: int,
    data: IssueUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """人工确认或标记审查问题为误报。"""
    service = ReviewService(db)
    result = await service.update_issue(issue_id, data)
    return ApiResponse(code=200, message="问题状态已更新", data=result)
