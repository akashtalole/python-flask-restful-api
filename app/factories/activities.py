import factory

from app.factories.base import BaseFactory

import app.factories.common as common
from app.models.activity import db, Activity


class ActivityFactory(BaseFactory):

    class Meta:
        model = Activity
        sqlalchemy_session = db.session

    actor = common.string_
    action = common.string_
