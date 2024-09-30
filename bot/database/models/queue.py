from sqlalchemy import Column, Integer, ForeignKey, BigInteger
from bot.database.models.base import BaseModel
from .user import User


class UserQueue(BaseModel):
    """
    Модель данных для пользователя
    """
    __tablename__ = "user_queue"

    id = Column(Integer, unique=True, nullable=False, primary_key=True)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)  # Reference to User's id column
