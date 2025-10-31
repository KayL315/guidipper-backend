from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from .database import SessionLocal, engine, Base
from sqlalchemy import text
from app.models import user  
from app.routers import user
from app.routers import bookmark
from app.routers import generate 
from app.routers import generated_route
from dotenv import load_dotenv
import openai
import os
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
openai.api_key = os.getenv("OPENAI_API_KEY")

# 初始化数据库表结构
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 建数据库session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 测试fastapi是否工作
@app.get("/")
def read_root():
    return {"message": "FastAPI is working!"}
app.include_router(user.router)

# 测试数据库连接
@app.get("/test-db")
def test_db_connection(db: Session = Depends(get_db)):
    try:

        db.execute(text("SELECT 1"))
        return {"message": "Database connected successfully"}
    except Exception as e:
        return {"error": str(e)}

app.include_router(user.router)
app.include_router(bookmark.router)
app.include_router(generate.router)
app.include_router(generated_route.router)