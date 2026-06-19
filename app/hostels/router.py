from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.hostel import Hostel
from app.schemas.hostel import HostelResponse

router = APIRouter(
    prefix="/hostels",
    tags=["Hostels"]
)


@router.get(
    "/campus/{campus_id}",
    response_model=list[HostelResponse]
)
def get_hostels_by_campus(
    campus_id: UUID,
    db: Session = Depends(get_db)
):
    return (
        db.query(Hostel)
        .filter(Hostel.campus_id == campus_id)
        .order_by(Hostel.name)
        .all()
    )