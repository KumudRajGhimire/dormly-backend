from uuid import UUID
from pydantic import BaseModel

class CategoryResponse(BaseModel):
    id: UUID
    name: str 
    slug: str

    model_config = {
        "from_attributes": True
    }

class CategoryMiniResponse(BaseModel):
    id: UUID
    name: str 
    slug: str
    icon: str|None=None

    model_config = {
        "from_attributes": True
    }