from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import settings
from app.database.base import Base
from app.database.session import SessionLocal, engine
from app.models import *  # noqa: F403
from app.routers import auth, banco, dashboard, notifications, propuestas, solicitudes, users
from app.services.seed import seed_initial_data


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name)
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.secret_key,
        same_site="lax",
        https_only=False,
    )

    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_initial_data(db)

    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    app.include_router(auth.router)
    app.include_router(dashboard.router)
    app.include_router(users.router)
    app.include_router(solicitudes.router)
    app.include_router(propuestas.router)
    app.include_router(banco.router)
    app.include_router(notifications.router)
    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

