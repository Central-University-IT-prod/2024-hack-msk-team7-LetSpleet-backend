from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy.dialects.postgresql import JSONB



EVENT_MEMBERS = []


class UserInfo(BaseModel):
    username: str
    password: str

class UserInfoFull(UserInfo):
    visibleName: str

class EventInfoFull(BaseModel):
    event_name: str
    event_members: List[str]

class EventInfoFullest(BaseModel):
    event_name: str
    visible_name_creator: str
    wastes: List[str]


class ReceiptInfoFull(BaseModel):
    receipt_json: Dict
    event_id: int

class DutyInfoFull(BaseModel):
    receipt_id: int
    borrower_id: int
    duty_amt: int




class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None



class UserBase(SQLModel):
    login: str = Field(index=True, unique=True, nullable=False)
    visible_name: str = Field(nullable=False)
    password: str = Field(nullable=False)


class User(UserBase, table=True):
    user_id: Optional[int] = Field(default=None, primary_key=True)


class UserCreate(UserBase):
    pass

class UserGet(UserBase):
    pass


class EventBase(SQLModel):
    event_name: str = Field(nullable=False)


class Event(EventBase, table=True):
    event_id: Optional[int] = Field(default=None, primary_key=True)
    event_members_index: int = Field()

    
    creator_id: int | None = Field(nullable=True, foreign_key="user.user_id")


class EventCreate(EventBase):
    event_members_index: int
    creator_id: int


class DutyBase(SQLModel):
    duty_amt: float = Field(nullable=False)


class Duty(DutyBase, table=True):

    duty_id: Optional[int] = Field(default=None, primary_key=True)
    event_id: int = Field(foreign_key="event.event_id", nullable=False)
    borrower_id: int = Field(foreign_key="user.user_id", nullable=False)
    duty_amt: float = Field(nullable=False)
    name: str = Field(nullable=False)


class DutyCreate(DutyBase):
    receipt_id: int
    borrower_id: int


