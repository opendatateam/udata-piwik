# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime

from udata.models import db


__all__ = ('PiwikTracking', )


class PiwikTracking(db.Document):
    url = db.StringField(required=True)
    date = db.DateTimeField(required=True, default=datetime.now)
    kwargs = db.DictField()

    meta = {
        'indexes': ['date'],
        'ordering': ['date'],
    }


class PiwikSyncJobs(db.Document):
    start_date = db.DateTimeField(required=True, default=datetime.now)
    end_date = db.DateTimeField()
