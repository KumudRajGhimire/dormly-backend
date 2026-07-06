from app.core.enums import ListingStatus, UserRole
from fastapi import HTTPException, status
from app.models.listings import Listing

def get_owned_listing(listing_id, current_user, db):
    listing = db.get(Listing, listing_id)
    if listing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found"
        )
    if listing.seller_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this listing"
        )
    return listing



def update_listing_status(
    listing_id,
    new_status: ListingStatus,
    current_user,
    db,
):
    listing = get_owned_listing(
        listing_id,
        current_user,
        db,
    )

    listing.status = new_status

    db.commit()
    db.refresh(listing)

    return listing