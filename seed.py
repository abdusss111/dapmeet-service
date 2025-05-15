from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from models import User, Meeting
from datetime import date
import uuid

# 🔧 Подключение к БД — настрой под себя
DATABASE_URL = "postgresql://dapuser:dappass@db:5432/dapmeet"
engine = create_engine(DATABASE_URL)

# ⚙️ Создание сессии
session = Session(bind=engine)

# 🔍 Найти пользователя
user_id = "107269937002782393048"
user = session.query(User).filter_by(id=user_id).first()

if not user:
    print("❌ Пользователь не найден.")
else:
    # ✅ Создаём плейсхолдер митинг
    meeting = Meeting(
        id=str(uuid.uuid4()),
        title="Placeholder Meeting",
        transcript="Это плейсхолдерный транскрипт.",
        created_at=date.today(),
        user_id=user.id,
        chat_history={"messages": []}  # или None
    )

    session.add(meeting)
    session.commit()
    print(f"✅ Митинг создан: {meeting.id}")
