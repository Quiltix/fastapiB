# app/main.py

from fastapi import FastAPI

from app.db.database import engine
from app.db.models import Base

# Создаем экземпляр FastAPI
app = FastAPI()


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("startup")
async def on_startup():
    await create_db_and_tables()

# Подключаем роутеры (пока закомментировано)
# Когда мы создадим app/routers/users.py и app/routers/events.py,
# мы раскомментируем эти строки.
# app.include_router(users.router)
# app.include_router(events.router)