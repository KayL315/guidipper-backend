from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserResponse, UserLogin, TokenResponse
from app.models.user import User
from app.database import get_db
from app.utils.hash import hash_password, verify_password
from app.utils.token import create_access_token
from app import schemas
from fastapi import UploadFile, File, Form
import uuid
import shutil
from fastapi import UploadFile, File, Form

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

# ⭐ NEW: Get all generated routes for current user
@router.get("/routes")
def get_user_routes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    routes = (
        db.query(User)
        .filter(User.id == current_user.id)
        .first()
        .generated_routes
    )

    # 返回 route_text 字段
    return {
        "routes": [r.route_text for r in routes] if routes else []
    }

@router.put("/update-username")
def update_username(
    username: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    current_user.username = username
    db.commit()
    db.refresh(current_user)
    return {"message": "Username updated", "username": current_user.username}

@router.post("/upload-avatar")
def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ext = file.filename.split(".")[-1]
    new_filename = f"{uuid.uuid4()}.{ext}"
    file_path = f"app/static/avatars/{new_filename}"

    # 保存上传的图片
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 存储头像 URL
    avatar_url = f"/static/avatars/{new_filename}"
    current_user.avatar_url = avatar_url

    db.commit()
    db.refresh(current_user)

    return {"avatar_url": avatar_url}
