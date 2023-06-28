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
    subscription_time = Column(String(50), default="10:00")
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


async def get_cars_by_time(time):
    async with async_session() as session:
        response = await session.execute(select(CarStats).filter(CarStats.creation_time > time))
        cars_stats = response.scalars().all()
        cars = []
        for car_stats in cars_stats:
            response = await session.execute(select(Car).filter(Car.id == car_stats.car_id))
            car = response.scalars().first()
            cars.append(car)
        return cars

async def add_subscriber(tg_id):
    async with async_session() as session:
        new_subscriber = Subscription(
            subscriber_tg_id=tg_id
        )
        session.add(new_subscriber)
        await session.commit()


async def check_subscriptions(tg_id):
    async with async_session() as session:
        sub = await session.execute(select(Subscription).filter(Subscription.subscriber_tg_id == tg_id))
        sub = sub.scalars().first()
        if sub is not None:
            return sub.subscription_daily, sub.subscription_random
        else:
            return False, False


async def check_subbed(tg_id):
    async with async_session() as session:
        sub = await session.execute(select(Subscription).filter(Subscription.subscriber_tg_id == tg_id))
        sub = sub.scalars().first()
        if sub is None:
            return False
        else:
            return True


async def time_change(tg_id, time):
    async with async_session() as session:
        sub = await session.execute(select(Subscription).filter(Subscription.subscriber_tg_id == tg_id))
        sub = sub.scalars().first()
        sub.subscription_time = time
        await session.merge(sub)
        await session.commit()


async def get_sub_time(tg_id):
    async with async_session() as session:
        sub = await session.execute(select(Subscription).filter(Subscription.subscriber_tg_id == tg_id))
        sub = sub.scalars().first()
        return sub.subscription_time


async def sub_daily_change(tg_id):
    async with async_session() as session:
        sub = await session.execute(select(Subscription).filter(Subscription.subscriber_tg_id == tg_id))
        sub = sub.scalars().first()
        sub.subscription_daily = not sub.subscription_daily
        await session.merge(sub)
        await session.commit()


async def sub_random_change(tg_id):
    async with async_session() as session:
        sub = await session.execute(select(Subscription).filter(Subscription.subscriber_tg_id == tg_id))
        sub = sub.scalars().first()
        sub.subscription_random = not sub.subscription_random
        await session.merge(sub)
        await session.commit()


async def sub_time_change(tg_id, time):
    async with async_session() as session:
        sub = await session.execute(select(Subscription).filter(Subscription.subscriber_tg_id == tg_id))
        sub = sub.scalars().first()
        sub.subscription_time = time
        await session.merge(sub)
        await session.commit()


async def get_subs_by_time(time):
    async with async_session() as session:
        subs = await session.execute(select(Subscription).filter(Subscription.subscription_time == time))
        subs = subs.scalars().all()
        return subs



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


async def get_cars_by_tg_id(tg_id):
    async with async_session() as session:
        response = await session.execute(select(Car).filter(Car.author_tg_id == tg_id))
        cars = response.scalars().all()
        return cars


async def get_last_id():
    async with async_session() as session:
        response = await session.execute(select(Car).order_by(Car.id.desc()).limit(1))
        car = response.scalars().first()
        return car.id


async def get_stats_by_tg_id(tg_id):
    cars = await get_cars_by_tg_id(tg_id)
    likes = 0
    dislikes = 0
    views = 0
    async with async_session() as session:
        for car in cars:
            car_stats = await session.execute(select(CarStats).filter(CarStats.id == car.id))
            car_stats = car_stats.scalars().first()
            likes = likes + car_stats.likes
            dislikes = dislikes + car_stats.dislikes
            views = views + car_stats.views
    return likes, dislikes, views


async def get_top_10_stats_by_likes():
    async with async_session() as session:
        response = await session.execute(select(CarStats).order_by(CarStats.likes.desc()).limit(10))
        cars = response.scalars().all()
        return cars


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


async def delete_car(car_id):
    async with async_session() as session:
        car = await session.execute(select(Car).filter(Car.id == car_id))
        car = car.scalars().first()
        await session.delete(car)
        await session.commit()


# async def get_user_stats():
#     async with async_session() as session:
#
#     pass
