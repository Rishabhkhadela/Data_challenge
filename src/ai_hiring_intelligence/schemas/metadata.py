from pydantic import BaseModel


class ServiceMetadata(BaseModel):
    name: str
    environment: str
    version: str

