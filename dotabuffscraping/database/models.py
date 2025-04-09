from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import sessionmaker, relationship, Mapped
from sqlalchemy import Column, Integer, String, ForeignKey, select

# Создаем таблицу postgres
DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/dotabuffparcer"
# создаем движок базы данных и сесию
engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase,AsyncAttrs):
    def __repr__(self):
        cols = []
        for col in self.__table__.columns.keys():
            cols.append(f"{col}={getattr(self, col)}")
        return f"<{self.__class__.__name__} {",".join(cols)}>"


# Добавляем таблицы с relationship(связей между таблицами)
class Hero(Base):
    __tablename__ = "heroes"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    characteristics = Column(String)
    counters = relationship("Counter", back_populates="hero")


class Counter(Base):
    __tablename__ = "counters"
    id = Column(Integer, primary_key=True)
    # Внешний ключ
    hero_id = Column(Integer, ForeignKey("heroes.id"))
    counter_name = Column(String)
    position = Column(String)
    hero = relationship("Hero", back_populates="counters")

#Создаем таблици
async def async_main():
    async with engine.begin() as conn:
        print(1)
        #Временно!!!! Убирае их
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)