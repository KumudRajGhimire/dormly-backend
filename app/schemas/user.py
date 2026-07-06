from app.schemas.hostel import HostelMiniResponse
from app.schemas.campus import CampusMiniResponse
from pydantic import BaseModel, EmailStr
from uuid import UUID


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    name: str
    password: str
    hostel_id: UUID | None = None


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    name: str


    model_config = {
        "from_attributes": True
    }

class SellerMiniResponse(BaseModel):
    id: UUID
    name: str
    username: str 

    campus: CampusMiniResponse
    hostel: HostelMiniResponse | None = None

    model_config = {
        "from_attributes": True
    }

class MessageResponse(BaseModel):
    message: str