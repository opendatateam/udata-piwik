import os

from udata.settings import Testing


class PiwikSettings(Testing):
    PLUGINS = ['piwik', 'metrics']
    PIWIK_ID_FRONT = 1
    PIWIK_ID_API = 2
    PIWIK_URL = os.environ.get('PIWIK_URL', 'localhost:8080')
    PIWIK_AUTH = 'eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'
    METRICS_DSN = {
        'host': 'localhost',
        'port': '8086',
        'username': 'piwik',
        'password': 'piwik',
        'database': 'piwik_db'
    }
    # FIXME: this should be taken care of in udata-gouvfr
    RESOURCES_SCHEMAGOUVFR_ENABLED = False
