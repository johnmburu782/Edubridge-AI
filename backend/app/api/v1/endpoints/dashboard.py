from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.models.dashboard import DashboardSnapshot
from app.schemas.dashboard import DashboardResponse

router = APIRouter()


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    session: AsyncSession = Depends(get_db_session),
) -> DashboardResponse:
    result = await session.execute(
        select(DashboardSnapshot).where(DashboardSnapshot.id == 1)
    )
    snapshot = result.scalar_one_or_none()
    if snapshot is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Dashboard data is not initialized. Run the database migrations.",
        )

    return DashboardResponse(
        **snapshot.content,
        updated_at=snapshot.updated_at.isoformat(),
    )
