from fastapi import Depends
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.utils.token import verify_token, oauth2_scheme
from app.database import get_db
from app.models.user import User

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    payload = verify_token(token)
    if payload is None:
        raise credentials_exception

    user_id = payload.get("sub")

    # ✅✅✅ 打印调试信息
    print("🧪 Token payload:", payload)
    print("🧪 user_id:", user_id)

    if user_id is None:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()

    # ✅✅✅ 打印是否找到用户
    print("🧪 Found user:", user)

    if user is None:
        raise credentials_exception

    return user

print("✅ 正在加载 auth.py 中的 get_current_user 函数")