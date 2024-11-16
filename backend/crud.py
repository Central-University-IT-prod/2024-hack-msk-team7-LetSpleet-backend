from sqlmodel import Session, select
from backend.core.security import verify_password
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from backend.models import (
        User, UserCreate,
        Event, EventCreate,
        Duty, DutyCreate,
        ) 


def create_user(*, session: Session, item_in: UserCreate):
    new_user = User.model_validate(item_in)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user

def get_user(*, session: Session, login: str):
    statement = select(User).where(User.login == login)
    user = session.exec(statement)
    if not user:
        return None
    return user


def auth_user(*, session: Session, login: str, password: str):
    statement = select(User).where(User.login == login)
    session_user = session.exec(statement).first()
    if not session_user:
        return None
    if not verify_password(password, session_user.password):
        return None
    return session_user


def create_event(*, session: Session, item_in: EventCreate):
    new_event = Event.model_validate(item_in)
    session.add(new_event)
    session.commit()
    session.refresh(new_event)
    return new_event

def create_duty(*, session: Session, item_in: DutyCreate):
    new_duty = Duty.model_validate(item_in)
    session.add(new_duty)
    session.commit()
    session.refresh(new_duty)
    return new_duty

def get_duties(*, session: Session, borrower_id: int):
    statement = select(Duty).where(Duty.borrower_id == borrower_id)
    session_duties = session.exec(statement).all()



