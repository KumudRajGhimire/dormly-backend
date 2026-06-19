from app.models.users import User
from app.models.listings import Listing
from app.models.images import ListingImage
from app.models.category import Category
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import desc
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.listing import ListingCreate, ListingResponse, ListingUpdate, UploadUrlResponse, ListingImageCreate, PaginatedListingResponse
from app.auth.dependencies import get_current_user
from uuid import UUID
from app.services.s3 import generate_upload_url
from app.listings.service import get_owned_listing
from typing import Optional
from app.core.enums import ListingCondition, ListingStatus
from sqlalchemy import or_


router = APIRouter(prefix="/listings", tags=["Listings"])

@router.post("", response_model = ListingResponse)
def add_listing(payload: ListingCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    category = (db.query(Category).filter(Category.id == payload.category_id).first())
    
    if category is None:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Category not found"
        )
    
    listing = Listing(
        title = payload.title,
        description = payload.description,
        price = payload.price,
        seller_id = current_user.id,
        category_id = payload.category_id,
        condition = payload.condition,
    )

    db.add(listing)
    db.commit()
    db.refresh(listing)

    return listing

@router.get("", response_model=PaginatedListingResponse)
def get_listing(
    category_id: UUID | None = None,
    condition: ListingCondition | None = None,
    status: ListingStatus | None = ListingStatus.ACTIVE,
    search: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    sort: str = "newest",

    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),

    db: Session = Depends(get_db)
):
    query = db.query(Listing)

    if category_id:
        query = query.filter(
            Listing.category_id == category_id
        )

    if condition:
        query = query.filter(
            Listing.condition == condition
        )

    if status:
        query = query.filter(
            Listing.status == status
        )

    if search:
        query = query.filter(
            or_(
                Listing.title.ilike(f"%{search}%"),
                Listing.description.ilike(f"%{search}%")
            )
        )

    if min_price is not None:
        query = query.filter(
            Listing.price >= min_price
        )

    if max_price is not None:
        query = query.filter(
            Listing.price <= max_price
        )

    if sort == "newest":
        query = query.order_by(
            desc(Listing.created_at)
        )

    elif sort == "price_asc":
        query = query.order_by(
            Listing.price.asc()
        )

    elif sort == "price_desc":
        query = query.order_by(
            Listing.price.desc()
        )

    total = query.count()

    items = (
        query
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size
    }

@router.get("/{listing_id}", response_model = ListingResponse)
def get_listing_by_id(listing_id: UUID, db: Session = Depends(get_db)):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()

    if listing is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Item not found")

    return listing

@router.delete("/{listing_id}")
def delete_listing(listing_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    listing = get_owned_listing(listing_id, current_user, db)
    
    db.delete(listing)
    db.commit()
    return {
        "message": "Item deleted successfully"
    }

@router.patch("/{listing_id}", response_model = ListingResponse)
def update_listing(listing_id: UUID, payload: ListingUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    listing = get_owned_listing(listing_id, current_user, db)
    
    if payload.title is not None:
        listing.title = payload.title
    if payload.description is not None:
        listing.description = payload.description
    if payload.price is not None:
        listing.price = payload.price
    if payload.condition is not None:
        listing.condition = payload.condition
    

    db.commit()
    db.refresh(listing)
    return listing 

@router.post("/{listing_id}/upload-url", response_model = UploadUrlResponse)
def get_upload_url(listing_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    listing = get_owned_listing(listing_id, current_user, db)

    return generate_upload_url(str(listing.id), "image/jpeg")

@router.post("/{listing_id}/images")
def attach_image(listing_id: UUID, payload: ListingImageCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    listing = get_owned_listing(listing_id, current_user, db)
    
    image = ListingImage(
        listing_id = listing.id,
        file_key = payload.file_key
    )

    db.add(image)
    db.commit()
    db.refresh(image)

    return{
        "message": "Image attached successfully"
    }