from uuid import UUID
from pydantic import BaseModel 
from datetime import datetime
from app.core.enums import ListingCondition, ListingStatus

class ListingCreate(BaseModel):
    title: str
    description: str 
    price: int
    category_id: UUID 
    condition: ListingCondition

class ListingImageResponse(BaseModel):
    id: UUID
    file_key:str

    model_config = {
        "from_attributes": True
    }

class ListingResponse(BaseModel):
    id: UUID 
    title: str 
    description: str 
    price: int 
    seller_id: UUID 
    category_id: UUID
    condition: ListingCondition
    status: ListingStatus

    created_at: datetime
    updated_at: datetime

    images: list[ListingImageResponse]

    model_config = {
        "from_attributes": True 
    }

class PaginatedListingResponse(BaseModel):
    items: list[ListingResponse]
    total: int
    page: int
    page_size: int
    
class ListingUpdate(BaseModel):
    title : str|None = None
    description : str|None = None 
    price : int|None = None
    condition : ListingCondition|None = None

class UploadUrlResponse(BaseModel):
    upload_url: str 
    file_key: str 

class ListingImageCreate(BaseModel):
    file_key: str

