from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.chat_session import ChatSession
from app.models.chat_message import ChatMessage
from app.models.generated_route import GeneratedRoute
from app.schemas.chat_session import ChatSessionCreate, ChatSessionResponse, ChatSessionWithRoute
from app.schemas.chat_message import ChatMessageCreate, ChatMessageResponse
from app.schemas.ai_response import AIResponse
from app.utils.diff_utils import apply_diff
from app.dependencies.auth import get_current_user
from openai import OpenAI
import json

router = APIRouter()
client = OpenAI()

@router.post("/sessions", response_model=ChatSessionResponse)
def create_chat_session(
    session_data: ChatSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    generated_route = db.query(GeneratedRoute).filter(
        GeneratedRoute.id == session_data.generated_route_id,
        GeneratedRoute.user_id == current_user.id
    ).first()

    if not generated_route:
        raise HTTPException(status_code=404, detail="Generated route not found or does not belong to user")

    new_session = ChatSession(
        user_id=current_user.id,
        generated_route_id=session_data.generated_route_id
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session

@router.get("/sessions", response_model=List[ChatSessionWithRoute])
def get_user_chat_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sessions = db.query(ChatSession).filter(
        ChatSession.user_id == current_user.id
    ).order_by(ChatSession.updated_at.desc()).all()

    result = []
    for session in sessions:
        route = db.query(GeneratedRoute).filter(
            GeneratedRoute.id == session.generated_route_id
        ).first()
        session_dict = {
            "id": session.id,
            "user_id": session.user_id,
            "generated_route_id": session.generated_route_id,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
            "route_text": route.route_text if route else None
        }
        result.append(session_dict)

    return result

@router.get("/sessions/{session_id}", response_model=ChatSessionWithRoute)
def get_chat_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    route = db.query(GeneratedRoute).filter(
        GeneratedRoute.id == session.generated_route_id
    ).first()

    return {
        "id": session.id,
        "user_id": session.user_id,
        "generated_route_id": session.generated_route_id,
        "created_at": session.created_at,
        "updated_at": session.updated_at,
        "route_text": route.route_text if route else None
    }

@router.post("/sessions/{session_id}/messages", response_model=ChatMessageResponse)
async def send_chat_message(
    session_id: int,
    message_data: ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    route = db.query(GeneratedRoute).filter(
        GeneratedRoute.id == session.generated_route_id
    ).first()

    user_message = ChatMessage(
        chat_session_id=session_id,
        role="user",
        content=message_data.content
    )
    db.add(user_message)
    db.commit()
    db.refresh(user_message)

    messages_history = db.query(ChatMessage).filter(
        ChatMessage.chat_session_id == session_id
    ).order_by(ChatMessage.created_at.asc()).all()

    chat_messages = [
        {"role": msg.role, "content": msg.content}
        for msg in messages_history
    ]

    prompt = f"""
You are a knowledgeable tour guide assistant. You have access to the user's generated tour plan below.
Use this plan as context to answer the user's questions. If the user wants to modify the plan, you must provide a Git-style diff.

IMPORTANT: Respond with ONLY valid JSON. No additional text before or after.
The JSON should have these fields:
- "chat_message": A friendly message explaining what you're suggesting
- "diff": A Git-style unified diff (optional, only if suggesting plan modifications)

Tour Plan:
{route.route_text if route else "No route found"}

User Question: {message_data.content}

If the user is asking for modifications to the tour plan, generate a new modified version of the plan and create a Git-style unified diff showing the changes. If they're just asking questions, set "diff" to null.

Example diff format:
---
+++ b/tour_plan.txt
@@ -1,5 +1,5 @@
-10:00 - 11:30: Coffee Shop Visit
+11:00 - 12:30: Extended Coffee Shop Visit (includes dessert)
 11:30 - 12:30: Lunch at Italian Restaurant
 12:30 - 13:30: Museum Visit
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": "You are a tour guide assistant that responds with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.7,
        )

        ai_response_text = response.choices[0].message.content.strip()

        try:
            ai_response_json = json.loads(ai_response_text)
            chat_msg = ai_response_json.get("chat_message", "")
            diff_content = ai_response_json.get("diff")
        except json.JSONDecodeError:
            chat_msg = ai_response_text
            diff_content = None

        assistant_message = ChatMessage(
            chat_session_id=session_id,
            role="assistant",
            content=chat_msg,
            diff_content=diff_content,
            chat_message=chat_msg
        )
        db.add(assistant_message)
        db.commit()
        db.refresh(assistant_message)

        return assistant_message

    except Exception as e:
        print("❌ OpenAI API 报错：", str(e))
        raise HTTPException(status_code=500, detail="Failed to get AI response")

@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessageResponse])
def get_chat_messages(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    messages = db.query(ChatMessage).filter(
        ChatMessage.chat_session_id == session_id
    ).order_by(ChatMessage.created_at.asc()).all()

    return messages

@router.delete("/sessions/{session_id}")
def delete_chat_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    db.delete(session)
    db.commit()
    return {"message": "Chat session deleted successfully"}

@router.post("/sessions/{session_id}/messages/{message_id}/apply-diff")
def apply_diff_to_route(
    session_id: int,
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    message = db.query(ChatMessage).filter(
        ChatMessage.id == message_id,
        ChatMessage.chat_session_id == session_id
    ).first()

    if not message:
        raise HTTPException(status_code=404, detail="Chat message not found")

    if not message.diff_content:
        raise HTTPException(status_code=400, detail="No diff content found in this message")

    route = db.query(GeneratedRoute).filter(
        GeneratedRoute.id == session.generated_route_id
    ).first()

    if not route:
        raise HTTPException(status_code=404, detail="Generated route not found")

    updated_route_text = apply_diff(route.route_text, message.diff_content)

    if updated_route_text is None:
        raise HTTPException(status_code=400, detail="Failed to apply diff - invalid diff format")

    route.route_text = updated_route_text
    db.commit()

    return {
        "message": "Diff applied successfully",
        "updated_route_text": updated_route_text
    }
