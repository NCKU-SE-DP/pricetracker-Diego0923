from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from ..models import User
from ..schemas import UserAuthSchema
from ..database import get_db
from src.routers.authenticate import create_access_token, verify_password
from passlib.context import CryptContext
from ..dependence import authenticate_user_token
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/api/v1/users/register")
def register_user(user: UserAuthSchema, db: Session = Depends(get_db)):
    """create user"""
    try:
        hashed_password = password_context.hash(user.password)
        db_user = User(username=user.username, hashed_password=hashed_password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as e:
        logger.error(f"Error occurred while registering user: {user.username}. Error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.post("/api/v1/users/login")
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """login"""
    try:
        user = db.query(User).filter(User.username == form_data.username).first()
        if not user or not verify_password(form_data.password, user.hashed_password):
            logger.warning(f"Invalid login attempt for username: {form_data.username}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        access_token = create_access_token(
            data={"sub": str(user.username)}, expires_delta=timedelta(minutes=30)
        )
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        logger.error(f"Error occurred during login for username: {form_data.username}. Error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/api/v1/users/me", response_model=UserAuthSchema)
def read_users_me(user=Depends(authenticate_user_token)):
    try:
        return {"username": user.username, "id": user.id}
    except Exception as e:
        logger.error(f"Error occurred while retrieving user data for user ID: {user.id}. Error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")