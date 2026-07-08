from app.core.security import verify_password
import secrets, uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.security import hash_password
from app.models.refresh_token import RefreshToken

REFRESH_TOKEN_EXPIRY_DAYS = 30

def generate_refresh_token() -> tuple[uuid.UUID, str, str]:
    token_id = uuid.uuid4()
    secret = secrets.token_urlsafe(64)
    refresh_token = f"{token_id}.{secret}"
    return token_id,secret,refresh_token

def store_refresh_token(
    user_id,
    token_id,
    secret,
    db: Session,
):
    token = RefreshToken(
        user_id=user_id,
        token_id=token_id,
        token_hash=hash_password(secret),
        expires_at=datetime.now(timezone.utc)
        + timedelta(days=REFRESH_TOKEN_EXPIRY_DAYS),
    )

    db.add(token)
    
    return token

def verify_refresh_token(refresh_token: str, db: Session)->RefreshToken | None:
    try:
        token_id_str, secret = refresh_token.rsplit(".", 1)
        token_id = UUID(token_id_str)
    except (ValueError, AttributeError):
        return None

    token = db.query(RefreshToken).filter(
        RefreshToken.token_id == token_id,
        RefreshToken.revoked_at == None,
        RefreshToken.expires_at > datetime.now(timezone.utc)
    ).first()
    
    if token and verify_password(secret, token.token_hash):
        return token
    
    return None

def revoke_refresh_token(token: RefreshToken, db:Session):
    token.revoked_at = datetime.now(timezone.utc)
