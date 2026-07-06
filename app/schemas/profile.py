from uuid import UUID

from pydantic import BaseModel

from app.schemas.campus import CampusMiniResponse
from app.schemas.hostel import HostelMiniResponse
from app.core.enums import UserRole


class UserProfileResponse(BaseModel):
    id: UUID
    username: str
    name: str

    campus: CampusMiniResponse
    hostel: HostelMiniResponse | None = None
    role: UserRole

    model_config = {
        "from_attributes": True
    }