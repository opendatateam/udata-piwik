from udata.settings import Testing


class PiwikSettings(Testing):
    PLUGINS = ['piwik']
    PIWIK_ID_FRONT = 1
    PIWIK_ID_API = 2
    PIWIK_URL = 'localhost:8080'
    PIWIK_SCHEME = 'https'
    PIWIK_AUTH = 'eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'
    # FIXME: this should be taken care of in udata-front
    RESOURCES_SCHEMAGOUVFR_ENABLED = False
