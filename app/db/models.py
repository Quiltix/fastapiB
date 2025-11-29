import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    """
    Модель пользователя.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)


    created_events = relationship("Event", back_populates="owner")

    tickets = relationship("Ticket", back_populates="participant")


class Event(Base):
    """
    Модель мероприятия.
    """
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    start_time = Column(DateTime)
    location = Column(String, nullable=False)

    # Внешний ключ на создателя
    owner_id = Column(Integer, ForeignKey("users.id"))

    # Связь с создателем (User)
    # back_populates="created_events" указывает на 'created_events' в модели User.
    owner = relationship("User", back_populates="created_events")

    # ----- ВОТ ИСПРАВЛЕНИЕ! -----
    # Связь со списком билетов/участников на это мероприятие.
    # back_populates="event" указывает на атрибут 'event' в модели Ticket.
    tickets = relationship("Ticket", back_populates="event", cascade="all, delete-orphan")


class Ticket(Base):
    """
    Модель билета.
    """
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    registration_time = Column(DateTime, default=datetime.datetime.now)

    # Внешний ключ на мероприятие
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    # Внешний ключ на участника
    participant_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Связь с мероприятием
    # back_populates="tickets" указывает на атрибут 'tickets' в модели Event.
    event = relationship("Event", back_populates="tickets")

    # Связь с участником (User)
    # back_populates="tickets" указывает на атрибут 'tickets' в модели User.
    participant = relationship("User", back_populates="tickets")