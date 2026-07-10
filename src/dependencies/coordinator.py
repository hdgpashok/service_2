from typing import Annotated

from fastapi import Depends

from src.dependencies.client import ClientDep
from src.services.saga_coordinator import SagaCoordinator


async def get_coordinator(client: ClientDep) -> SagaCoordinator:
    return SagaCoordinator(external_client=client)


CoordinatorDep = Annotated[SagaCoordinator, Depends(get_coordinator)]