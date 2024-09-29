from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import sessionmaker


def get_session_maker(engine: AsyncEngine) -> sessionmaker:
    """This will be used for asynchronous sessions for interacting with database"""
    return sessionmaker(engine, class_=AsyncSession)
