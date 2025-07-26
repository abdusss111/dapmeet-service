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

# Загружаем переменные из .env файла
load_dotenv()

# Получаем DATABASE_URL из переменных окружения
DATABASE_URL = os.getenv("DATABASE_URL")

# Проверяем, что переменная установлена
if DATABASE_URL is None:
    raise ValueError("DATABASE_URL environment variable not set. Please create a .env file or set it manually.")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
