from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from src.config import JWT_SECRET_KEY, DEFAULT_TOKEN_EXPIRE_MINUTES

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    驗證用戶輸入的密碼是否與儲存的加密密碼匹配
    """
    return password_context.verify(plain_password, hashed_password)

def create_access_token(data, expires_delta=None):
    """create access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=DEFAULT_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    print(to_encode)
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm="HS256")
    return encoded_jwt