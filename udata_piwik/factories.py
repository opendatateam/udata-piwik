import factory

from bson import ObjectId

from udata.factories import ModelFactory
from udata.utils import faker

from udata_piwik.models import PiwikTracking


class PiwikTrackingFactory(ModelFactory):
    class Meta:
        model = PiwikTracking

    url = factory.Faker('uri')

    @factory.lazy_attribute
    def kwargs(self):
        return {
            'uid': ObjectId(),
            'user_ip': faker.ipv4(),
        }
