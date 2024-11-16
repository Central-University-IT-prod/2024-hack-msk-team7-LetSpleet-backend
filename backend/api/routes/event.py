from datetime import timedelta
from typing import Annotated, Any, List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
import jwt
from backend import crud
from deps import CurrentUser, SessionDep, get_current_active_superuser, get_current_user, verify_hmac
from backend.core import security
from security import get_password_hash
from backend.models import Token, EventBase, Event, User


router = APIRouter()

@router.post('/event')
async def create_event(body: EventBase, session: SessionDep, token: str = Depends(OAuth2PasswordRequestForm)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        user = get_current_user(session, token)
    except jwt.PyJWTError:
        raise credentials_exception
    event = Event(
        name=body.name, description=body.description,
        invited_friends=body.invited_friends, creator=user)
    return event.event_id

@router.get('/event/{id}')
async def get_event(id: int, session: SessionDep, token: str = Depends(OAuth2PasswordRequestForm)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        user = get_current_user(session, token)
    except jwt.PyJWTError:
        raise credentials_exception
    return (status.HTTP_200_OK,
            Event(event_id=id, creator=user).name,
            Event(event_id=id, creator=user).description,
            Event(event_id=id, creator=user).invited_friends)

@router.delete('/event/{id}')
async def delete_event(id: int, session: SessionDep, token: str = Depends(OAuth2PasswordRequestForm)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        user = get_current_user(session, token)
    except jwt.PyJWTError:
        raise credentials_exception
    event = Event(event_id=id, creator=user)
    session.delete(event)
    session.commit()
    return {'msg': 'Deleted successfully', 'status':status.HTTP_200_OK}

@router.put('/event/{id}/invite')
async def invite_friends(body: List[User], id: int, session: SessionDep, token: str = Depends(OAuth2PasswordRequestForm)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        user = get_current_user(session, token)
    except jwt.PyJWTError:
        raise credentials_exception
    for i in body:
        if not User(i.user_id):
            return status.HTTP_404_NOT_FOUND
    event = Event(event_id=id, creator=user)
    event.invited_friends = List[event.invited_friends + body]
    session.commit()
    return status.HTTP_200_OK

@router.get('/event/{id}/join/{secret}')
async def join_to_event(secret: str, id: int, session: SessionDep, token: str = Depends(OAuth2PasswordRequestForm)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        user = get_current_user(session, token)
    except jwt.PyJWTError:
        raise credentials_exception
    if not verify_hmac(secret, token):
        raise HTTPException(status_code=403, detail="Invalid secret code")
    event = Event(event_id=id, creator=user)
    event.invited_friends = List[event.invited_friends.append(user)]
    session.commit()
    return status.HTTP_200_OK


@router.get('/event/{id}/join/link')
async def create_invitelink(id: int, session: SessionDep, token: str = Depends(OAuth2PasswordRequestForm)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        user = get_current_user(session, token)
    except jwt.PyJWTError:
        raise credentials_exception
    pass

@router.delete('/event/{id}/kick/{id_user}')
async def kick(id: int, id_user:int, session: SessionDep, token: str = Depends(OAuth2PasswordRequestForm)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        user = get_current_user(session, token)
    except jwt.PyJWTError:
        raise credentials_exception
    event = Event(event_id=id, creator=user)
    if user != event.creator:
        return status.HTTP_403_FORBIDDEN
    event.invited_friends = List[event.invited_friends.remove(User(user_id=id_user))]
    session.commit()
    return status.HTTP_200_OK


