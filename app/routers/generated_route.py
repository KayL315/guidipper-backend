# routers/generated_route.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models
from app.models.generated_route import GeneratedRoute
from app.schemas.generated_route import GeneratedRouteCreate, GeneratedRouteResponse
from app.models.user import User
from app.dependencies.auth import get_current_user

router = APIRouter()

#save generated route
@router.post("/save-route", response_model=GeneratedRouteResponse)
def save_generated_route(
    route_data: GeneratedRouteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # ✅ 自动识别当前用户
):
    new_route = GeneratedRoute(
        user_id=current_user.id,  # ✅ 使用 token 提取的用户 ID
        route_text=route_data.route_text,
    )
    db.add(new_route)
    db.commit()
    db.refresh(new_route)
    return new_route

#get generated routes for a user
@router.get("/routes/{user_id}", response_model=List[GeneratedRouteResponse])
def get_routes_by_user(user_id: int, db: Session = Depends(get_db)):
    routes = db.query(models.generated_route.GeneratedRoute).filter(models.generated_route.GeneratedRoute.user_id == user_id).all()
    if not routes:
        raise HTTPException(status_code=404, detail="No routes found for this user.")
    return routes