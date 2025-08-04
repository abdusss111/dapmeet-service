# src/dapmeet/cmd/main.py
import sys
import os
from pathlib import Path

# Настраиваем пути ДО импорта FastAPI и других модулей
def setup_paths():
    """
    Настраивает пути для корректной работы как через run.py, так и через uvicorn напрямую
    """
    # Получаем абсолютный путь к корню проекта
    # Структура: project_root/src/dapmeet/cmd/main.py
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent.parent.parent  # Поднимаемся на 4 уровня вверх
    src_path = project_root / "src"
    
    # Добавляем src в sys.path если его там нет
    src_path_str = str(src_path)
    if src_path_str not in sys.path:
        sys.path.insert(0, src_path_str)
    
    # Устанавливаем рабочую директорию в корень проекта (где находится .env)
    if os.getcwd() != str(project_root):
        os.chdir(str(project_root))

# Вызываем настройку путей ПЕРЕД всеми импортами
setup_paths()

# Теперь можно импортировать модули
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Загружаем .env файл
load_dotenv()

# Импортируем роутер после настройки всех путей
from dapmeet.api import api_router as main_router

app = FastAPI(
    title="DapMeet API",
    description="API for DapMeet meeting transcription service",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(main_router)

@app.get("/")
async def root():
    return {"message": "Dapmeet API is running"}
