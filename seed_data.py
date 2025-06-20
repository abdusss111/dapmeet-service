from sqlalchemy.orm import Session
from db import SessionLocal
from models import Meeting

user_id = "100579084074270788578"

sample_meetings = [
    {
        "title": "Product Strategy Kickoff",
        "transcript": """
            Welcome everyone to our Q2 product strategy kickoff. Today's discussion focused on aligning our roadmap with 
            customer feedback and emerging trends. Anna presented a competitive analysis showing we're falling behind in AI features. 
            Action items include: (1) finalizing Q2 priorities by Friday, (2) scheduling a design sprint for the new onboarding flow.
        """
    },
    {
        "title": "Engineering Sync — Platform Stability",
        "transcript": """
            The platform team discussed ongoing infrastructure challenges. Downtime incidents in April were traced to memory leaks in the worker nodes. 
            Sanzhar proposed refactoring the job queue system and adding observability dashboards. Follow-up: DevOps to provision staging replicas by Monday.
        """
    },
    {
        "title": "Client Call — Acme Corp Integration",
        "transcript": """
            Met with Acme Corp regarding the integration of our analytics SDK. Their CTO emphasized GDPR compliance and performance impact. 
            Agreed to a phased rollout: start with event tracking, then expand to user identity mapping. Our legal team will send updated DPA by Thursday.
        """
    }
]

def seed():
    db: Session = SessionLocal()
    try:
        for entry in sample_meetings:
            meeting = Meeting(
                id=str(uuid.uuid4()),
                title=entry["title"],
                transcript=entry["transcript"],
                created_at=datetime.utcnow(),
                user_id=user_id
            )
            db.add(meeting)

        db.commit()
        print("✅ Seed complete.")
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
