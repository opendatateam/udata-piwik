# udata-piwik

[![Build status][circleci-badge]][circleci-url]
[![Join the chat at https://gitter.im/opendatateam/udata][gitter-badge]][gitter-url]

This plugin provide integration between [udata][] and [Piwik/Matomo](https://matomo.org/)

## Compatibility

**udata-piwik** requires Python 2.7+ and [udata][].

## Installation

Install [udata][].

Remain in the same virtual environment (for Python) and use the same version of npm (for JS).

Install **udata-piwik**:

```shell
pip install udata-piwik
```

Modify your local configuration file of **udata** (typically, `udata.cfg`) as following:

```python
PLUGINS = ['piwik']
# Piwik/Matomo site IDs
# this site will track front (template) events
PIWIK_ID_FRONT = 1
# this site will track back (API) events
PIWIK_ID_API = 1
PIWIK_SCHEME = 'https'
PIWIK_URL = 'stats.data.gouv.fr'
PIWIK_AUTH = '<32-chars-auth-token-from-piwik>'
# `client.track` method `requests` timeout
PIWIK_TRACK_TIMEOUT = 60  # in seconds
# `client.analyze` method `requests` timeout
PIWIK_ANALYZE_TIMEOUT = 60 * 5  # in seconds
```

### Optional configuration

```python
# Content tracking options. Default: None
#   - 'all': track all impressions
#   - 'visible': track impressions of visible items only (default refresh: 750 ms)
PIWIK_CONTENT_TRACKING = 'visible'
```

## Testing on local env

```shell
$ docker-compose up
$ pip install -r requirements/test.pip
$ pytest
```

[circleci-url]: https://circleci.com/gh/opendatateam/udata-piwik
[circleci-badge]: https://circleci.com/gh/opendatateam/udata-piwik.svg?style=shield
[gitter-badge]: https://badges.gitter.im/Join%20Chat.svg
[gitter-url]: https://gitter.im/opendatateam/udata
[udata]: https://github.com/opendatateam/udata
