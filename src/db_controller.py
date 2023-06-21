import datetime

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, relationship, selectinload
from sqlalchemy import Column, Integer, String, ForeignKey, select, Boolean, func
from sqlalchemy.orm import declarative_base



engine = create_async_engine('sqlite+aiosqlite:///data/database.db')
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    tg_id = Column(String(50), nullable=True)
    name = Column(String(50), nullable=True)
    role = Column(String(50), nullable=True, default="user")
    cars = relationship('Car', back_populates='author')
    subscription = relationship('Subscription', back_populates='user')


class Subscription(Base):
    __tablename__ = 'subscriptions'
    id = Column(Integer, primary_key=True)
    subscriber_tg_id = Column(String(50), ForeignKey('users.tg_id'))
    subscription_random = Column(Boolean, default=False)
    subscription_daily = Column(Boolean, default=False)
    subscription_time = Column(String(50))
    user = relationship('User', back_populates='subscription')


class Car(Base):
    __tablename__ = 'cars'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    source = Column(String(100))
    source_key = Column(String(100), nullable=True)
    author_tg_id = Column(String(50), ForeignKey('users.tg_id'))
    author = relationship("User", back_populates="cars")
    stats = relationship("CarStats", back_populates="car")


class CarStats(Base):
    __tablename__ = 'car_stats'
    id = Column(Integer, primary_key=True)
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    dislikes = Column(Integer, default=0)
    creation_time = Column(String(50))
    car_id = Column(Integer, ForeignKey('cars.id'))
    car = relationship("Car", back_populates="stats")


async def get_car_by_id(car_id):
    async with async_session() as session:
        response = await session.execute(select(Car).filter(Car.id == car_id))
        car = response.scalars().first()
        return car


async def get_cars_by_name(car_name):
    async with async_session() as session:
        response = await session.execute(select(Car).filter(func.lower(Car.name).ilike(f'%{car_name.lower()}%')))
        cars = response.scalars().all()
        return cars


async def get_last_id():
    async with async_session() as session:
        response = await session.execute(select(Car).order_by(Car.id.desc()).limit(1))
        car = response.scalars().first()
        return car.id


async def add_car(car_name, author_tg_id, source, source_key=None):
    async with async_session() as session:
        new_car = Car(
            name=car_name,
            source=source,
            source_key=source_key,
            author_tg_id=author_tg_id
        )
        session.add(new_car)
        await session.commit()

        new_car_stats = CarStats(
            creation_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            car_id=new_car.id
        )
        session.add(new_car_stats)

        await session.commit()
        return new_car


async def create_user(message):
    async with async_session() as session:
        user = User(
            name=message.from_user.username,
            tg_id=message.from_user.id
        )
        session.add(user)
        await session.commit()
        return user


async def give_admin_role(user_id):
    async with async_session() as session:
        user = await session.execute(select(User).filter(User.tg_id == user_id))
        user = user.scalars().first()
        user.role = "admin"
        await session.merge(user)
        await session.commit()


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def add_like(car_id):
    async with async_session() as session:
        car = await session.execute(select(CarStats).filter(CarStats.id == car_id))
        car = car.scalars().first()
        car.likes += 1
        await session.merge(car)
        await session.commit()


async def add_dislike(car_id):
    async with async_session() as session:
        car = await session.execute(select(CarStats).filter(CarStats.id == car_id))
        car = car.scalars().first()
        car.dislikes += 1
        await session.merge(car)
        await session.commit()


async def add_views(car_id):
    async with async_session() as session:
        car = await session.execute(select(CarStats).filter(CarStats.id == car_id))
        car = car.scalars().first()
        car.views += 1
        await session.merge(car)
        await session.commit()


async def get_stats(car_id):
    async with async_session() as session:
        car = await session.execute(select(CarStats).filter(CarStats.id == car_id))
        car = car.scalars().first()
        return car.likes, car.dislikes, car.views
