import os

from udata.settings import Testing


class PiwikSettings(Testing):
    PLUGINS = ['piwik']
    PIWIK_ID_FRONT = 1
    PIWIK_ID_API = 2
    PIWIK_URL = os.environ.get('PIWIK_URL', 'localhost:8080')
    PIWIK_AUTH = 'eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'
    PIWIK_GOALS = {
        'NEW_DATASET': 1,
        'NEW_REUSE': 2,
        'NEW_FOLLOW': 3,
        'SHARE': 4,
        'RESOURCE_DOWNLOAD': 5,
        'RESOURCE_REDIRECT': 6,
    }
    METRICS_DSN = {
        'host': 'localhost',
        'port': '8086',
        'username': 'piwik',
        'password': 'piwik',
        'database': 'piwik_db'
    }
