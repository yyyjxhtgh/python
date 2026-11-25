from collections.abc import Iterator

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import User
from .service import CheckInService

bearer = HTTPBearer(auto_error=False)


def get_session(request: Request) -> Iterator[Session]:
    with request.app.state.session_factory() as session:
        yield session


def get_service(request: Request) -> CheckInService:
    return request.app.state.service


def current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
    s: Session = Depends(get_session),
) -> User:
    if creds is None:
        raise HTTPException(status_code=401, detail="Missing API token")
    user = s.scalar(select(User).where(User.api_token == creds.credentials))
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid API token")
    return user
