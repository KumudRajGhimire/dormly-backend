from uuid import UUID
from pydantic import BaseModel


class HostelResponse(BaseModel):
    id: UUID
    name: str
    slug: str

    model_config = {
        "from_attributes": True
    }