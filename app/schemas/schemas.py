from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

#Вспомогательные схемы
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
    event: EventInUser

    class Config:
        from_attributes = True

#Схемы пользователя
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

#Схемы для токена
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    sub: str

#Схемы событий
class EventCreate(BaseModel):
    title: str = Field(..., min_length=4)
    description: str
    start_time: datetime
    location: str = Field(..., min_length=4)

class EventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=4)
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    location: Optional[str] = Field(None, min_length=4)

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

class EventShort(BaseModel):
    id: int
    title: str
    description: str
    start_time: datetime
    location: str
    owner: OwnerInEvent

    class Config:
        from_attributes = True



#Схемы билетов
class TicketCreate(BaseModel):
    event_id: int


class Ticket(BaseModel):
    id: int
    event: EventInUser
    participant: ParticipantInTicket

    class Config:
        from_attributes = True

Event.model_rebuild()
Ticket.model_rebuild()
User.model_rebuild()
TicketInEvent.model_rebuild()
TicketInUser.model_rebuild()