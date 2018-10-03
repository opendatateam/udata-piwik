# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from flask import render_template, Blueprint
from jinja2 import contextfunction

from udata.frontend import footer_snippet

blueprint = Blueprint('piwik', __name__, template_folder='templates')


@footer_snippet
@contextfunction
def render_piwik_snippet(ctx):
    return render_template('piwik.html', **ctx)
