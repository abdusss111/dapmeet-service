from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from dapmeet.core.deps import get_db
from dapmeet.schemas.auth import CodePayload
from dapmeet.services.google_auth_service import (
    exchange_code_for_token,
    get_google_user_info,
    find_or_create_user,
    generate_jwt
)

router = APIRouter()

@router.post("/google")
async def google_auth(payload: CodePayload, db: Session = Depends(get_db)):
    access_token = await exchange_code_for_token(payload.code)
    user_info = await get_google_user_info(access_token)
    user = find_or_create_user(user_info, db)
    jwt_token = generate_jwt(user_info)

    return {"access_token": jwt_token, "user": user_info}
