import logging
import os
from apscheduler.schedulers.background import BackgroundScheduler
from dapmeet.core.containers import container
from dapmeet.db.db import SessionLocal

def batch_processing_job():
    """
    Задача, которую будет выполнять планировщик.
    Создает временную сессию БД для выполнения работы.
    """
    logging.info("Scheduler: Running batch processing job...")
    db_session = None
    try:
        # Используем 'with' для автоматического закрытия сессии
        with SessionLocal() as db_session:
            # Получаем сервис через контейнер, передавая ему сессию вручную
            segment_service = container.get_segment_service(db=db_session)
            segment_service.process_all_batches()
    except Exception as e:
        logging.error(f"Scheduler: Error during batch processing job: {e}", exc_info=True)
    
    logging.info("Scheduler: Batch processing job finished.")

# Получаем интервал из переменной окружения
interval_seconds = int(os.getenv("SCHEDULER_INTERVAL_SECONDS", 15))

scheduler = BackgroundScheduler()
scheduler.add_job(
    batch_processing_job, 
    'interval', 
    seconds=interval_seconds, 
    id="segment_batch_job"
)

def start_scheduler():
    """Запускает планировщик."""
    try:
        scheduler.start()
        logging.info("Scheduler has been started.")
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()

def stop_scheduler():
    """Останавливает планировщик."""
    scheduler.shutdown()
    logging.info("Scheduler has been shut down.")
