from app.models.users import User
from app.models.campus import Campus
from app.models.hostel import Hostel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user import UserCreate, UserResponse
from app.schemas.auth import LoginCreate, LoginResponse
from app.core.security import hash_password, verify_password, create_jwt
from app.auth.dependencies import get_current_user



router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse)
def register_user(payload: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise HTTPException(status_code = status.HTTP_409_CONFLICT, detail = "User with this email already exists")

    existing_username = (
        db.query(User)
        .filter(User.username == payload.username)
        .first()
    )

    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists"
        )

    campus = (
        db.query(Campus)
        .filter(Campus.id == payload.campus_id)
        .first()
    )

    if not campus:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campus not found"
        )

    hostel = None
    if payload.hostel_id is not None:
        hostel = (
            db.query(Hostel)
            .filter(
                Hostel.id == payload.hostel_id,
                Hostel.campus_id == campus.id
            )
            .first()
        )

        if not hostel:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Hostel not found or does not belong to this campus"
            )

    if payload.hostel_id:
        hostel = (
            db.query(Hostel)
            .filter(Hostel.id == payload.hostel_id)
            .first()
        )

        if hostel.campus_id != payload.campus_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Hostel does not belong to selected campus"
            )
    
    hashed_pass = hash_password(payload.password)
    user = User(
        username=payload.username,
        email=payload.email,
        name=payload.name,
        hashed_password=hashed_pass,
        campus_id=payload.campus_id,
        hostel_id=payload.hostel_id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print("Before return: ", user)
    return user

@router.post("/login", response_model = LoginResponse)
def login_user(payload: LoginCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "User does not exist")
    
    if not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Incorrect password")

    token = create_jwt({
        "sub": str(user.id)
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }

@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return{
        "id": current_user.id,
        "name": current_user.name
    }