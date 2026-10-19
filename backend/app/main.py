from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, categories, dashboard, expenses
from app.core.config import settings
from app.core.errors import register_error_handlers

app = FastAPI(title="Spendar API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,  # narrow: only the frontend origin(s)
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Content-Type", "X-CSRF-Token"],
)

register_error_handlers(app)

api_v1 = APIRouter(prefix="/api/v1")
api_v1.include_router(auth.router)
api_v1.include_router(expenses.router)
api_v1.include_router(categories.router)
api_v1.include_router(dashboard.router)
app.include_router(api_v1)


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
