# src/dapmeet/db/init_db.py
from dapmeet.db.db import Base, engine

def init_db():
    # создаст ВСЕ таблицы, описанные в Base.metadata, которые ещё не созданы
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
