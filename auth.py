from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from google_auth_service import JWT_SECRET, find_or_create_user
from models import User
from deps import get_db
import jwt
import httpx

oauth2_scheme = HTTPBearer()

def verify_custom_jwt(token: str):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None

async def fetch_google_user_info(token: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {token}"}
        )
    if response.status_code != 200:
        return None
    return response.json()

async def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    # 1. Попытка расшифровать кастомный JWT
    payload = verify_custom_jwt(token.credentials)
    if payload:
        user = db.query(User).filter(User.id == payload["sub"]).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    # 2. Попытка получить инфо по Google access_token
    user_info = await fetch_google_user_info(token.credentials)
    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid token")

    # 3. Найти или создать пользователя в БД
    user = find_or_create_user(user_info, db)
    return user
