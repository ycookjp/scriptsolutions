'''Application module.

Copyright ycookjp

https://github.com/ycookjp/

'''
from .utils import init_logging

from django.apps import AppConfig
import yaml
import os

_config_file = os.path.join(os.path.dirname(__file__), 'config.yml')
with open(_config_file, 'r', encoding='utf-8') as file:
    _config = yaml.load(file, Loader=yaml.SafeLoader)
print(_config)
init_logging(stream=_config['logging'].get('stream'),
             filename=_config['logging'].get('filename'),
            level=_config['logging'].get('level'))

class MycalendarConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mycalendar'
