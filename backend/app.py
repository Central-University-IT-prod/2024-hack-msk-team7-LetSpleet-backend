from typing import Annotated
from datetime import timedelta

from sqlmodel import select, or_
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

from backend.core import dependencies
from backend.core import security
from backend.core.security import get_password_hash
from backend.core.db import build_db
from backend.core.dependencies import (
                                       sessionDep, 
                                       CurrentUser)

from backend.core.config import CONFIG
from backend.models import (User, Event, Duty, EVENT_MEMBERS,
                            UserCreate, EventCreate, DutyCreate,
                            Token,
                            UserInfo, 
                            UserInfoFull, EventInfoFull, DutyInfoFull, EventInfoFullest,
                            UserBase,                             )
import backend.core.security as security
import backend.crud as crud
from backend.crud import create_user, create_event, create_duty, get_user

from sqlmodel import create_engine, SQLModel
from backend.core.config import CONFIG



engine = create_engine(CONFIG.db_uri)
SQLModel.metadata.create_all(engine)

build_db()
app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------- USER API ----------- #

@app.get("/user/exists/{username}", status_code=200)
async def is_a_user(username: str, session: sessionDep):
    statement = select(User).where(User.login == username)
    selected_user = session.exec(statement).first()
    print(selected_user)
    if not selected_user:
        raise HTTPException(404, "user not found")
    return {""}


@app.post("/user/login", status_code=200, response_model=Token)
async def register_user(session: sessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = crud.auth_user(session=session, login=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(404, "incorrect password or login")

    return Token(access_token=security.create_access_token(user.user_id, expires_delta=CONFIG.token_expire_timedelta))


@app.get("/user/me", response_model=User)
async def get_me(current_user: CurrentUser):
    return current_user



@app.post("/user/register", status_code=200, response_model=UserInfo)
async def add_new_user(session: sessionDep, userinfo: UserInfoFull):
    user_in = UserCreate(login=userinfo.username, visible_name=userinfo.visibleName, password=get_password_hash(userinfo.password))
    statement_unique = select(User).where(User.login == user_in.login)
    old_user = session.exec(statement_unique).first()
    if old_user:
        raise HTTPException(404, "user already exists")
    create_user(session=session, item_in=user_in)
    return UserInfo(username=userinfo.username, password=userinfo.password)

@app.get("/users")
async def list_all_users(session: sessionDep):
    statement = select(User)
    users = session.exec(statement).all()
    return users

# ------------- EVENT API -------------- #
@app.get("/me/event")
async def get_all_events(session: sessionDep, current_user: CurrentUser):
    statement = select(Event).where(Event.creator_id == current_user.user_id)
    events = session.exec(statement).all()
    return events
    


@app.post("/event/register", status_code=200)
async def add_new_even(session: sessionDep, current_user: CurrentUser, eventinfo: EventInfoFull): 
    user_ids = [get_user(session=session, login=username) for username in eventinfo.event_members]
    #user_ids = [1, 2, 3]
    EVENT_MEMBERS.append(user_ids)
    event_members_id = len(EVENT_MEMBERS) - 1
    event_in = EventCreate(
            event_name=eventinfo.event_name,
            event_members_index=event_members_id,
            creator_id=current_user.user_id,
                           )
    statement_unique = select(Event).where(Event.creator_id == event_in.creator_id).where(Event.event_name == event_in.event_name)
    old_user = session.exec(statement_unique).first()
    if old_user:
        raise HTTPException(406, "event name must be unique inside one creator")
    new_event = create_event(session=session, item_in=event_in)
    return new_event.event_id


@app.get("/event/{event_id}", response_model=EventInfoFullest)
async def get_event(session: sessionDep, event_id: int):
    statement = select(Event).where(Event.event_id == event_id)
    cur_event = session.exec(statement).first()
    creator = session.exec(select(User).where(User.user_id == cur_event.creator_id)).first()
    info = EventInfoFullest(
            event_name=cur_event.event_name,
            visible_name_creator=creator.visible_name,
            wastes=[""]
            )
    return info


# --------------- DUTY API ------------- #

@app.get("/duty/{user_id}")
def list_all_duties(session: sessionDep, user_id: int):
    pass

def main():
    build_db()
    pass
    


if __name__ == "__main__":
    main()
