from fastapi import APIRouter
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.auth.dependencies import get_current_user
from app.db.session import get_db
from app.models.users import User
from app.models.listings import Listing
from app.models.wishlist import Wishlist
from app.schemas.listing import ListingResponse

router = APIRouter(prefix="/wishlist", tags=["Wishlist"])

@router.post("/{listing_id}")
def add_to_wishlist(listing_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    listing = db.get(Listing, listing_id)
    if listing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")

    existing = (
        db.query(Wishlist)
        .filter(
            Wishlist.user_id == current_user.id,
            Wishlist.listing_id == listing_id
        )
        .first()
    )
    if existing:
        return{
            "message":"Already in wishlist"
        }

    wishlist = Wishlist(
        user_id = current_user.id,
        listing_id = listing_id
    )

    db.add(wishlist)
    db.commit()

    return {
        "message": "Added to wishlist"
    }

@router.delete("/{listing_id}")
def remove_from_wishlist(listing_id:UUID, current_user:User = Depends(get_current_user), db:Session = Depends(get_db)):
    wishlist = (
        db.query(Wishlist)
        .filter(
            Wishlist.user_id == current_user.id,
            Wishlist.listing_id == listing_id
        )
        .first()
    )

    if wishlist is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not in wishlist")
    
    db.delete(wishlist)
    db.commit()

    return {
        "message": "Removed from wishlist"
    }

@router.get("", response_model = list[ListingResponse])
def get_wishlist(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    wishlist = (
        db.query(Wishlist)
        .options(
            joinedload(Wishlist.listing)
            .joinedload(Listing.seller)
            .joinedload(User.campus),

            joinedload(Wishlist.listing)
            .joinedload(Listing.seller)
            .joinedload(User.hostel),

            joinedload(Wishlist.listing)
            .joinedload(Listing.category),

            joinedload(Wishlist.listing)
            .joinedload(Listing.images)
        )
        .filter(
            Wishlist.user_id == current_user.id
        )
        .all()
    )

    return {
        item.listing 
        for item in wishlist
    }