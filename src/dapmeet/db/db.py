# Этот файл является центральной точкой для конфигурации базы данных.
# Он отвечает за:
# 1. Загрузку переменных окружения из файла .env (с помощью python-dotenv).
# 2. Создание SQLAlchemy `engine`, который является точкой входа к базе данных.
# 3. Создание `SessionLocal` для управления сессиями.
# 4. Определение `Base` для декларативных моделей SQLAlchemy.
#
# Любая часть приложения, которой нужен доступ к БД, должна импортировать
# объекты из этого файла.

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)

# Загружаем переменные из .env файла
load_dotenv()

# Получаем DATABASE_URL из переменных окружения
DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_URL_ASYNC = os.getenv("DATABASE_URL_ASYNC")

# Проверяем, что переменная установлена
if DATABASE_URL is None:
    raise ValueError("DATABASE_URL environment variable not set. Please create a .env file or set it manually.")

# Для async-режима требуется отдельный DSN с asyncpg-драйвером
if DATABASE_URL_ASYNC is None:
    # Разрешаем отсутствовать на раннем этапе миграции — но укажем подсказку
    # Реальное использование async-сессии упадет без этой переменной
    DATABASE_URL_ASYNC = None

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Async engine/session (используется постепенно)
async_engine = None
AsyncSessionLocal = None

if DATABASE_URL_ASYNC:
    # Add SSL for production (Render requires it)
    engine_kwargs = {
        "pool_pre_ping": True,
        "pool_size": 10,  # Reduced for Render's resource limits
        "max_overflow": 10,  # Reduced for Render's resource limits
        "pool_timeout": 30,  # Timeout for getting connection from pool
    }
    
    # Add SSL for production databases (Render requires it)
    if "sslmode=require" in DATABASE_URL_ASYNC:
        engine_kwargs["connect_args"] = {"sslmode": "require"}
    elif "render.com" in DATABASE_URL_ASYNC or ".internal" in DATABASE_URL_ASYNC:
        # Render databases require SSL even for internal connections
        engine_kwargs["connect_args"] = {"sslmode": "require"}
    
    async_engine = create_async_engine(DATABASE_URL_ASYNC, **engine_kwargs)
    AsyncSessionLocal = async_sessionmaker(
        async_engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )
