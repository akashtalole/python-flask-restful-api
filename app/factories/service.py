import factory

from app.factories.base import BaseFactory

import app.factories.common as common
from app.models.service import db, Service


class ServiceFactory(BaseFactory):
    class Meta:
        model = Service
        sqlalchemy_session = db.session

    name = common.string_
