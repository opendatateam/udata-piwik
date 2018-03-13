# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import date

from flask import _app_ctx_stack
from werkzeug.routing import RequestRedirect
from werkzeug.urls import url_parse


class RouteNotFound(Exception):
    pass


def route_from(url, method=None):
    appctx = _app_ctx_stack.top
    if appctx is None:
        raise RuntimeError('Attempted to match a URL without the '
                           'application context being pushed. This has to be '
                           'executed when application context is available.')

    url_adapter = appctx.url_adapter
    if url_adapter is None:
        raise RuntimeError('Application was not able to create a URL '
                           'adapter for request independent URL matching. '
                           'You might be able to fix this by setting '
                           'the SERVER_NAME config variable.')
    parsed_url = url_parse(url)
    if parsed_url.netloc is not "" and parsed_url.netloc != url_adapter.server_name:
        raise RouteNotFound

    try:
        url_adapter.path_info = url_adapter.path_info or parsed_url.path
        url_adapter.query_args = url_adapter.query_args or parsed_url.decode_query()
        return url_adapter.match(parsed_url.path, method)
    except RequestRedirect as re:
        return route_from(re.new_url, method)


def is_today(day):
    today = date.today()
    if isinstance(day, basestring):
        return day == today.isoformat()
    else:
        return day == today
