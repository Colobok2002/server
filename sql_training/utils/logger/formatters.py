"""
:mod:`formatters` -- docs
===================================
.. moduleauthor:: ilya Barinov <i-barinov@it-serv.ru>
"""

import re
from logging import Formatter, LogRecord

__all__ = (
    "DefaultFormatter",
    "SensitiveFormatter",
)


class SensitiveFormatter(Formatter):
    """Formatter that removes sensitive information in urls."""

    @staticmethod
    def _filter(s: str) -> str:
        return re.sub(r":\/\/(.*?)\@", r"://", s)

    def format(self, record: LogRecord) -> str:
        original = super().format(record)
        return self._filter(original)


DefaultFormatter = SensitiveFormatter(
    "%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
)
