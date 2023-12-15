from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from routers import auth, candidates, matches, positions


def get_application():
    _app = FastAPI(title=settings.PROJECT_NAME, docs_url='/')

    _app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            str(origin) for origin in settings.BACKEND_CORS_ORIGINS
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return _app


app = get_application()
app.include_router(candidates.router, tags=['candidates'])
app.include_router(positions.router, tags=['positions'])
app.include_router(matches.router, tags=['matches'])
app.include_router(auth.router, tags=['auth'])
