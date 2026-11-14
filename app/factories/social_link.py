import factory

from app.factories.base import BaseFactory

import app.factories.common as common
from app.factories.event import EventFactoryBasic
from app.models.social_link import db, SocialLink


class SocialLinkFactory(BaseFactory):
    class Meta:
        model = SocialLink
        sqlalchemy_session = db.session

    event = factory.RelatedFactory(EventFactoryBasic)
    name = common.string_
    link = common.socialUrl_('facebook')
    identifier = common.string_
    event_id = 1
