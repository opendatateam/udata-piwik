import logging
from datetime import date, time, datetime

from udata_metrics.client import metrics_client_factory


KEYS = 'nb_uniq_visitors nb_hits nb_visits'.split()


log = logging.getLogger(__name__)


def upsert_metric_for_resource(resource, dataset, day, data, latest=False):
    if not dataset:
        log.error('No dataset linked to resource %s', resource.id)
        return
    author_type, author = ('organization', dataset.organization) \
        if dataset.organization else ('user', dataset.owner)
    tags = {
        'author_type': author_type if author else None,
        'author': author.id if author else None,
        'dataset': dataset.id,
        'resource': resource.id,
    }
    if latest:
        tags.update({'latest_url': 'true'})
    upsert_in_metrics_backend(
        day=day,
        metric='resource_views',
        tags=tags,
        data=data,
    )


def upsert_metric_for_community_resource(com_resource, dataset, day, data, latest=False):
    author_type, author = ('organization', com_resource.organization) \
        if com_resource.organization else ('user', com_resource.owner)
    tags = {
        'author_type': author_type if author else None,
        'author': author.id if author else None,
        'dataset': dataset.id if dataset else None,
        'communityresource': com_resource.id,
    }
    if latest:
        tags.update({'latest_url': 'true'})
    upsert_in_metrics_backend(
        day=day,
        metric='community_resource_views',
        tags=tags,
        data=data,
    )


def upsert_metric_for_dataset(dataset, day, data):
    author_type, author = ('organization', dataset.organization) \
        if dataset.organization else ('user', dataset.owner)
    upsert_in_metrics_backend(
        day=day,
        metric='dataset_views',
        tags={
            'author_type': author_type if author else None,
            'author': author.id if author else None,
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
            'author_type': author_type if author else None,
            'author': author.id if author else None,
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
            'user_view': user.id,
        },
        data=data,
    )


def upsert_in_metrics_backend(day=None, metric=None, tags={}, data={}):
    if isinstance(day, str):
        day = date.fromisoformat(day)
    # we're on a daily basis, but backend is not
    dt = datetime.combine(day or date.today(), time())
    client = metrics_client_factory()
    body = {
        'time': dt,
        'measurement': metric,
        'tags': tags,
        'fields': dict((k, data[k]) for k in KEYS)
    }
    client.insert(body)
