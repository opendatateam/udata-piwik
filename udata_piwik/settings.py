'''
Default settings for udata-piwik
'''
# Piwik/Matomo instance URL
PIWIK_URL = None

# Scheme used to make Piwik/Matomo API calls (http or https)
PIWIK_SCHEME = 'http'

# Piwik/Matomo site IDs
# this site will track front (template) events
PIWIK_ID_FRONT = 1
# this site will track back (API) events
PIWIK_ID_API = 1

# Authentication token from Piwik/Matomo
PIWIK_AUTH = '<32-chars-auth-token-from-piwik>'

# Piwik/Matomo reporting analyse timeout in seconds
PIWIK_ANALYZE_TIMEOUT = 60 * 5

# Piwik/Matomo tracking submission timeout in seconds
PIWIK_TRACK_TIMEOUT = 60

# Use bulk API calls processing
# NB: if true, you need to schedule the `piwik-bulk-track-api` job
PIWIK_BULK = False
