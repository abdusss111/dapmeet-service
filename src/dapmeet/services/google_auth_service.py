import os
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"))

import httpx
import jwt
from sqlalchemy.orm import Session
from fastapi import HTTPException
from dapmeet.models.user import User

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_ID_EXTENSION = os.getenv("GOOGLE_CLIENT_ID_EXTENSION")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
JWT_SECRET = os.getenv("NEXTAUTH_SECRET", "secret-key")


async def validate_chrome_access_token(access_token: str) -> dict:
    """
    Валидирует access token для Chrome Identity API
    Проверяет audience и expiration
    """
    async with httpx.AsyncClient() as client:
        token_info_resp = await client.get(
            f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}"
        )

    if token_info_resp.status_code != 200:
        raise HTTPException(
            status_code=401,
            detail=f"Token validation failed: {token_info_resp.text}"
        )

    token_info = token_info_resp.json()

    if token_info.get("audience") != GOOGLE_CLIENT_ID_EXTENSION:
        raise HTTPException(
            status_code=401,
            detail="Token audience mismatch - token not issued for this application"
        )

    if token_info.get("expires_in", 0) <= 0:
        raise HTTPException(
            status_code=401,
            detail="Token has expired"
        )

    return token_info


async def get_google_user_info(access_token: str) -> dict:
    """
    Получает информацию о пользователе из Google API
    """
    async with httpx.AsyncClient() as client:
        user_resp = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )

    if user_resp.status_code != 200:
        raise HTTPException(
            status_code=400,
            detail=f"User info fetch failed: {user_resp.text}"
        )

    return user_resp.json()


async def authenticate_with_google_token(access_token: str, db: Session) -> tuple[User, str]:
    """
    1️⃣ Валидирует Google токен для расширения
    2️⃣ Получает user info
    3️⃣ Создает/находит пользователя в БД
    4️⃣ Генерирует кастомный JWT
    """
    try:
        token_info = await validate_chrome_access_token(access_token)
        user_info = await get_google_user_info(access_token)

        user = find_or_create_user(user_info, db)
        jwt_token = generate_jwt(user_info)

        return user, jwt_token

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Authentication failed: {str(e)}"
        )


def find_or_create_user(user_info: dict, db: Session) -> User:
    user = db.query(User).filter(User.id == user_info["id"]).first()
    if not user:
        user = User(
            id=user_info["id"],
            email=user_info["email"],
            name=user_info.get("name", "")
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def generate_jwt(user_info: dict) -> str:
    payload = {
        "sub": user_info["id"],
        "email": user_info["email"],
        "name": user_info.get("name", ""),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")
