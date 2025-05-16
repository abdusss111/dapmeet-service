from sqlalchemy.orm import Session
from models import Meeting, User
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# ⚙️ DB setup
DATABASE_URL = "postgresql://dapuser:dappass@db:5432/dapmeet"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

# 🔍 Specify user
user_id = "107269937002782393048"

# ✅ Delete all meetings for this user
deleted_count = session.query(Meeting).filter_by(user_id=user_id).delete()

# 💾 Commit the transaction
session.commit()

print(f"🗑️ Deleted {deleted_count} meeting(s) for user {user_id}")
