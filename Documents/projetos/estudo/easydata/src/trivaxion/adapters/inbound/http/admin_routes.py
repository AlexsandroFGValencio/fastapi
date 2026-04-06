from typing import Annotated

from fastapi import APIRouter, Depends

from trivaxion.adapters.inbound.http.dependencies import (
    CurrentUser,
    DBSession,
    get_audit_repository,
    require_admin,
)
from trivaxion.application.ports.repositories import AuditRepository

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}


@router.get("/audit-events", dependencies=[Depends(require_admin)])
async def get_audit_events(
    current_user: CurrentUser,
    session: DBSession,
    audit_repository: Annotated[AuditRepository, Depends(get_audit_repository)],
    limit: int = 100,
) -> list[dict[str, object]]:
    if not current_user.organization_id:
        return []
    
    events = await audit_repository.find_by_organization(current_user.organization_id, limit=limit)
    
    return [
        {
            "id": str(event.id),
            "event_type": event.event_type.value,
            "user_id": str(event.user_id) if event.user_id else None,
            "resource_type": event.resource_type,
            "resource_id": str(event.resource_id) if event.resource_id else None,
            "timestamp": event.timestamp.isoformat(),
            "metadata": event.metadata,
        }
        for event in events
    ]


@router.get("/system-status", dependencies=[Depends(require_admin)])
async def get_system_status() -> dict[str, object]:
    return {
        "status": "operational",
        "version": "0.1.0",
        "environment": "production",
    }
