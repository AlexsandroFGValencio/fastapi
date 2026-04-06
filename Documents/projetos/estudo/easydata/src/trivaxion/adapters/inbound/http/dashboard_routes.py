from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta

from trivaxion.adapters.inbound.http.dependencies import CurrentUser, DBSession
from trivaxion.infrastructure.db.models import AnalysisModel

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
async def get_dashboard_summary(
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    """Get dashboard summary statistics"""
    
    # Total analyses
    total_result = await db.execute(
        select(func.count(AnalysisModel.id))
        .where(AnalysisModel.organization_id == current_user.organization_id.value)
    )
    total_analyses = total_result.scalar() or 0
    
    # Analyses this month
    first_day_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_result = await db.execute(
        select(func.count(AnalysisModel.id))
        .where(
            AnalysisModel.organization_id == current_user.organization_id.value,
            AnalysisModel.created_at >= first_day_of_month
        )
    )
    analyses_this_month = month_result.scalar() or 0
    
    # Processing analyses
    processing_result = await db.execute(
        select(func.count(AnalysisModel.id))
        .where(
            AnalysisModel.organization_id == current_user.organization_id.value,
            AnalysisModel.status == 'PROCESSING'
        )
    )
    processing = processing_result.scalar() or 0
    
    # Completed today
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_result = await db.execute(
        select(func.count(AnalysisModel.id))
        .where(
            AnalysisModel.organization_id == current_user.organization_id.value,
            AnalysisModel.status == 'COMPLETED',
            AnalysisModel.completed_at >= today_start
        )
    )
    completed_today = today_result.scalar() or 0
    
    return {
        "total_analyses": total_analyses,
        "analyses_this_month": analyses_this_month,
        "processing": processing,
        "completed_today": completed_today,
    }
