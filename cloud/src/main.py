from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.database import init_model
import uvicorn

from src.router.files import router as files_router

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await init_model()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(files_router)

def start_app() -> None:
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True, app_dir="src")

if __name__ == "__main__":
    start_app()