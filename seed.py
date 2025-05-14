from sqlalchemy.orm import Session
from db import SessionLocal
from models import Meeting
from datetime import datetime
import uuid

# ID пользователя, для которого создаём встречу
user_id = "100579084074270788578"

# Пример транскрипта (можешь вставить любой другой)
transcript_text = """
00:00 Salta Bolatova: Сегодня мы проводим встречу по итогам месяца.
00:10 Jaslan Aldongarov: Да, обсудим воронку продаж и обратную связь от клиентов.
00:25 Salta Bolatova: Ещё важно затронуть планы на следующую неделю, особенно по корпоративам.
00:45 Jaslan Aldongarov: Согласен, и обсудим возможную автоматизацию подтверждений участия.
"""

# Название встречи
meeting_title = "Обсуждение итогов и планов"

def create_transcript():
    db: Session = SessionLocal()
    try:
        meeting = Meeting(
            id=str(uuid.uuid4()),
            title=meeting_title,
            transcript=transcript_text,
            created_at=datetime.utcnow(),
            user_id=user_id
        )
        db.add(meeting)
        db.commit()
        print(f"✅ Транскрипт добавлен (ID встречи: {meeting.id})")
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_transcript()
