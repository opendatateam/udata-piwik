from flask import render_template, Blueprint

from udata_gouvfr.frontend import template_hook

blueprint = Blueprint('piwik', __name__, template_folder='templates')


@template_hook('footer.snippets')
def render_piwik_snippet(ctx):
    return render_template('piwik.html', **ctx)
