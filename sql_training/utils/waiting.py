"""
:mod:`waiting` -- Ожидание запуска служб от которых зависит работа приложения
===================================
.. moduleauthor:: ilya Barinov <i-barinov@it-serv.ru>
"""

from asyncio import get_event_loop
from typing import Any
from urllib.parse import ParseResult, urlparse

from sqlalchemy.engine.url import make_url
from wait_for_it.wait_for_it import _connect_all_parallel_async

__all__ = (
    "async_waiting_required_services",
    "waiting_required_services",
)


async def async_waiting_required_services(
    config: dict[str, Any],
    timeout: int = 15,
) -> None:
    """
    Ожидание запуска служб в зависимости от типа запуска и объявленных в конфигурации служб.

    В зависимости от типа запуска различаются службы, от которых зависит приложение.

    Если приложение запускается в качестве REST API, то оно зависит от следующих служб:
     * Сервер RabbitMQ - `celery.broker`;
     * Сервер Redis - `celery.backend`;
     * Контроллер уведомлений - `notif.facade.url` (если задан в конфигурации).

    Если приложение запускается в режиме работника Celery, оно зависит от следующих дополнительных
    служб:
     * API, через который запускаются задачи;
     * База данных OmniUS - `db.url`;
     * Сервис миграции БД - `db.migration.url`;
     * Сервер кеширования Redis - `cache.redis.url`;
     * Планировщик задач - `scheduler` (если задан в конфигурации);
     * Фасад - `cache.facade.url` (если задан в конфигурации).

    В случае, если по истечении таймаута указанные службы не будут запущены, приложение завершится
    ошибкой.

    :param config: Конфигурация
    :param execution_type: Режим запуска
    :param timeout: Таймаут ожидания
    """
    services = set()

    # fast_stream_broker = urlparse(config.get("fast_stream")["broker"])  # type: ignore
    # services.add(f"{fast_stream_broker.hostname}:{get_service_port(fast_stream_broker)}")

    # if (
    #     config.get("notif")
    #     and config.get("notif").get("facade")
    #     and config.get("notif").get("facade").get("url")
    # ):
    #     notify_ctrl = urlparse(config.get("notif")["facade"]["url"])
    #     services.add(f"{notify_ctrl.hostname}:{get_service_port(notify_ctrl)}")

    services.add(get_host_and_port_from_sqlalchemy_url(config.get("db")["url"]))  # type: ignore

    await _connect_all_parallel_async(services, timeout)


def waiting_required_services(config: dict[str, Any], timeout: int = 15) -> None:
    """
    Синхронное ожидание запуска служб (только для ExecutionType.worker)

    :param config: Конфигурация
    :param timeout: Таймаут ожидания
    """
    loop = get_event_loop()
    loop.run_until_complete(
        async_waiting_required_services(
            config=config,
            timeout=timeout,
        )
    )


def get_service_port(parse_res: ParseResult) -> int | None:
    """Получение порта по-умолчанию для различных схем"""
    if parse_res.port is None:
        if parse_res.scheme == "http":
            return 80
        if parse_res.scheme == "https":
            return 443
        if parse_res.scheme == "redis":
            return 6379
        if parse_res.scheme == "admin":
            return 5672

    return parse_res.port


def get_host_and_port_from_sqlalchemy_url(url: str) -> str:
    """Получение имени сервера и порта из url SQLAlchemy"""
    url = make_url(url)

    return f"{url.host}:{url.port}"
