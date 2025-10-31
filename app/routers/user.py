from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserResponse, UserLogin, TokenResponse
from app.models.user import User
from app.database import get_db
from app.utils.hash import hash_password, verify_password
from app.utils.token import create_access_token
from app import schemas

router = APIRouter()

# Register
@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

# Login
@router.post("/login", response_model=TokenResponse)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid email or password")
    
    access_token = create_access_token(data={"sub": str(user.id)})
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": {
        "id": user.id,
        "email": user.email,
        "username": user.username,
    }}

# Get current user info
from app.dependencies.auth import get_current_user
@router.get("/me", response_model=schemas.UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user