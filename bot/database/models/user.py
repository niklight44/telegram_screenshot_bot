from sqlalchemy import Column, Integer, VARCHAR, DATE

from bot.database.models.base import BaseModel


class User(BaseModel):
    """
    Модель данных пользователя
    """
    __tablename__ = 'users'

    user_id = Column(Integer, unique=True, nullable=False, primary_key=True)

    name = Column(VARCHAR(36))
    surname = Column(VARCHAR(36))
    email = Column(VARCHAR(100))
    phone = Column(VARCHAR(100))
    birthday = Column(DATE)

    def __str__(self):
        return f"User ID: {self.user_id} \n " \
               f"Name: {self.name} \n" \
               f"Surname: {self.surname} \n" \
               f"Email: {self.email} \n" \
               f"Phone: {self.phone} \n" \
               f"Birthday: {self.birthday}"