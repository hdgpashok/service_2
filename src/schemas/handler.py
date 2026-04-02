from pydantic import BaseModel


class Handler(BaseModel):
    detail: str