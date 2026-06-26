from uuid import UUID

from pydantic import BaseModel

from app.schemas.campus import CampusMiniResponse
from app.schemas.hostel import HostelMiniResponse


class UserProfileResponse(BaseModel):
    id: UUID
    username: str
    name: str

    campus: CampusMiniResponse
    hostel: HostelMiniResponse | None = None

    model_config = {
        "from_attributes": True
    }