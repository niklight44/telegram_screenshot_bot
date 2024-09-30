from sqlalchemy import Column, Integer, VARCHAR, DATE, BigInteger

from bot.database.models.base import BaseModel


class User(BaseModel):
    """
    Модель данных пользователя
    """
    __tablename__ = 'users'

    id = Column(Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)

    name = Column(VARCHAR(36))
    surname = Column(VARCHAR(36))
    email = Column(VARCHAR(100))
    phone = Column(VARCHAR(100))
    birthday = Column(DATE)
    chat_id = Column(VARCHAR(50))

    def __str__(self):
        return f"User ID: {self.id} \n " \
               f"Name: {self.name} \n" \
               f"Surname: {self.surname} \n" \
               f"Email: {self.email} \n" \
               f"Phone: {self.phone} \n" \
               f"Birthday: {self.birthday}"