import factory

from app.factories.base import BaseFactory

import app.factories.common as common
from app.models.event_topic import db, EventTopic


class EventTopicFactory(BaseFactory):
    class Meta:
        model = EventTopic
        sqlalchemy_session = db.session

    name = common.string_
    slug = common.slug_
    system_image_url = common.imageUrl_
