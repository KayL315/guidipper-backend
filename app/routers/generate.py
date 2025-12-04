import math
import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.schemas.preference import PreferenceRequest
from app.models.user import User
from app.models.bookmark import Bookmark
from openai import OpenAI  # 使用新版 openai SDK
from app.models.generated_route import GeneratedRoute

router = APIRouter()
client = OpenAI()  # 自动从环境变量读取 OPENAI_API_KEY

def distance_km(lon1, lat1, lon2, lat2):
    """
    Calculate distance between 2 point(Unit: km)
    Parameter Unit: degree
    Haversine formula
    """
    R = 6371.0

    # to radian
    rad_lon1 = math.radians(lon1)
    rad_lat1 = math.radians(lat1)
    rad_lon2 = math.radians(lon2)
    rad_lat2 = math.radians(lat2)

    # Haversine formula
    dlon = rad_lon2 - rad_lon1
    dlat = rad_lat2 - rad_lat1

    a = math.sin(dlat / 2) ** 2 + math.cos(rad_lat1) * math.cos(rad_lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))

    distance = R * c

    return round(distance, 2)

def distance_and_walk_time_str(lon1, lat1, lon2, lat2, walk_speed_kmh=5.0):
    """
    Example：
    - "distance 1.23 km, walk time 15 min - 22 min"
    - "distance 5.67 km, walk time > 68 min"
    """
    dist = distance_km(lon1, lat1, lon2, lat2)  # km

    t_min = dist / walk_speed_kmh * 60
    t_max = dist * math.sqrt(2) / walk_speed_kmh * 60
    t_min_rounded = int(round(t_min))
    t_max_rounded = int(round(t_max))

    if t_min_rounded > 60:
        return f"distance {dist} km, walk time > {t_min_rounded} min"
    else:
        return f"distance {dist} km, walk time {t_min_rounded} min - {t_max_rounded} min"

def generate_center_coordinate(center_landmark: str):
    prompt = """
Your task: extract a precise geo-coordinate from the user message. 
Respond with JSON only, containing:
{
  "place_name": "...",
  "longitude": xx.xxxx,
  "latitude": xx.xxxx
}
If coordinates are missing, use your best estimate.

Example: 

User message: "Eiffel Tower"
Your response: "{
    "place_name": "Eiffel Tower",
    "longitude": 2.2945,
    "latitude": 48.8584
}"
"""

    prompt += f"""
User message: "{center_landmark}"
Your response:
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,
            temperature=0.7,
        )
    except Exception as e:
        print("❌ OpenAI API 报错：", str(e))
        raise HTTPException(status_code=500, detail="OpenAI API 请求失败")
    
    result = response.choices[0].message.content
    result_obj = json.loads(result)
    coordinate = (result_obj["longitude"], result_obj["latitude"])
    print("✅ 解析出的坐标：", coordinate)
    return coordinate

def filter_bookmarks_by_center_landmark(bookmarks, center_lon, center_lat, max_distance_km=100.0):
    filtered = []
    for b in bookmarks:
        dist = distance_km(center_lon, center_lat, b.longitude, b.latitude)
        if dist <= max_distance_km:
            filtered.append(b)
    print(f"✅ 过滤后剩余 {len(filtered)} 个 bookmark（距离中心地标 {max_distance_km} km 内）")
    return filtered

@router.post("/generate-route")
def generate_route(
    preferences: PreferenceRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    print("✅ 收到 preferences：", preferences.dict())

    # 查询当前用户上传的 bookmark
    bookmarks = db.query(Bookmark).filter(Bookmark.user_id == current_user.id).all()
    if not bookmarks:
        raise HTTPException(status_code=400, detail="请先上传收藏夹 JSON 文件")

    # 生成中心地标坐标
    center_lon, center_lat = generate_center_coordinate(preferences.center_landmark)

    # 过滤无关的 bookmark
    bookmarks = filter_bookmarks_by_center_landmark(bookmarks, center_lon, center_lat, max_distance_km=50.0)

    # 整理 bookmarks 数据为字符串
    bookmark_list = [f"{b.title}, {b.address}" for b in bookmarks]
    bookmark_text = "\n".join(bookmark_list)

    # Calculate distance info between any 2 bookmarks (for debugging)
    distance_info = []
    for i in range(len(bookmarks)):
        for j in range(i + 1, len(bookmarks)):
            b1 = bookmarks[i]
            b2 = bookmarks[j]
            dist_info = distance_and_walk_time_str(
                b1.longitude, b1.latitude,
                b2.longitude, b2.latitude
            )
            distance_info.append(f"Distance between '{b1.title}' and '{b2.title}': {dist_info}")
    distance_info_text = "\n".join(distance_info)

    # ✅ 使用 snake_case 字段访问
    prompt = f"""
You are a smart travel planning AI assistant. Please generate a **one-day travel itinerary** for the user based on the following preferences:

1. Prioritize places from the user's uploaded bookmarks (restaurants, landmarks, cafes, etc.)
2. If no matching places are found in the bookmarks (e.g., preferred cuisine), recommend high-rated alternatives from Yelp
3. All places must fit within the user's time range and commute limitations. Each single trip should not exceed {preferences.max_commute_time} minutes.
4. The commute time between places should be calculated based on walking speed.

【User Preferences】
- Start Point: {preferences.center_landmark}
- Must-Visit Places: {', '.join(preferences.must_visit)}
- Start Time: {preferences.start_time}
- End Time: {preferences.end_time}
- Preferred Transportation Modes: {', '.join(preferences.transport_modes)}
- Allow Alcohol: {"Yes" if preferences.allow_alcohol else "No"}
- Preferred Cuisines: {', '.join(preferences.preferred_cuisine)}
- Max Single Commute Time: {preferences.max_commute_time} minutes

【User Bookmarks】 (prioritize selections from below):
{bookmark_text}

【Distance Information】
{distance_info_text}

Please output the itinerary in the following format:
09:00 - 10:00: Head to [Place Name], brief explanation (e.g., museum, restaurant, landmark, etc.)
10:00 - 11:30: Activity such as visit, dining, resting, etc.

Plan a full-day itinerary with reasonable timing for meals, sightseeing, and breaks. No need to include returning home.
"""
    print("🧾 Constructed Prompt:\n", prompt)

    try:
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,
            temperature=0.7,
        )
    except Exception as e:
        print("❌ OpenAI API 报错：", str(e))
        raise HTTPException(status_code=500, detail="OpenAI API 请求失败")
    
    result = response.choices[0].message.content
    print("🧠 OpenAI 完整返回：", response)
    print("📌 bookmark_text 内容：\n", bookmark_text)
    print("✅ OpenAI 返回的结果：\n", result)
    return {"generated_route": result}