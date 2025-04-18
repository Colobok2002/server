"""
:mod:`app` -- Rest App
===================================
.. moduleauthor:: ilya Barinov <i-barinov@it-serv.ru>
"""

from sql_training import __appname__, __version__
from sql_training.di import APPLICATION_CONFIG
from sql_training.di.rest import RestDI

di = RestDI()

di.config.from_yaml(APPLICATION_CONFIG)
di.config.app_name.from_value(f"{__appname__}")
di.config.app_ver.from_value(__version__)

di.init_resources()
app = di.app()
