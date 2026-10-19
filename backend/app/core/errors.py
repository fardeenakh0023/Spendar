from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class AppError(Exception):
    """Business-rule error that maps to an HTTP status code."""

    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(_: Request, exc: AppError):
        return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)

    @app.exception_handler(RequestValidationError)
    async def validation_handler(_: Request, exc: RequestValidationError):
        messages = []
        for err in exc.errors():
            field = ".".join(str(p) for p in err["loc"] if p not in ("body", "query", "path"))
            msg = err["msg"].removeprefix("Value error, ")
            messages.append(f"{field}: {msg}" if field else msg)
        return JSONResponse({"detail": "; ".join(messages)}, status_code=422)
