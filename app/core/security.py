from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta, timezone
from app.core.config import JWT_SECRET, ALGORITHM, ACCESS_TOKEN_EXPIRY

pwd_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password:str, hashed_password:str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_jwt(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc)+timedelta(minutes=int(ACCESS_TOKEN_EXPIRY))

    to_encode["exp"] = expire
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)

    return encoded_jwt

def decode_jwt(token: str):
    return jwt.decode(token, key = JWT_SECRET, algorithms= [ALGORITHM])

