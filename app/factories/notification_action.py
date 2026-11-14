import factory

from app.factories.base import BaseFactory

import app.factories.common as common
import app.models.notification as notification
from app.models import db


class NotificationActionFactory(BaseFactory):
    class Meta:
        model = notification.NotificationAction
        sqlalchemy_session = db.session

    subject = 'event',
    link = common.url_,
    subject_id = 1,
    action_type = 'view'
