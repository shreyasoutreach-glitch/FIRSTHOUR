"""Bootstrap deterministic demo data only when DEMO_MODE is enabled and the database is empty.

This is intentionally idempotent: it never wipes a populated database. Production
deployments must set DEMO_MODE=false and therefore skip this bootstrap entirely.
"""
from app.core.config import get_settings
from app.core.database import SessionLocal
from app.models import entities as m
from seed.seed import run_seed


def main() -> None:
    settings = get_settings()
    if not settings.demo_mode:
        print("Demo bootstrap skipped: DEMO_MODE=false")
        return

    db = SessionLocal()
    try:
        db.set_tenant(None)
        user_count = db.query(m.User).count()
        if user_count:
            print(f"Demo bootstrap skipped: database already has {user_count} user(s)")
            return
        result = run_seed(db, seed_value=settings.seed)
        print(f"Demo bootstrap complete: {result}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
