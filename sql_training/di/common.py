"""
:mod:`container` -- Dependency Injection (DI) контейнер
===================================
.. moduleauthor:: ilya Barinov <i-barinov@it-serv.ru>
"""

from logging import Logger

from dependency_injector import containers, providers

from sql_training.utils.logger import extend_log_record, get_logger
from sql_training.utils.logger.handlers import StderrHandler, StdoutHandler


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

    config = providers.Configuration()

    logger = providers.Resource(
        init_logger,
        loglevel=config.loglevel,
        app_name=config.app_name,
        app_ver=config.app_ver,
    )
