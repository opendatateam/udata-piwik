# uData-piwik

[![Build status][circleci-badge]][circleci-url]
[![Join the chat at https://gitter.im/opendatateam/udata][gitter-badge]][gitter-url]

This plugin provide integration between uData and Piwik

## Compatibility

**udata-piwik** requires Python 2.7+ and [uData][].

## Installation

Install [uData][].

Remain in the same virtual environment (for Python) and use the same version of npm (for JS).

Install **udata-piwik**:

```shell
pip install udata-piwik
```

Modify your local configuration file of **udata** (typically, `udata.cfg`) as following:

```python
PLUGINS = ['piwik']
# Tracked site id in Piwik
PIWIK_ID = 1
PIWIK_URL = 'stats.data.gouv.fr'
PIWIK_AUTH = '<32-chars-auth-token-from-piwik>'
# Mapping of piwik goals {'<name_in_udata>': <id_in_piwik>}
# All keys are required
PIWIK_GOALS = {
    'NEW_DATASET': 1,
    'NEW_REUSE': 2,
    'NEW_FOLLOW': 3,
    'SHARE': 4,
    'RESOURCE_DOWNLOAD': 5,
    'RESOURCE_REDIRECT': 6,
}
# `client.track` method `requests` timeout
PIWIK_TRACK_TIMEOUT = 60  # in seconds
# `client.analyze` method `requests` timeout
PIWIK_ANALYZE_TIMEOUT = 60 * 5  # in seconds
```

## Testing on local env

First, clone the [udata-piwik-docker] repository and run `docker-compose up`.

Then run:

```
$ pip install -r requirements/test.pip
$ pytest
```

[udata-piwik-docker]: https://github.com/opendatateam/udata-piwik-docker
[circleci-url]: https://circleci.com/gh/opendatateam/udata-piwik
[circleci-badge]: https://circleci.com/gh/opendatateam/udata-piwik.svg?style=shield
[gitter-badge]: https://badges.gitter.im/Join%20Chat.svg
[gitter-url]: https://gitter.im/opendatateam/udata
[uData]: https://github.com/opendatateam/udata
