# Changelog

## Current (in progress)

- Ensure compatibility with udata-front and removed goals mechanism [#245](https://github.com/opendatateam/udata-piwik/pull/245)

## 2.1.4 (2021-05-06)

- Pin influx docker image version to prevent usign Influx v2 [#239](https://github.com/opendatateam/udata-piwik/pull/239)

## 2.1.3 (2021-05-05)

- Fix noscript img protocol [#215](https://github.com/opendatateam/udata-piwik/pull/215)
- Add exception raise when analyze's API call fails [#230](https://github.com/opendatateam/udata-piwik/pull/230)

## 2.1.2 (2020-07-03)

- Add specific query for each model metrics [#203](https://github.com/opendatateam/udata-piwik/pull/203)

## 2.1.1 (2020-05-20)

- Remove object's id in error log message in order to have a cleaner message [#195](https://github.com/opendatateam/udata-piwik/pull/195)

## 2.1.0 (2020-05-12)

- Changed metrics system [#185](https://github.com/opendatateam/udata-piwik/pull/185):
  - Metrics are now stored into InfluxDB before being injected in udata's objects
  - Udata piwik accesses influxDB throught [udata-metrics](https://github.com/opendatateam/udata-metrics)
  - The periodic job `piwik-update-metrics` needs to be scheduled in addition to existing jobs, in order to retrieve the views metrics in udata's objects
  - The command `update-metrics` was added to trigger the metrics injection manually

## 2.0.2 (2020-04-24)

- [fix] Do not expect a json response from tracking api [#192](https://github.com/opendatateam/udata-piwik/pull/190)

## 2.0.1 (2020-04-07)

- Do not expect a json response from tracking api [#190](https://github.com/opendatateam/udata-piwik/pull/190)

## 2.0.0 (2020-03-11)

- Migrate to python3 🐍 [#68](https://github.com/opendatateam/udata-piwik/pull/68)
- Migrate footer snippet to the new `footer.snippets` hook [#157](https://github.com/opendatateam/udata-piwik/pull/157)

## 1.5.1 (2019-12-31)

- Fix JS syntax when subscribing to goals [#174](https://github.com/opendatateam/udata-piwik/pull/174)

## 1.5.0 (2019-12-30)

- Independant Matomo site ids for front and api tracking :warning: breaking change, you need to set `PIWIK_ID_FRONT` and `PIWIK_ID_API` in settings (they can be the same) [#173](https://github.com/opendatateam/udata-piwik/pull/173)

## 1.4.2 (2019-12-13)

- Improve detect_by_url error handling [#171](https://github.com/opendatateam/udata-piwik/pull/171)

## 1.4.1 (2019-05-15)

- Fix bulk handling of unicode URLs [#139](https://github.com/opendatateam/udata-piwik/pull/139)

## 1.4.0 (2019-03-27)

- Consolidate and expose default settings [#119](https://github.com/opendatateam/udata-piwik/pull/119)
- Process API calls in bulk [#120](https://github.com/opendatateam/udata-piwik/pull/120)

## 1.3.2 (2019-01-14)

- Add `PIWIK_SCHEME` config support [#104](https://github.com/opendatateam/udata-piwik/pull/104)

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
