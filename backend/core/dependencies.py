from typing import Annotated
from fastapi import Depends, HTTPException, status
from sqlmodel import Session
from backend.core.db import engine
import jwt
from jwt.exceptions import InvalidKeyError
from backend.models import TokenPayload, User
from pydantic import ValidationError
from fastapi.security import OAuth2PasswordBearer
from backend.core.config import CONFIG



SECRET_KEY = "OOOO YEAHH SECRET KEY"
ALGORITHM = "HS256"
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl="/user/login"
)


def get_session():
    with Session(engine) as session:
        yield session


sessionDep = Annotated[Session, Depends(get_session)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_current_user(session: sessionDep, token: TokenDep):
    try:
        payload = jwt.decode(
            token, SECRET_KEY, algorithms=[ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidKeyError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = session.get(User, token_data.sub)
    return user

CurrentUser = Annotated[User, Depends(get_current_user)]



