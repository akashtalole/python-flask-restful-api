import factory

from app.factories.base import BaseFactory

import app.factories.common as common
from app.factories.event import EventFactoryBasic
from app.models.export_job import db, ExportJob


class ExportJobFactory(BaseFactory):
    class Meta:
        model = ExportJob
        sqlalchemy_session = db.session

    task = common.string_
    user_email = common.string_
    event = factory.RelatedFactory(EventFactoryBasic)
