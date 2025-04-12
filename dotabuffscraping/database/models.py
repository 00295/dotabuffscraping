from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import sessionmaker, relationship, Mapped, mapped_column
from sqlalchemy import Column, Integer, String, ForeignKey, select

# Создаем таблицу postgres
from os import getenv
from dotenv import load_dotenv
# зашружаем dotenv
load_dotenv()
DATABASE_URL = f"postgresql+asyncpg://{getenv("DB_USER")}:{getenv("DB_PASS")}@{getenv("DB_HOST")}:{getenv("DB_PORT")}/{getenv("DB_NAME")}"
#DATABASE_URL = f"postgresql+asyncpg://postgres:postgres@localhost:5432/dotabuffparcer"
# создаем движок базы данных и сесию
engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# создаем родительский для всех остальних таблиц клас
class Base(DeclarativeBase,AsyncAttrs):
    def __repr__(self):
        cols = []
        for col in self.__table__.columns.keys():
            cols.append(f"{col}={getattr(self, col)}")              #Штука для красивого вывода в консоль
        return f"<{self.__class__.__name__} {",".join(cols)}>"


# Добавляем таблицы с relationship(связей между таблицами)
class Hero(Base):
    __tablename__ = "heroes"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    characteristics: Mapped[str] = mapped_column()
    counters: Mapped[list["Counter"]] = relationship(back_populates="hero")


class Counter(Base):
    __tablename__ = "counters"
    id: Mapped[int] = mapped_column(primary_key=True)
    # Внешний ключ
    hero_id: Mapped[int] = mapped_column(ForeignKey("heroes.id"))
    counter_name: Mapped[str] = mapped_column()
    position: Mapped[str] = mapped_column()
    hero: Mapped["Hero"] = relationship(back_populates="counters")

#Создаем таблици
async def async_main():
    async with engine.begin() as conn:
        print(1)
        #Удаляем старую и создаем новую
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)