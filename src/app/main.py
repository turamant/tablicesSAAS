from fastapi import FastAPI
from src.app.api.v1 import auth, tables, data, fields
from fastapi.middleware.cors import CORSMiddleware
from src.app.middleware.auth_middleware import AuthMiddleware
from fastapi.openapi.utils import get_openapi

app = FastAPI(title="Table SaaS", version="0.1.0")

# CORS — ЭТО РЕШЕНИЕ!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # твой фронт
    allow_credentials=True,  # обязательно для кук!
    allow_methods=["*"],
    allow_headers=["*"],
)

# Добавляем схему для cookie
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Table SaaS",
        version="0.1.0",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "cookieAuth": {
            "type": "apiKey",
            "in": "cookie",
            "name": "access_token"
        }
    }
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            openapi_schema["paths"][path][method]["security"] = [{"cookieAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Middleware
app.add_middleware(AuthMiddleware)

# Routers
app.include_router(auth.router)
app.include_router(tables.router)
app.include_router(data.router)
app.include_router(fields.router)

@app.get("/")
async def root():
    return {"message": "Table SaaS API"}


