"""Bootstrap deterministic demo data only when DEMO_MODE is enabled and the
expected seeded administrator is absent.

This is intentionally idempotent for the shipped demo: it only resets/reseeds
when the deterministic SEED=42 administrator token is missing. Production
deployments must set DEMO_MODE=false and therefore skip this bootstrap.
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
        expected_admin_token = "3e7d80fdfed273606f4c76ff8b24f98b098d2f129a31e399"
        admin_exists = db.query(m.User).filter(m.User.api_token == expected_admin_token).first()
        if admin_exists:
            print("Demo bootstrap skipped: deterministic administrator already present")
            return
        result = run_seed(db, seed_value=settings.seed)
        print(f"Demo bootstrap complete: {result}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
