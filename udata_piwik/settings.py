# -*- coding: utf-8 -*-
from __future__ import unicode_literals
'''
Default settings for udata-piwik
'''
# Piwik/Matomo instance URL
PIWIK_URL = None

# Scheme used to make Piwik/Matomo API calls (http or https)
PIWIK_SCHEME = 'http'

# Piwik/Matomo site ID
PIWIK_ID = 1

# Authentication token from Piwik/Matomo
PIWIK_AUTH = '<32-chars-auth-token-from-piwik>'

# Piwik/Matomo Goals mapping
# All keys are required and should exists on instance
PIWIK_GOALS = {
    # 'NEW_DATASET': 1,
    # 'NEW_REUSE': 2,
    # 'NEW_FOLLOW': 3,
    # 'SHARE': 4,
    # 'RESOURCE_DOWNLOAD': 5,
    # 'RESOURCE_REDIRECT': 6,
}

# Piwik/Matomo reporting analyse timeout in seconds
PIWIK_ANALYZE_TIMEOUT = 60 * 5

# Piwik/Matomo tracking submission timeout in seconds
PIWIK_TRACK_TIMEOUT = 60

# Use bulk API calls processing
# NB: if true, you need to schedule the `piwik-bulk-track-api` job
PIWIK_BULK = False
