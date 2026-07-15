from fastapi import FastAPI

from app.api.routes.auth import router as auth_router
from app.core.errors import register_exception_handlers
from app.middleware.request_id import RequestIDMiddleware

app = FastAPI(title="BehaviorPulse API", version="0.1.0")

app.add_middleware(RequestIDMiddleware)
register_exception_handlers(app)

app.include_router(auth_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}