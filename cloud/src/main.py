import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from src.config import setup_logging
from src.database import init_model
from src.router.files import router as files_router
from src.router.users import router as user_router

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await init_model()
    yield


logger = logging.getLogger(__name__)
app = FastAPI(lifespan=lifespan)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


app.include_router(files_router)
app.include_router(user_router)


def start_app() -> None:
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True, app_dir="src")


if __name__ == "__main__":
    start_app()
