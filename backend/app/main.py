from fastapi import FastAPI

from app.api.routes.auth import router as auth_router
from app.api.routes.client_apps import router as client_apps_router
from app.api.routes.api_keys import router as api_keys_router
from app.api.routes.observations import router as observations_router
from app.core.errors import register_exception_handlers
from app.middleware.request_id import RequestIDMiddleware

app = FastAPI(title="BehaviorPulse API", version="0.1.0")

app.add_middleware(RequestIDMiddleware)
register_exception_handlers(app)

app.include_router(auth_router)
app.include_router(client_apps_router)
app.include_router(api_keys_router)
app.include_router(observations_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}