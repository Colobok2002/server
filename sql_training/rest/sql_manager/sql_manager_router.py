"""
:mod:`AuthRouter` -- Роутер для авторизации
===================================
.. moduleauthor:: ilya Barinov <i-barinov@it-serv.ru>
"""

from sqlalchemy import text

from sql_training.models.request import BadResponse, GoodResponse
from sql_training.rest.common import RoutsCommon

__all__ = ("SqlManagerRouter",)

T = GoodResponse | BadResponse


class SqlManagerRouter(RoutsCommon):
    """Роутер для авторизации"""

    def setup_routes(self) -> None:
        """Функция назначения routs"""
        self._router.add_api_route("/ping", self.ping, methods=["GET"])
        self._router.add_api_route("/test-sql-engect", self.test_sql_engect, methods=["GET"])

    def ping(self) -> GoodResponse:
        """PIng -pong"""
        return self.good_response("Pong")

    def test_sql_engect(self) -> T:
        """Тестирование правд доступа"""
        with self.db_helper.sessionmanager() as session:
            result = session.execute(text("SELECT current_user")).fetchone()

        return self.good_response(message=result[0])  # type: ignore
