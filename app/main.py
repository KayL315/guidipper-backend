from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from .database import SessionLocal, engine, Base
from sqlalchemy import text
from app.routers import user
from app.routers import bookmark
from app.routers import generate
from app.routers import generated_route
from app.routers import chat
from dotenv import load_dotenv
import openai
import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# 加载环境变量
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# 初始化数据库
Base.metadata.create_all(bind=engine)

# 初始化 FastAPI
app = FastAPI()

# ⭐⭐⭐ 正确的 CORS 中间件 —— 必须放在 include_router **前面**
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],         # ←← 完全放开
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据库 Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 测试
@app.get("/")
def read_root():
    return {"message": "FastAPI is working!"}

# ⭐⭐⭐ 只 include 一次（你之前 include 了两次！）
app.include_router(user.router)
app.include_router(bookmark.router)
app.include_router(generate.router)
app.include_router(generated_route.router)
app.include_router(chat.router, prefix="/chat", tags=["chat"])

# 测试数据库
@app.get("/test-db")
def test_db_connection(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"message": "Database connected successfully"}
    except Exception as e:
        return {"error": str(e)}

app.mount("/static", StaticFiles(directory="app/static"), name="static")
