from fastapi import HTTPException, status, Query
from sqlalchemy.orm import joinedload
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID 
from app.schemas.profile import UserProfileResponse
from app.schemas.listing import PaginatedListingResponse
from app.db.session import get_db
from app.models.users import User
from app.models.listings import Listing
from app.core.enums import ListingStatus
from sqlalchemy import desc

router = APIRouter(prefix="/users", tags = ["Users"])

@router.get("/{user_id}", response_model = UserProfileResponse)
def get_user_profile(user_id:UUID, db: Session = Depends(get_db)):
    user = (db.query(User).options(
        joinedload(User.campus),
        joinedload(User.hostel)
    )
    .filter(User.id == user_id)
    .first()
    )

    if user is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "User not found")

    return user

@router.get("/{user_id}/listings", response_model = PaginatedListingResponse)
def get_user_listings(user_id: UUID, page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "User not found"
        )
    
    query = (
        db.query(Listing)
        .options(
            joinedload(Listing.seller).joinedload(User.campus),
            joinedload(Listing.seller).joinedload(User.hostel),
            joinedload(Listing.category),
            joinedload(Listing.images),
        )
        .filter(Listing.seller_id == user_id)
        .order_by(desc(Listing.created_at))
    )
    total = query.count()
    items = query.offset((page-1)*page_size).limit(page_size).all()

    return{
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size
    }