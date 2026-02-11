from src.schemas.healthcheck import HealthCheck

from fastapi import APIRouter

router = APIRouter()


@router.get('/healthcheck')
async def healthcheck() -> HealthCheck:
    return HealthCheck(
        status='ok'
    )
