from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

from .routers import works, bangumi, game_profiles, tags  # noqa: E402

app.include_router(works.router, prefix="/api")
app.include_router(bangumi.router, prefix="/api")
app.include_router(game_profiles.router, prefix="/api")
app.include_router(tags.router, prefix="/api")
