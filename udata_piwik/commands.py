import logging

import click

from datetime import date, timedelta

from udata.commands import cli, success

from udata_piwik.counter import counter
from udata_piwik.metrics import update_metrics_from_backend


log = logging.getLogger(__name__)


@cli.group()
def piwik():
    '''Piwik related operations'''
    pass


class DateParamType(click.ParamType):
    name = 'date'

    def convert(self, value, param, ctx):
        if not value:
            return
        if isinstance(value, date):
            return value
        try:
            parts = [int(s) for s in value.strip().split('-')]
            return date(*parts)
        except ValueError:
            self.fail('%s is not a valid date' % value, param, ctx)


DATE = DateParamType()


@piwik.command()
@click.option('-s', '--start', type=DATE, default=None,
              help='The start of the period to fill')
@click.option('-e', '--end', type=DATE, default=date.today,
              help='The end of the period to fill')
def fill(start, end):
    '''Fill the piwik metrics'''
    start = start or end
    log.info('Loading metrics from {start} to {end}'.format(start=start, end=end))

    current_date = start

    while current_date <= end:
        log.info('Processing %s', current_date)
        counter.count_for(current_date)
        current_date += timedelta(days=1)

    success('Loaded all metrics for the period')


@piwik.command()
def update_metrics():
    '''Update instance's metrics from backend'''
    update_metrics_from_backend()
