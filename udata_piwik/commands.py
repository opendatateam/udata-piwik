# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from datetime import date, timedelta

from udata.commands import submanager

from .counter import counter


log = logging.getLogger(__name__)


m = submanager('piwik',
    help='Piwik related operations',
    description='Handle all Piwik related operations'
)


def parse_date(string):
    if string:
        parts = [int(s) for s in string.strip().split('-')]
        return date(*parts)


@m.command
def fill(start=None, end=None):
    '''Fill the piwik metrics'''
    end = parse_date(end) or date.today()
    start = parse_date(start) or end
    log.info('Loading metrics from {start} to {end}'.format(start=start, end=end))

    current_date = start

    while current_date <= end:
        log.info(str(current_date))
        counter.count_for(current_date)
        current_date += timedelta(days=1)
