from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from deps import get_db
from router import router as main_router
from google_auth_service import (
    exchange_code_for_token,
    get_google_user_info,
    find_or_create_user,
    generate_jwt
)

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://dapmeet.kz"],  # or ["*"] for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(main_router)


class CodePayload(BaseModel):
    code: str


@app.post("/auth/google")
async def google_auth(payload: CodePayload, db: Session = Depends(get_db)):
    access_token = await exchange_code_for_token(payload.code)
    user_info = await get_google_user_info(access_token)
    user = find_or_create_user(user_info, db)
    jwt_token = generate_jwt(user_info)

    return {"access_token": jwt_token, "user": user_info}
