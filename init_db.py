# src/dapmeet/db/init_db.py
from dapmeet.db.db import Base, engine
from os import getenv
from dotenv import load_dotenv
load_dotenv()
def init_db():
    # создаст ВСЕ таблицы, описанные в Base.metadata, которые ещё не созданы
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    print(getenv("DATABASE_URL"))
    init_db()