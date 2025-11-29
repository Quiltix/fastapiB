import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    """
    Модель пользователя. Хранит информацию о зарегистрированных пользователях.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    events = relationship("Event", back_populates="owner")

class Event(Base):
    """
    Модель мероприятия. Хранит всю информацию о конкретном событии.
    """
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True) # Описание может быть необязательным
    start_time = Column(DateTime)
    location = Column(String, nullable=False)

    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="events")

class Ticket(Base):
    """
    Модель билета
    """
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    registration_time = Column(DateTime, default=datetime.datetime.now)

    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    participant_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    event = relationship("Event", back_populates="tickets")
    participant = relationship("User", back_populates="tickets")