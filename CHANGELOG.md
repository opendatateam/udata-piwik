# Changelog

## 1.3.1 (2018-11-05)

- Ensure JS goals handling waits for `uData` object to be present [#91](https://github.com/opendatateam/udata-piwik/pull/91)

## 1.3.0 (2018-10-11)

- Advanced search tracking: display results count and categories (datasets, reuses, organizations) [#88](https://github.com/opendatateam/udata-piwik/pull/88)
- Lower jobs piriority to `low` [#90](https://github.com/opendatateam/udata-piwik/pull/90)
- Depends on `udata>=1.6.1`

## 1.2.0 (2018-06-06)

- Simpler and more reliable metrics computation [#54](https://github.com/opendatateam/udata-piwik/pull/54)

## 1.1.1 (2018-03-15)

- Handle multiple resources for same url [#49](https://github.com/opendatateam/udata-piwik/pull/49)

## 1.1.0 (2018-03-13)

- Refactor `counter.handle_downloads` - fix [#1421](https://github.com/opendatateam/udata/issues/1421)
- Switch to `flask-cli` and endpoint-based commands (requires `udata>=1.3`) [#33](https://github.com/opendatateam/udata-piwik/pull/33)
- Expose the new `udata.tasks` endpoint [#39](https://github.com/opendatateam/udata-piwik/pull/39)
- Expose the new `udata.views` endpoint [#41](https://github.com/opendatateam/udata-piwik/pull/41)
- Add content tracking options in configuration paramaters [#42](://github.com/opendatateam/udata-piwik/pull/42)

## 1.0.2 (2017-12-20)

- Fix version number
- Fix README on pypi

## 1.0.1 (2017-12-20)

- Fix packaging issue

## 1.0.0 (2017-12-19)

- Add (automated) tests against a Piwik instance [#20](https://github.com/opendatateam/udata-piwik/issues/20)
- Handle download count on latest url for (community) resources [#30](https://github.com/opendatateam/udata-piwik/pull/30)

## 0.9.3 (2017-12-11)

- Add a timeout to `analyze()` [#19](https://github.com/opendatateam/udata-piwik/pull/19)

## 0.9.2 (2017-12-11)

- Add a timeout to `track()` [#18](https://github.com/opendatateam/udata-piwik/pull/18)

## 0.9.1 (2017-01-10)

- Fix build and packaging

## 0.9.0 (2017-01-10)

- First published release
