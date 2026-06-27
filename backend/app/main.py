from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.database import init_db
from app.routers import hosts, metrics, ports, ssl, settings as settings_router
from app.services.scheduler import shutdown_scheduler, start_scheduler

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    start_scheduler()
    yield
    shutdown_scheduler()


app = FastAPI(
    title="Network Monitor API",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    # Pydantic returns `detail` as a list of error objects; the frontend expects
    # a single string, so flatten it here to keep the API contract consistent.
    first_error = exc.errors()[0]
    message = str(first_error.get("msg", "入力内容が不正です"))
    if message.startswith("Value error, "):
        message = message[len("Value error, "):]
    return JSONResponse(status_code=422, content={"detail": message})


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-XSS-Protection"] = "0"
    response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    return response


app.include_router(hosts.router)
app.include_router(metrics.router)
app.include_router(ports.router)
app.include_router(ssl.router)
app.include_router(settings_router.router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
