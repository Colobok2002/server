"""
:mod:`db` -- Модели для работы с Базой
===================================
.. moduleauthor:: ilya Barinov <i-barinov@it-serv.ru>
"""

from sql_training.models.db import Base


class User(Base):
    """Таблица с пользователями"""

    __tablename__ = "system.user"

    ...
