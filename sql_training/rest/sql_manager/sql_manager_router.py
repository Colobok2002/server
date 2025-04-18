"""
:mod:`AuthRouter` -- Роутер для авторизации
===================================
.. moduleauthor:: ilya Barinov <i-barinov@it-serv.ru>
"""

from sql_training.models.request import GoodResponse
from sql_training.rest.common import RoutsCommon

__all__ = ("SqlManagerRouter",)


class SqlManagerRouter(RoutsCommon):
    """Роутер для авторизации"""

    def setup_routes(self) -> None:
        """Функция назначения routs"""

        self._router.add_api_route("/ping", self.ping, methods=["GET"])

    def ping(self) -> GoodResponse:
        return self.good_response("Pong")
