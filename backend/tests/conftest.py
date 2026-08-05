import pytest

from app.db.seed_services import seed_services


@pytest.fixture(scope="session", autouse=True)
def _seed_services_once():
    """TestClient(app) - the pattern every test file in this suite uses -
    does not trigger FastAPI's lifespan. Confirmed directly: making a real
    request through a plain TestClient(app) does not run seed_services().
    A real app start (uvicorn) does, which is why a Codespace that's ever
    run the dev server already has this data locally and this gap goes
    unnoticed. CI's Postgres container starts completely empty every run,
    so any test expecting a seeded service (test_services.py) fails there
    unless this runs first. autouse=True + scope="session" means this
    fires exactly once, automatically, before any test in the run - no
    test file needs to import or reference it."""
    seed_services()