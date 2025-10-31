from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, status

# ✅ 保留一个统一密钥，登录与验证必须一致
SECRET_KEY = "a_secret_key_for_token_generation"  # ✅ 用 jwt.py 中的版本
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day

# ✅ 用于 FastAPI 的依赖注入，配合 Depends 使用
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# ✅ 创建 token（用于 login）
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# ✅ 验证 token（用于 get_current_user）
def verify_token(token: str):
    try:
        print("🐛 Raw token:", token)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print("📦 Decoded payload:", payload)

        if "sub" not in payload:
            print("❌ 'sub' not in payload")
            return None

        return payload
    except JWTError as e:
        print("❌ JWTError:", e)
        return None

# ✅ 自定义 401 错误
def credentials_exception():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )