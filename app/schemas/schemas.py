from datetime import datetime
from typing import List

from pydantic import BaseModel, Field

class UpdateUsername(BaseModel):
    username: str = Field(..., min_length=5)

class UpdatePassword(BaseModel):
    old_password: str = Field(..., min_length=5)
    new_password: str = Field(..., min_length=5)

class User(BaseModel):
    id: int
    username: str
    created_events: List[EventInUser] = []
    tickets: List[TicketInUser] = []

    class Config:
        from_attributes = True

class UserAuth(BaseModel):
    username: str = Field(..., min_length=5)
    password: str = Field(..., min_length=5)


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: int

class EventCreate(BaseModel):
    title: str = Field(..., min_length=4)
    description: str
    start_time: datetime
    location: str = Field(..., min_length=4)

class TicketCreate(BaseModel):
    event_id: int


class OwnerInEvent(BaseModel):
    id: int
    username: str


class ParticipantInTicket(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True

class TicketInEvent(BaseModel):
    id: int
    registration_time: datetime
    participant: ParticipantInTicket

    class Config:
        from_attributes = True


class EventInUser(BaseModel):
    id: int
    title: str
    start_time: datetime

    class Config:
        from_attributes = True

class TicketInUser(BaseModel):
    id: int
    registration_time: datetime
    event: EventInUser

    class Config:
        from_attributes = True



class Event(BaseModel):
    id: int
    title: str
    description: str
    start_time: datetime
    location: str
    owner: OwnerInEvent
    tickets: List[TicketInEvent] = []

    class Config:
        from_attributes = True

class Ticket(BaseModel):
    id: int
    registration_time: datetime
    event: EventInUser
    participant: ParticipantInTicket

    class Config:
        from_attributes = True


Event.model_rebuild()
Ticket.model_rebuild()
User.model_rebuild()
TicketInEvent.model_rebuild()
TicketInUser.model_rebuild()