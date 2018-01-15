# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest

from datetime import date, timedelta

from click.testing import CliRunner
from udata.commands import cli


@pytest.fixture
def cmd(mocker, app):
    def mock_runner(args):
        runner = CliRunner()
        return runner.invoke(cli, ['piwik'] + args.split())

    # Mock counter to speedup test as it is already tested elsewhere
    mock_runner.counter = mocker.patch('udata_piwik.commands.counter')
    # Avoid to instanciate another app and reuse the app fixture
    mocker.patch.object(cli, 'create_app', return_value=app)
    return mock_runner


def test_command_without_parameters(cmd):
    result = cmd('fill')

    assert result.exit_code == 0, result.output_bytes
    cmd.counter.count_for.assert_called_once_with(date.today())


def test_command_with_start_date(cmd):
    days = 3
    start_date = date.today() - timedelta(days=days)
    result = cmd('fill -s {0:%Y-%m-%d}'.format(start_date))

    assert result.exit_code == 0, result.output_bytes

    assert cmd.counter.count_for.call_count == days + 1

    for delta in range(days + 1):
        param = start_date + timedelta(days=delta)
        cmd.counter.count_for.assert_any_call(param)


def test_command_with_end_date(cmd):
    end_date = date.today() - timedelta(days=3)
    result = cmd('fill -e {0:%Y-%m-%d}'.format(end_date))

    assert result.exit_code == 0, result.output_bytes
    cmd.counter.count_for.assert_called_once_with(end_date)


def test_command_with_start_and_end_date(cmd):
    days = 3
    start_date = date.today() - timedelta(days=days)
    end_date = date.today() - timedelta(days=1)
    result = cmd(
        'fill -s {0:%Y-%m-%d} -e {1:%Y-%m-%d}'.format(start_date, end_date)
    )

    assert result.exit_code == 0, result.output_bytes

    assert cmd.counter.count_for.call_count == days

    for delta in range(days):
        param = start_date + timedelta(days=delta)
        cmd.counter.count_for.assert_any_call(param)
