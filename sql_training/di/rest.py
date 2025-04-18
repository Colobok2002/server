"""
:mod:`rest` -- docs
===================================
.. moduleauthor:: ilya Barinov <i-barinov@it-serv.ru>
"""

import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from logging import Logger
from typing import Any, cast

from dependency_injector import containers, providers
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi_offline import FastAPIOffline
from sqlalchemy import create_engine

from sql_training import __version__
from sql_training.di.common import CommonDI
from sql_training.rest.auth.auth_router import AuthRouter
from sql_training.rest.common import RoutsCommon
from sql_training.rest.sql_manager.sql_manager_router import SqlManagerRouter
from sql_training.utils.db_helper import DBHelper
from sql_training.utils.waiting import async_waiting_required_services

__all__ = ("RestDI",)


class CustomFastAPIType(FastAPI):
    """Кастомный тип FastApi чтоб добавить атрибут logger"""

    logger: Logger


def init_rest_app(
    routers: list[type[RoutsCommon]],
    logger: Logger,
    config: dict[str, Any],
) -> FastAPI:
    """
    Инициализация Rest интерфейса


    :return: Экземпляр :class:`FastAPIOffline`
    """

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[Any]:  # noqa: ARG001
        # Ожидание запуска сервисов от которых зависит приложение
        await async_waiting_required_services(config=config)
        yield

    app: CustomFastAPIType = cast(
        CustomFastAPIType, FastAPIOffline(version=__version__, lifespan=lifespan)
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    for router in routers:
        app.include_router(router().router)  # type: ignore

    app.logger = logger

    @app.middleware("http")
    async def timing_middleware(request: Request, call_next: Any) -> Any:
        """Middleware для автоматического замера времени выполнения ВСЕХ маршрутов в FastAPI."""
        start_time = time.time()

        response = await call_next(request)
        duration = time.time() - start_time

        logger.info(
            f"Маршрут {request.url.path} выполнен за {duration:.4f} секунд.",
        )

        return response

    logger.info("Зарегистрированные routs", extra={"routs": str(app.router.routes)})
    return app


def get_db_helper(
    url: str,
    app_name: str,
    pool_size: int | None = None,
    max_overflow: int | None = None,
) -> DBHelper:
    pool_size = pool_size or 5
    max_overflow = max_overflow or 10
    engine = create_engine(
        url,
        pool_pre_ping=True,
        pool_size=pool_size,
        max_overflow=max_overflow,
        connect_args={
            "application_name": app_name,
        },
    )

    return DBHelper(engine=engine)


class RestDI(containers.DeclarativeContainer):
    """DI-контейнер с основными зависимостями"""

    config = providers.Configuration()

    common_di = providers.Container(CommonDI, config=config)

    db_helper = providers.Resource(
        get_db_helper,
        url=config.db.url,
        pool_size=config.db.pool_size,
        max_overflow=config.db.max_overflow,
        app_name=config.app_name,
    )

    auth_router = providers.Singleton(
        AuthRouter,
        prefix="/auth",
        tags=["auth"],
        db_helper=db_helper,
    )

    sql_manager_router = providers.Singleton(
        SqlManagerRouter,
        prefix="/sql-manager",
        tags=["sql-manager"],
        db_helper=db_helper,
    )

    app = providers.Factory(
        init_rest_app,
        config=config,
        routers=[
            auth_router,
            sql_manager_router,
        ],
        logger=common_di.logger,
    )
