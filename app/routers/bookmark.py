# app/routers/bookmark.py
import json
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.bookmark import Bookmark
from app.models.user import User
from app import schemas
from typing import List

router = APIRouter()

@router.post("/upload-bookmarks")
async def upload_bookmarks(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    content = await file.read()
    try:
        raw_data = json.loads(content)
        features = raw_data.get("features", [])
        print("🛠️ 上传的 features 内容如下：")
        for f in features[:3]:  # 只打印前几个，防止太长
            print(json.dumps(f, indent=2)) 
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON format")

    # 删除用户旧数据
    db.query(Bookmark).filter(Bookmark.user_id == current_user.id).delete()

    # 插入新数据
    skipped = 0
    added = 0

    for item in features:
        try:
            properties = item.get("properties", {})
            location_info = properties.get("location", {})
            geometry = item.get("geometry", {})
            coordinates = geometry.get("coordinates", [None, None])

            title = location_info.get("name")
            address = location_info.get("address")
            longitude, latitude = coordinates  # 注意顺序是 [lon, lat]
            maps_url = properties.get("google_maps_url", "")

            if not title or not address or latitude is None or longitude is None or latitude == 0 or longitude == 0:
                print("⚠️ Skipping invalid bookmark:", title, address, latitude, longitude)
                skipped += 1
                continue

            print(f"✅ Parsed bookmark: {title} | {address} | ({latitude}, {longitude})")

            bookmark = Bookmark(
                user_id=current_user.id,
                title=title,
                address=address,
                latitude=latitude,
                longitude=longitude,
                category="",
                google_maps_url=maps_url
            )
            db.add(bookmark)
            added += 1
        except Exception as e:
            print("❌ Error parsing bookmark:", e)
            skipped += 1

    db.commit()

    return {
        "message": f"📥 Bookmarks uploaded successfully. Added: {added}, Skipped: {skipped}"
    }
#get uploaded bookmarks for current user
@router.get("/bookmarks", response_model=List[schemas.BookmarkResponse])
def get_user_bookmarks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    bookmarks = db.query(Bookmark).filter(Bookmark.user_id == current_user.id).all()
    return bookmarks

#check if bookmarks exist for a user
@router.get("/check-bookmarks/{user_id}")
def check_user_bookmarks(user_id: int, db: Session = Depends(get_db)):
    print(f"🧪 Checking bookmarks for user: {user_id}")
    bookmarks = db.query(Bookmark).filter(Bookmark.user_id == user_id).all()
    print(f"📊 Found {len(bookmarks)} bookmarks")
    return {"exists": len(bookmarks) > 0}