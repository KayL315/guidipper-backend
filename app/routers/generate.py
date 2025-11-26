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

    # 整理 bookmarks 数据为字符串
    bookmark_list = [f"{b.title}, {b.address}" for b in bookmarks]
    bookmark_text = "\n".join(bookmark_list)

    # ✅ 使用 snake_case 字段访问
    prompt = f"""
You are a smart travel planning AI assistant. Please generate a **one-day travel itinerary** for the user based on the following preferences:

1. Prioritize places from the user's uploaded bookmarks (restaurants, landmarks, cafes, etc.)
2. If no matching places are found in the bookmarks (e.g., preferred cuisine), recommend high-rated alternatives from Yelp
3. All places must fit within the user's time range and commute limitations. Each single trip should not exceed {preferences.max_commute_time} minutes.

【User Preferences】
- Central Landmark: {preferences.center_landmark}
- Must-Visit Places: {', '.join(preferences.must_visit)}
- Start Time: {preferences.start_time}
- End Time: {preferences.end_time}
- Preferred Transportation Modes: {', '.join(preferences.transport_modes)}
- Allow Alcohol: {"Yes" if preferences.allow_alcohol else "No"}
- Preferred Cuisines: {', '.join(preferences.preferred_cuisine)}
- Max Single Commute Time: {preferences.max_commute_time} minutes

【User Bookmarks】 (prioritize selections from below):
{bookmark_text}

Please output the itinerary in the following format:
09:00 - 10:00: Head to [Place Name], brief explanation (e.g., museum, restaurant, landmark, etc.)
10:00 - 11:30: Activity such as visit, dining, resting, etc.

Plan a full-day itinerary with reasonable timing for meals, sightseeing, and breaks. No need to include returning home.
"""
    print("🧾 Constructed Prompt:\n", prompt)

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
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