from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, categories, health, items, public, restaurant, templates


def create_app() -> FastAPI:
    app = FastAPI(title='Restaurant Menu API', version='1.0.0')
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(templates.router)
    app.include_router(categories.router)
    app.include_router(items.router)
    app.include_router(restaurant.router)
    app.include_router(public.router)
    return app


app = create_app()
