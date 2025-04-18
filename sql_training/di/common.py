"""
:mod:`container` -- Dependency Injection (DI) контейнер
===================================
.. moduleauthor:: ilya Barinov <i-barinov@it-serv.ru>
"""

from logging import Logger

from dependency_injector import containers, providers
from pydantic import Field, field_validator, ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict

from sql_training import __appname__, __version__
from sql_training.utils.logger import extend_log_record, get_logger
from sql_training.utils.logger.handlers import StderrHandler, StdoutHandler


class Settings(BaseSettings):
    """Настройки приложения"""

    LOG_LEVEL: str = "INFO"

    POSTGRES_USER: str = Field()
    POSTGRES_PASSWORD: str = Field()
    POSTGRES_DB: str = Field()
    POSTGRES_HOST: str = Field()
    POSTGRES_PORT: int = Field()

    DB_URL: str | None = None

    @field_validator("DB_URL", mode="before")
    @staticmethod
    def assemble_db_connection(_v: str, values: ValidationInfo) -> str:
        """Собирает URL для подключения к PostgreSQL."""
        return (
            f"postgresql://{values.data['POSTGRES_USER']}:{values.data['POSTGRES_PASSWORD']}@"
            f"{values.data['POSTGRES_HOST']}:{values.data['POSTGRES_PORT']}/{values.data['POSTGRES_DB']}"
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow",
    )


def init_logger(
    loglevel: str,
    app_name: str,
    app_ver: str,
    logstash_index: str | None = None,
) -> Logger:
    """
    Инициализация логгера

    :param loglevel: Уровень логирования
    :param app_name: Наименование приложения
    :param app_ver: Версия приложения
    :param logstash_index: Индекс, в который будет выгружен лог
    """
    if not logstash_index:
        logstash_index = "pybeat"

    logger = get_logger(app_name)

    extend_log_record(app_name=app_name, app_ver=app_ver)

    logger.setLevel(level=loglevel.upper())

    logger.addHandler(StdoutHandler())
    logger.addHandler(StderrHandler())

    return logger


class CommonDI(containers.DeclarativeContainer):
    """Базовый DI-контейнер"""

    settings = providers.Singleton(Settings)
    logger = providers.Singleton(
        init_logger,
        loglevel=settings.provided.LOG_LEVEL,
        app_name=__appname__,
        app_ver=__version__,
    )
