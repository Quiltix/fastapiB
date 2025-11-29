# app/main.py

from fastapi import FastAPI

from app.db.database import engine
from app.db.models import Base
from app.routes.user import router as user_router
from app.routes.event import router as event_router
from app.routes.ticket import router as ticket_router


app = FastAPI()


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("startup")
async def on_startup():
    await create_db_and_tables()


app.include_router(user_router)
app.include_router(event_router)
app.include_router(ticket_router)
