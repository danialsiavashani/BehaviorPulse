from app.db.models.service import Service
from app.db.session import SessionLocal

SERVICES = [
    {
        "service_key": "observations.analyze",
        "name": "Observation Analysis",
        "description": (
            "Analyze observed entities over time from cameras, sensors, "
            "detections, or monitoring systems. Computes activity patterns, "
            "source patterns, recurring windows, confidence trends, and "
            "prediction windows."
        ),
        "status": "active",
        "endpoint": "/v1/observations/analyze",
    },
]


def seed_services() -> None:
    db = SessionLocal()
    try:
        for entry in SERVICES:
            existing = db.query(Service).filter_by(service_key=entry["service_key"]).first()
            if existing:
                continue
            db.add(Service(**entry))
        db.commit()
        print(f"Seeded {len(SERVICES)} services (skipped any that already existed).")
    finally:
        db.close()


if __name__ == "__main__":
    seed_services()