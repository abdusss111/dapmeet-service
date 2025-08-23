from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
import httpx

from dapmeet.core.deps import get_async_db, get_http_client
from dapmeet.schemas.auth import CodePayload
from dapmeet.services.google_auth_service import (
    authenticate_with_google_token,
    exchange_code_for_token,
    get_google_user_info,
    find_or_create_user,
    generate_jwt
)

router = APIRouter()

@router.post("/google")
async def google_auth(
    payload: CodePayload, 
    db: AsyncSession = Depends(get_async_db),
    http_client: httpx.AsyncClient = Depends(get_http_client)
):
    access_token = await exchange_code_for_token(payload.code, http_client)
    user_info = await get_google_user_info(access_token, http_client)
    user = await find_or_create_user(user_info, db)
    jwt_token = generate_jwt(user_info)

    return {"access_token": jwt_token, "user": user_info}

@router.post("/validate")
async def validate_chrome_extension_auth(
    request: Request,
    db: AsyncSession = Depends(get_async_db),
    http_client: httpx.AsyncClient = Depends(get_http_client)
):
    # Получаем Google access token из заголовка
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid auth header")
    
    google_token = auth_header.split(" ")[1]
    
    # Аутентифицируем пользователя
    user, jwt_token = await authenticate_with_google_token(google_token, db, http_client)
    
    return {
        "token": jwt_token,
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name
        }
    }