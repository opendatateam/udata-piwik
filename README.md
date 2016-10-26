uData-piwik
===========

[![Build status][circleci-badge]][circleci-url]
[![Join the chat at https://gitter.im/opendatateam/udata][gitter-badge]][gitter-url]

This plugin provide integration between uData and Piwik

Compatibility
-------------

**udata-piwik** requires Python 2.7+ and [uData][].


Installation
------------

Install [uData][].

Remain in the same virtual environment (for Python) and use the same version of npm (for JS).

Install **udata-piwik**:

```shell
pip install udata-piwik
```

Modify your local configuration file of **udata** (typically, `udata.cfg`) as following:

```python
PLUGINS = ['piwik']
```

[circleci-url]: https://circleci.com/gh/opendatateam/udata-piwik
[circleci-badge]: https://circleci.com/gh/opendatateam/udata-piwik.svg?style=shield
[gitter-badge]: https://badges.gitter.im/Join%20Chat.svg
[gitter-url]: https://gitter.im/opendatateam/udata
[uData]: https://github.com/opendatateam/udata
