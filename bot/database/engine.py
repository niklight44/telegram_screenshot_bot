from typing import Union

from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import create_async_engine as _create_async_engine


def create_async_engine(url: Union[URL, str]) -> AsyncEngine:
    """Creates async engine with specific parameters"""
    return _create_async_engine(url=url, echo=True, pool_pre_ping=True)


