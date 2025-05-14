# В файле init_db.py
from db import Base, engine  # Base = declarative_base(), engine = create_engine(...)
import models  # чтобы подтянуть все таблицы

Base.metadata.create_all(bind=engine)
