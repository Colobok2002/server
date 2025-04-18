"""
:mod:`di` -- Dependency injection
===================================
.. moduleauthor:: ilya Barinov <i-barinov@it-serv.ru>
"""

from os import environ, path

__all__ = ("APPLICATION_CONFIG",)

config_path = path.join(path.dirname(__file__), "config")


APPLICATION_CONFIG = environ.get("APPLICATION_CONFIG", path.join(config_path, "config.yml"))
