import logging
import uuid

from datetime import date, time, datetime

from flask import current_app
from influxdb import InfluxDBClient

from udata.core.metrics.models import Metrics
from udata.core.dataset.models import Dataset, get_resource
from udata.models import Reuse, CommunityResource

KEYS = 'nb_uniq_visitors nb_hits nb_visits'.split()


log = logging.getLogger(__name__)


def get_backend_client():
    dsn = current_app.config['METRICS_DSN']
    return InfluxDBClient(**dsn)


def update_metrics_from_backend():
    update_resources_metrics_from_backend()
    # TODO other objects


def update_resources_metrics_from_backend():
    '''Update resources' metrics from backend'''
    client = get_backend_client()
    query = 'select sum(*) from resource_views group by dataset, resource;'
    result = client.query(query)
    for (_, keys), _values in result.items():
        values = next(_values)
        values.pop('time')
        resource_id = uuid.UUID(resource_id)
        resource = get_resource(resource_id)
        if resource:
            print(dataset_id, resource.id, values)
            resource.metrics.update(values)
            resource.save()
        else:
            log.error(f'Resource not found - id {resource_id}, dataset {dataset_id}')


def aggregate_organization_datasets_daily(org, day):
    keys = ['datasets_{0}'.format(k) for k in KEYS]
    ids = [d.id for d in Dataset.objects(organization=org).only('id')]
    metrics = Metrics.objects(object_id__in=ids,
                              level='daily', date=day.isoformat())
    values = [int(metrics.sum('values.{0}'.format(k))) for k in KEYS]
    return Metrics.objects.update_daily(org, day, **dict(zip(keys, values)))


def aggregate_organization_reuses_daily(org, day):
    keys = ['reuses_{0}'.format(k) for k in KEYS]
    ids = [r.id for r in Reuse.objects(organization=org).only('id')]
    metrics = Metrics.objects(object_id__in=ids,
                              level='daily', date=day.isoformat())
    values = [int(metrics.sum('values.{0}'.format(k))) for k in KEYS]
    Metrics.objects.update_daily(org, day, **dict(zip(keys, values)))


def upsert_metric_for_resource(resource, dataset, day, data):
    author_type, author = ('organization', dataset.organization) \
        if dataset.organization else ('user', dataset.owner)
    upsert_in_metrics_backend(
        day=day,
        metric='resource_views',
        tags={
            'author_type': author_type if author else None,
            'author': author.id if author else None,
            'dataset': dataset.id,
            'resource': resource.id,
        },
        data=data,
    )


def upsert_metric_for_dataset(dataset, day, data):
    author_type, author = ('organization', dataset.organization) \
        if dataset.organization else ('user', dataset.owner)
    upsert_in_metrics_backend(
        day=day,
        metric='dataset_views',
        tags={
            'author_type': author_type,
            'author': author.id,
            'dataset': dataset.id,
        },
        data=data,
    )


def upsert_metric_for_reuse(reuse, day, data):
    author_type, author = ('organization', reuse.organization) \
        if reuse.organization else ('user', reuse.owner)
    upsert_in_metrics_backend(
        day=day,
        metric='reuse_views',
        tags={
            'author_type': author_type,
            'author': author.id,
            'reuse': reuse.id,
        },
        data=data,
    )


def upsert_metric_for_organization(org, day, data):
    upsert_in_metrics_backend(
        day=day,
        metric='organization_views',
        tags={
            'organization': org.id,
        },
        data=data,
    )


def upsert_metric_for_user(user, day, data):
    upsert_in_metrics_backend(
        day=day,
        metric='user_views',
        tags={
            'user': user.id,
        },
        data=data,
    )


def upsert_in_metrics_backend(day=None, metric=None, tags={}, data={}):
    if isinstance(day, str):
        day = date.fromisoformat(day)
    # we're on a daily basis, but backend is not
    dt = datetime.combine(day or date.today(), time())
    client = get_backend_client()
    body = {
        'time': dt,
        'measurement': metric,
        'tags': tags,
        'fields': dict((k, data[k]) for k in KEYS)
    }
    client.write_points([body])
