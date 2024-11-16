from datetime import timedelta
from typing import Annotated, Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
import jwt
from backend import crud
from deps import CurrentUser, SessionDep, get_current_active_superuser, get_current_user, verify_hmac
from backend.core import security
from security import get_password_hash
from backend.models import Token, EventBase, Event, User, ReceiptBase, Receipt

router = APIRouter()


@router.post('/event/{id}/receipt')
async def create_receipt(body: ReceiptBase, id: int, session: SessionDep,
                         token: str = Depends(OAuth2PasswordRequestForm)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        user = get_current_user(session, token)
    except jwt.PyJWTError:
        raise credentials_exception
    for i in body.receipt_json.values():
        if not isinstance(i, User):
            return status.HTTP_404_NOT_FOUND
    event = Event(event_id=id, creator=user)
    receipt = Receipt(event_id=id, event=event, duties=body.receipt_json)
    try:
        event.receipts = List[event.receipts.append(receipt)]
    except Exception as e:
        return e
    session.commit()
    return {'data': receipt.receipt_id}


@router.delete('/event/{id}/receipt/{receipt_id}/delete')
async def delete_receipt(id:int, receipt_id: int, session: SessionDep,
                         token: str = Depends(OAuth2PasswordRequestForm), status_code=200):
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
    receipt = Receipt(receipt_id=receipt_id, event=event)
    for i in receipt.receipt_json.values():
        if not isinstance(i, User):
            return {'status': status.HTTP_404_NOT_FOUND}
    session.delete(Receipt, receipt)
    session.commit()
    return {'msg': 'Deleted successfully'}


@router.post('/event/{id}/reciept/{r_id}/claim')
async def claim_position(body: list, query: Optional[User], id:int, r_id: int, session: SessionDep,
                         token: str = Depends(OAuth2PasswordRequestForm), status_code=200):
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
    receipt = Receipt(receipt_id=r_id, event=event)
    for i in receipt.receipt_json.values():
        if not isinstance(i, User):
            return {""}
