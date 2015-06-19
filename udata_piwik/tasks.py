# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from datetime import date, timedelta
from udata.tasks import connect, job
from udata.api.signals import on_api_call

import udata_piwik
from .counter import counter


log = logging.getLogger(__name__)


@job('piwik-current-metrics')
def piwik_current_metrics(self):
    '''Fetch piwik metrics for the current day'''
    day = date.today()

    self.log.info('Loading Piwik metrics for today ({day})'.format(day=day))

    counter.count_for(day)


@job('piwik-yesterday-metrics')
def piwik_yesterday_metrics(self):
    '''Bump piwik daily metrics for yesterday'''
    day = date.today() - timedelta(days=1)

    self.log.info('Bump Piwik metrics for {day}'.format(day=day))

    counter.count_for(day)


@connect(on_api_call)
def piwik_track_url(url, **params):
    '''Track a URL into Piwik.'''
    log.debug('Sending to piwik: {url}'.format(url=url))
    udata_piwik.track(url, **params)
