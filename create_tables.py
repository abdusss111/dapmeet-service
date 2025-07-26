# Этот скрипт предназначен для первоначального создания всех таблиц в базе данных.
# Он напрямую использует метаданные SQLAlchemy (Base.metadata) для генерации
# и выполнения SQL-команд CREATE TABLE.
#
# ВАЖНО: Этот скрипт не управляет версиями схемы (миграциями).
# Он полезен для быстрой настройки пустой базы данных.
# Для последующих изменений схемы следует использовать Alembic.

import os
import sys
import logging

# Добавляем src в путь, чтобы найти модули
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # Импортируем engine и Base.
    # db.py сам позаботится о загрузке .env и создании engine.
    from dapmeet.db.db import Base, engine
    # Импортируем все модели, чтобы они зарегистрировались в Base.metadata
    from dapmeet.models import user, meeting, segment, chat_message

    logger.info("Attempting to create all tables in the database...")
    # Создаем все таблицы
    Base.metadata.create_all(bind=engine)
    logger.info("Successfully created tables.")

except ImportError as e:
    logger.error(f"Failed to import a module: {e}")
    logger.error("Please ensure all dependencies are installed and the PYTHONPATH is correct.")
except Exception as e:
    logger.error(f"An error occurred while creating tables: {e}")
