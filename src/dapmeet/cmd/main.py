# src/dapmeet/cmd/main.py
import sys
import os
from pathlib import Path

# Настраиваем пути ДО импорта FastAPI и других модулей
def setup_paths():
    """
    Настраивает пути для корректной работы как через run.py, так и через uvicorn напрямую
    """
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent.parent.parent
    src_path = project_root / "src"
    
    src_path_str = str(src_path)
    if src_path_str not in sys.path:
        sys.path.insert(0, src_path_str)
    
    if os.getcwd() != str(project_root):
        os.chdir(str(project_root))

setup_paths()

# Теперь можно импортировать модули
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Загружаем .env файл
load_dotenv()

# Импортируем компоненты приложения
from dapmeet.api import api_router
from dapmeet.core.logging_config import setup_logging
from dapmeet.core.scheduler import start_scheduler, stop_scheduler

# --- Инициализация ---
setup_logging()

# --- Приложение FastAPI ---
app = FastAPI(
    title="DapMeet API",
    description="API for DapMeet meeting transcription service",
    version="1.0.0",
    on_startup=[start_scheduler],
    on_shutdown=[stop_scheduler],
)

# --- Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  #  todo: В проде лучше указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Роутеры ---
app.include_router(api_router)

# --- Базовый эндпоинт ---
@app.get("/")
async def root():
    """Корневой эндпоинт для проверки доступности API."""
    return {"message": "DapMeet API is running"}
