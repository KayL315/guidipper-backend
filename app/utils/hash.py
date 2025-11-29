from passlib.context import CryptContext

# 使用 pbkdf2_sha256（不会出现 72 bytes 限制问题）
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto",
)

# 加密密码
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# 验证密码
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

