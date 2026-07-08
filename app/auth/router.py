from datetime import timezone
from datetime import datetime
from app.schemas.auth import LogoutRequest
from app.auth.refresh_service import revoke_refresh_token
from app.auth.refresh_service import verify_refresh_token
from app.schemas.auth import RefreshTokenRequest
from app.models.users import User
from app.models.campus import Campus
from app.models.hostel import Hostel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user import UserCreate, MessageResponse
from app.schemas.auth import LoginCreate, LoginResponse, VerifyEmailRequest, ResendOTPRequest, ForgotPasswordRequest, ResetPasswordRequest
from app.core.security import hash_password, verify_password, create_jwt
from app.auth.dependencies import get_current_user
from app.auth.service import get_campus_from_email
from app.otp.service import create_otp
from app.core.enums import OTPPurpose
from app.otp.service import verify_otp
from app.auth.refresh_service import generate_refresh_token, store_refresh_token
from app.models.refresh_token import RefreshToken


router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=MessageResponse)
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

    campus = get_campus_from_email(payload.email, db)

    if campus is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The campus with your email domain is yet to be registered to Dormly."
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

        if hostel is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hostel not found or does not belong to this campus"
            )


    hashed_pass = hash_password(payload.password)
    user = User(
        username=payload.username,
        email=payload.email,
        name=payload.name,
        hashed_password=hashed_pass,
        campus_id=campus.id,
        hostel_id=payload.hostel_id
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    create_otp(email= user.email, purpose= OTPPurpose.EMAIL_VERIFICATION, db= db)
    return {
        "message":"Registration successful. Verify your email."
    }

@router.post("/login", response_model = LoginResponse)
def login_user(payload: LoginCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "User does not exist")
    
    if not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Incorrect password")

    if not user.email_verified:
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = "Please verify your email first")

    access_token = create_jwt({
        "sub": str(user.id)
    })

    token_id, secret, refresh_token = generate_refresh_token()

    store_refresh_token(user.id, token_id, secret, db)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/logout")
def logout(payload: LogoutRequest, db: Session = Depends(get_db)):
    token = verify_refresh_token(payload.refresh_token, db)
    if token:
        revoke_refresh_token(token, db)
    db.commit()

    return{
        "message": "Logged out successfully"
    }

    

@router.post("/verify-email")
def verify_email(payload: VerifyEmailRequest, db: Session = Depends(get_db)):
    user = (
        db.query(User)
        .filter(User.email == payload.email)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user.email_verified:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Email already verified")

    valid = verify_otp(
        email=payload.email,
        otp=payload.otp,
        purpose=OTPPurpose.EMAIL_VERIFICATION,
        db=db,
    )

    if not valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP",
        )

    user.email_verified = True
    db.commit()
    return {"message": "Email verified successfully"}

@router.post("/resend-otp")
def resend_otp(payload: ResendOTPRequest, db: Session = Depends(get_db)):
    user = (
        db.query(User)
        .filter(User.email == payload.email)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user.email_verified:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Email already verified")

    create_otp(
        email=payload.email,
        purpose=OTPPurpose.EMAIL_VERIFICATION,
        db=db,
    )

    return {"message": "OTP sent successfully"}

@router.post("/forget-password")
def forget_password(payload: ForgotPasswordRequest, db:Session=Depends(get_db)):
    user = (
    db.query(User)
    .filter(User.email == payload.email)
    .first()
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    create_otp(
        email=payload.email,
        purpose=OTPPurpose.PASSWORD_RESET,
        db=db,
    )

    return {"message": "OTP sent successfully"}

@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = (
        db.query(User)
        .filter(User.email == payload.email)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    valid = verify_otp(
        email=payload.email,
        otp=payload.otp,
        purpose=OTPPurpose.PASSWORD_RESET,
        db=db,
    )

    if not valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP",
        )

    user.hashed_password = hash_password(payload.new_password)

    (
        db.query(RefreshToken)
        .filter(
            RefreshToken.user_id == user.id,
            RefreshToken.revoked_at.is_(None)
        ).update(
            {
                RefreshToken.revoked_at: datetime.now(timezone.utc)
            },
            synchronize_session=False
        )
    )

    db.commit()

    return {"message": "Password reset successfully"}


@router.post("/refresh", response_model = LoginResponse)
def refresh_access_token(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    token = verify_refresh_token(payload.refresh_token, db)

    if token is None:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid refresh token"
        )
    
    user = db.get(User, token.user_id)

    if user is None:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "User not found"
        )

    access_token = create_jwt(
        {
            "sub": str(user.id)
        }
    )

    token_id, secret, refresh_token = generate_refresh_token()
    new_token = store_refresh_token(user.id, token_id, secret, db)

    revoke_refresh_token(token, db)

    db.commit()
    db.refresh(new_token)

    return{
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }