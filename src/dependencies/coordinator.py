from typing import Annotated

from fastapi import Depends

from src.services.saga_coordinator import SagaCoordinator


async def get_coordinator() -> SagaCoordinator:
    return SagaCoordinator()


CoordinatorDep = Annotated[SagaCoordinator, Depends(get_coordinator)]