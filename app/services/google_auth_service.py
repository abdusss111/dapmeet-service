import os
from dotenv import load_dotenv  # ✅ добавить
load_dotenv()  # ✅ вызывается ДО os.getenv

import httpx
import jwt
from sqlalchemy.orm import Session
from fastapi import HTTPException
from models import User

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
JWT_SECRET = os.getenv("NEXTAUTH_SECRET", "secret-key")

async def exchange_code_for_token(code: str) -> str:
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

    if token_resp.status_code != 200:
        raise HTTPException(status_code=400, detail=f"Token exchange failed: {token_resp.text}")

    token_data = token_resp.json()
    return token_data["access_token"]


async def get_google_user_info(access_token: str) -> dict:
    async with httpx.AsyncClient() as client:
        user_resp = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )

    if user_resp.status_code != 200:
        raise HTTPException(status_code=400, detail=f"User info fetch failed: {user_resp.text}")

    return user_resp.json()


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
    return jwt.encode(
        {
            "sub": user_info["id"],
            "email": user_info["email"],
            "name": user_info.get("name", ""),
        },
        JWT_SECRET,
        algorithm="HS256"
    )
