from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.campus import Campus
from app.schemas.campus import CampusResponse

router = APIRouter(
    prefix="/campuses",
    tags=["Campuses"]
)


@router.get("", response_model=list[CampusResponse])
def get_campuses(
    db: Session = Depends(get_db)
):
    return db.query(Campus).order_by(Campus.name).all()