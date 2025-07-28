import logging
import os
import sys
from pathlib import Path
from pythonjsonlogger import jsonlogger

def setup_logging():
    """
    Настраивает логирование на основе переменных окружения.
    """
    log_path_str = os.getenv("SEGMENT_LOG_PATH")
    if not log_path_str:
        raise ValueError("SEGMENT_LOG_PATH environment variable not set. Application cannot start.")

    log_path = Path(log_path_str)
    
    # Создаем родительскую директорию для лог-файла, если ее нет
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Настройка логгера для батчей сегментов
    segment_logger = logging.getLogger("segment_batch_logger")
    segment_logger.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())
    segment_logger.propagate = False

    # Обработчик для записи в файл .jsonl
    log_handler = logging.FileHandler(log_path)
    
    # Форматер для преобразования логов в JSON
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s'
    )
    
    log_handler.setFormatter(formatter)
    
    # Очищаем старые хендлеры и добавляем новый, чтобы избежать дублирования
    if segment_logger.hasHandlers():
        segment_logger.handlers.clear()
    segment_logger.addHandler(log_handler)

# Настройка не вызывается автоматически при импорте,
# а будет вызвана в main.py, чтобы гарантировать загрузку .env

# Пример использования:
# from dapmeet.core.logging_config import segment_logger
# segment_logger.info("Test message", extra={'key': 'value'})
