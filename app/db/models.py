import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    # Модель пользователя.
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    banned = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)

    created_events = relationship("Event", back_populates="owner")
    tickets = relationship("Ticket", back_populates="participant")


class Event(Base):
    # Модель мероприятия.
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    start_time = Column(DateTime(timezone=True))
    location = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="created_events")
    tickets = relationship("Ticket", back_populates="event", cascade="all, delete-orphan")


class Ticket(Base):
    # Модель билета.
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    participant_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    event = relationship("Event", back_populates="tickets")
    participant = relationship("User", back_populates="tickets")