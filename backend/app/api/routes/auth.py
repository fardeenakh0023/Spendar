from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.api.dependencies import get_csrf_protected_user, get_current_session
from app.core.config import settings
from app.core.database import get_db
from app.models import UserSession
from app.schemas.user import AuthOut, LoginRequest, RegisterRequest, UserOut
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    return auth_service.register(db, data)


@router.post("/login", response_model=AuthOut)
def login(data: LoginRequest, response: Response, db: Session = Depends(get_db)):
    raw_token, session = auth_service.login(db, data)
    response.set_cookie(
        settings.SESSION_COOKIE_NAME, raw_token,
        max_age=settings.SESSION_EXPIRE_MINUTES * 60,
        httponly=True, secure=settings.COOKIE_SECURE, samesite=settings.COOKIE_SAMESITE, path="/",
    )
    return {"user": session.user, "csrf_token": session.csrf_token}


@router.post("/logout", status_code=204)
def logout(
    response: Response,
    session: UserSession = Depends(get_current_session),
    _user=Depends(get_csrf_protected_user),
    db: Session = Depends(get_db),
):
    auth_service.logout(db, session)
    response.delete_cookie(settings.SESSION_COOKIE_NAME, path="/")


@router.get("/me", response_model=AuthOut)
def me(session: UserSession = Depends(get_current_session)):
    return {"user": session.user, "csrf_token": session.csrf_token}
