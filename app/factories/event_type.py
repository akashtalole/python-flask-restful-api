import factory

from app.factories.base import BaseFactory

import app.factories.common as common
from app.models.event_type import db, EventType


class EventTypeFactory(BaseFactory):
    class Meta:
        model = EventType
        sqlalchemy_session = db.session

    name = common.string_
    slug = common.slug_
