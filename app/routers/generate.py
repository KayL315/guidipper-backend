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
你是一个聪明的旅游规划 AI 助手，请为用户制定一日旅游路线，满足以下要求：

1. 优先使用用户上传的收藏夹地点（餐厅、景点、咖啡店等）
2. 如果收藏夹中没有符合用户偏好的地点（如：偏好菜系的餐厅），请从 Yelp 上推荐评分高的替代选项
3. 所有地点需在出发时间和结束时间范围内，交通方式合理，单次通勤不超过 {preferences.max_commute_time} 分钟

【用户偏好】
- 中心地标：{preferences.center_landmark}
- 必去景点：{', '.join(preferences.must_visit)}
- 出发时间：{preferences.start_time}
- 结束时间：{preferences.end_time}
- 可接受交通方式：{', '.join(preferences.transport_modes)}
- 是否允许饮酒：{"是" if preferences.allow_alcohol else "否"}
- 偏好菜系：{', '.join(preferences.preferred_cuisine)}
- 最长单次通勤时间：{preferences.max_commute_time} 分钟

【用户收藏夹】（优先从以下地点中选择）：
{bookmark_text}

请输出格式如下：
09:00 - 10:00: 出发并前往 [地点名称]，说明原因（如：博物馆、餐厅、景点等）
10:00 - 11:30: 游览或用餐等活动安排

请规划完整的一日行程，并在适当时段安排用餐、休息、游玩、返回等安排。
"""
    print("🧾 构造的 Prompt 内容：\n", prompt)

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