from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.auth import router as auth_router
from app.api.routes.client_apps import router as client_apps_router
from app.api.routes.api_keys import router as api_keys_router
from app.api.routes.observations import router as observations_router
from app.api.routes.services import router as services_router
from app.api.routes.logs import router as logs_router
from app.api.routes.usage import router as usage_router
from app.api.routes.analyses import router as analyses_router
from app.core.errors import register_exception_handlers
from app.db.seed_services import seed_services
from app.middleware.request_id import RequestIDMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    seed_services()
    yield


app = FastAPI(title="BehaviorPulse API", version="0.1.0", lifespan=lifespan)

app.add_middleware(RequestIDMiddleware)
register_exception_handlers(app)

app.include_router(auth_router)
app.include_router(client_apps_router)
app.include_router(api_keys_router)
app.include_router(observations_router)
app.include_router(services_router)
app.include_router(logs_router)
app.include_router(usage_router)
app.include_router(analyses_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}