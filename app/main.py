import logging
import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sentry_sdk import capture_exception
from starlette.middleware.cors import CORSMiddleware

from app.container.containers import Container
from app.routes.api_v1 import api as api_v1

logger = logging.getLogger()
API_V1_STR = "/api/v1"


async def catch_exceptions_middleware(request: Request, call_next):  # type: ignore
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


def create_app() -> FastAPI:
    container = Container()
    container.config()
    container.logging()
    logger.debug("START create_app FastAPI")
    container.db()
    container.sentry_sdk()

    container.db().create_database()
    container.init_resources()

    fast_api_app = FastAPI()
    fast_api_app.container = container
    fast_api_app.include_router(api_v1.router, prefix=API_V1_STR)
    # Set all CORS enabled origins
    fast_api_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    fast_api_app.middleware("http")(catch_exceptions_middleware)
    logger.debug("DONE configure create_app FastAPI")
    return fast_api_app


app = create_app()


@app.exception_handler(Exception)
async def validation_exception_handler(request, err):
    base_error_message = f"Failed to execute: {request.method}: {request.url}"
    logger.error(err)
    capture_exception(err)
    return JSONResponse(status_code=400, content={"message": f"{base_error_message}. Detail: {err}"})
