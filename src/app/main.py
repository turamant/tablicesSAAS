from fastapi import FastAPI
from src.app.api.v1 import auth
from src.app.middleware.auth_middleware import AuthMiddleware

app = FastAPI(title="Table SaaS", version="0.1.0")

# Middleware
app.add_middleware(AuthMiddleware)

# Routers
app.include_router(auth.router)

@app.get("/")
async def root():
    return {"message": "Table SaaS API"}