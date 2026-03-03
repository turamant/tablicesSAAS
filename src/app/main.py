from fastapi import FastAPI
from src.app.api.v1 import auth, tables
from src.app.middleware.auth_middleware import AuthMiddleware
from fastapi.openapi.utils import get_openapi

app = FastAPI(title="Table SaaS", version="0.1.0")

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

@app.get("/")
async def root():
    return {"message": "Table SaaS API"}


