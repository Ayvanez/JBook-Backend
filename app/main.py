from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi_jwt_auth.exceptions import AuthJWTException
from starlette.exceptions import HTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.api.errors.http_error import http_error_handler
from app.api.errors.validation_error import http422_error_handler
from app.api.routes.api import router as api_router
from app.core.config import get_app_settings
from app.core.events import create_start_app_handler, create_stop_app_handler


def get_application() -> FastAPI:
    settings = get_app_settings()

    settings.configure_logging()

    application = FastAPI(**settings.fastapi_kwargs)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_hosts,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.add_event_handler(
        "startup",
        create_start_app_handler(application, settings),
    )
    application.add_event_handler(
        "shutdown",
        create_stop_app_handler(application),
    )

    @application.exception_handler(AuthJWTException)
    def authjwt_exception_handler(request: Request, exc: AuthJWTException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message}
        )
    # TODO ^
    application.add_exception_handler(HTTPException, http_error_handler)
    application.add_exception_handler(ValueError, http422_error_handler)

    application.include_router(api_router, prefix=settings.api_prefix)

    return application


app = get_application()