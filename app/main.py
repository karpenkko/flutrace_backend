from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from app.routes import logs, auth, projects, analytics, seed
from app.models import Base
from app.database import engine
import re

app = FastAPI()

async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(logs.router)
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(analytics.router)
app.include_router(seed.router)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Flutrace API",
        version="1.0.0",
        description="API for Flutrace logging and user management",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    secure_prefixes = [r"^/auth/me", r"^/logs", r"^/projects"]

    for path, path_item in openapi_schema["paths"].items():
        if any(re.match(p, path) for p in secure_prefixes):
            for method in path_item.values():
                method.setdefault("security", [{"BearerAuth": []}])
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
