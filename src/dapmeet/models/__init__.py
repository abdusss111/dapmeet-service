# src/dapmeet/models/__init__.py

# ОБЯЗАТЕЛЬНО импортировать ВСЕ модели для регистрации в SQLAlchemy MetaData
from .user import User
from .meeting import Meeting  
from .segment import TranscriptSegment
from .prompt import Prompt

# Делаем их доступными при импорте пакета
__all__ = ["User", "Meeting", "TranscriptSegment", "Prompt"]